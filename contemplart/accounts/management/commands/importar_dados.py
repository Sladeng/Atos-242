import csv
import uuid
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_duration
from django.utils.text import slugify

from contemplart.accounts.models import Customer
from contemplart.catalog.models import Product
from contemplart.finance.models import AccountReceivable
from contemplart.orders.models import Order, OrderItem

# IDs derivados do conteúdo do CSV: rodar o comando de novo atualiza os
# mesmos registros em vez de duplicar.
NAMESPACE = uuid.UUID('0b7d1e44-8f3a-4c62-9d15-5a7e2c9f1b30')

DIR_PADRAO = Path(settings.BASE_DIR) / 'contemplart' / 'dados'

# Marcadores usados na planilha para "sem valor".
VAZIOS = {'', '(vazio)', 'confirmar'}

# Preço de varejo provisório usado na planilha enquanto o real não é definido.
PRECO_PROVISORIO = Decimal('999')

STATUS_PGTO = {
    'pg': Order.PAID,
    '': Order.PENDING,
    '(vazio)': Order.PENDING,
}


def import_id(chave):
    return uuid.uuid5(NAMESPACE, chave)


def texto(valor):
    valor = (valor or '').strip()
    return '' if valor.lower() in VAZIOS else valor


def decimal_ou_none(valor):
    valor = texto(valor)
    if not valor:
        return None
    try:
        return Decimal(valor.replace(',', '.'))
    except InvalidOperation:
        return None


def inteiro_ou_none(valor):
    numero = decimal_ou_none(valor)
    return int(numero) if numero is not None and numero == int(numero) else None


def data_ou_none(valor):
    """Datas inválidas (ex.: 'CONFIRMAR', 'Mães', '(vazio)') viram None."""
    valor = texto(valor)
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor).date()
    except ValueError:
        return None


def duracao_ou_none(valor):
    """Número puro = minutos; senão aceita 'HH:MM:SS' / formato do Django."""
    valor = texto(valor)
    if not valor:
        return None
    minutos = decimal_ou_none(valor)
    if minutos is not None:
        return timedelta(minutes=float(minutos))
    return parse_duration(valor)


def chave_nome(nome):
    return ' '.join(nome.split()).casefold()


class Command(BaseCommand):
    help = (
        'Importa clientes, produtos e vendas dos CSVs (clientes.csv, produtos.csv, vendas.csv). '
        'Idempotente: rodar de novo atualiza os registros em vez de duplicar.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir', type=Path, default=DIR_PADRAO,
            help=f'Pasta com os CSVs (padrão: {DIR_PADRAO}).',
        )

    def handle(self, *args, **options):
        pasta = options['dir']
        arquivos = {nome: pasta / f'{nome}.csv' for nome in ('clientes', 'produtos', 'vendas')}
        faltando = [str(p) for p in arquivos.values() if not p.exists()]
        if faltando:
            raise CommandError(f'Arquivo(s) não encontrado(s): {", ".join(faltando)}')

        self.avisos = []
        with transaction.atomic():
            clientes = self.importar_clientes(self.ler(arquivos['clientes']))
            produtos = self.importar_produtos(self.ler(arquivos['produtos']))
            vendas = self.importar_vendas(self.ler(arquivos['vendas']), clientes, produtos)

        for aviso in self.avisos:
            self.stdout.write(self.style.WARNING(aviso))
        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {len(clientes)} clientes, {len(produtos)} produtos, {vendas} vendas.'
        ))

    def ler(self, caminho):
        # utf-8-sig remove o BOM que o Excel coloca no início do arquivo.
        with open(caminho, encoding='utf-8-sig', newline='') as f:
            return [
                (numero, {k.strip(): v for k, v in linha.items() if k})
                for numero, linha in enumerate(csv.DictReader(f), start=2)
            ]

    def importar_clientes(self, linhas):
        User = get_user_model()
        clientes = {}
        for numero, linha in linhas:
            nome = texto(linha.get('NOME'))
            if not nome:
                self.avisos.append(f'clientes.csv linha {numero}: sem NOME, ignorada.')
                continue
            id_cliente = inteiro_ou_none(linha.get('ID_CLIENTE'))
            chave = f'cliente:{id_cliente}' if id_cliente is not None else f'cliente:{chave_nome(nome)}'

            username = f'importado_{id_cliente}' if id_cliente is not None else f'importado_{slugify(nome)}'
            usuario, criado = User.objects.get_or_create(username=username[:150])
            if criado:
                usuario.set_unusable_password()
                usuario.save()

            cliente, _ = Customer.objects.update_or_create(
                id=import_id(chave),
                defaults={
                    'usuario': usuario,
                    'nome': nome,
                    'telefone': texto(linha.get('CONTATO')),
                    'endereco': texto(linha.get('ENDEREÇO')),
                    'cpf_cnpj': texto(linha.get('CPF_CNPJ')),
                    'pessoa_contato': texto(linha.get('PESSOA_CONTATO')),
                    # Clientes da planilha compram a preço de atacado.
                    'tipo_cliente': Customer.WHOLESALE,
                },
            )
            data_cadastro = data_ou_none(linha.get('DATA_CADASTRO'))
            if data_cadastro:
                # criado_em é auto_now_add; usa a data real de cadastro quando válida.
                Customer.objects.filter(pk=cliente.pk).update(
                    criado_em=timezone.make_aware(datetime.combine(data_cadastro, datetime.min.time()))
                )
            clientes[chave_nome(nome)] = cliente
        return clientes

    def importar_produtos(self, linhas):
        produtos = {}
        for numero, linha in linhas:
            nome = texto(linha.get('NOME'))
            if not nome:
                self.avisos.append(f'produtos.csv linha {numero}: sem NOME, ignorada.')
                continue
            id_produto = inteiro_ou_none(linha.get('ID_PRODUTO'))
            chave = f'produto:{id_produto}' if id_produto is not None else f'produto:{chave_nome(nome)}'

            preco_atacado = decimal_ou_none(linha.get('VALOR_ATACADO'))
            preco = decimal_ou_none(linha.get('VALOR_VAREJO'))
            if preco is None or preco == PRECO_PROVISORIO:
                preco = preco_atacado
            if preco is None:
                self.avisos.append(f'produtos.csv linha {numero} ({nome}): sem preço de varejo nem atacado, ignorada.')
                continue

            produto, _ = Product.objects.update_or_create(
                id=import_id(chave),
                defaults={
                    'nome': nome,
                    'slug': self.slug_unico(nome, import_id(chave)),
                    'tipo_produto': Product.PHYSICAL,
                    'preco': preco,
                    'preco_atacado': preco_atacado,
                    'custo': decimal_ou_none(linha.get('CUSTO')),
                    'peso_g': decimal_ou_none(linha.get('PESO (g)')),
                    'tempo_impressao': duracao_ou_none(linha.get('TEMPO_IMPRESSAO')),
                },
            )
            produtos[chave_nome(nome)] = produto
        return produtos

    def slug_unico(self, nome, produto_id):
        base = slugify(nome)[:240] or 'produto'
        slug, n = base, 2
        while Product.objects.filter(slug=slug).exclude(id=produto_id).exists():
            slug, n = f'{base}-{n}', n + 1
        return slug

    def importar_vendas(self, linhas, clientes, produtos):
        # A planilha não tem ID_VENDA preenchido; a chave da venda é o
        # conteúdo que a identifica (sem TOTAL/STATUS, que podem ser
        # corrigidos depois) + nº de ocorrência para linhas idênticas.
        ocorrencias = Counter()
        importadas = 0
        for numero, linha in linhas:
            cliente = clientes.get(chave_nome(texto(linha.get('CLIENTE'))))
            produto = produtos.get(chave_nome(texto(linha.get('PRODUTO'))))
            quantidade = inteiro_ou_none(linha.get('QUANTIDADE'))
            preco_unitario = decimal_ou_none(linha.get('VALOR_VENDA'))

            problemas = []
            if cliente is None:
                problemas.append(f'cliente "{linha.get("CLIENTE")}" não encontrado')
            if produto is None:
                problemas.append(f'produto "{linha.get("PRODUTO")}" não encontrado')
            if quantidade is None:
                problemas.append('QUANTIDADE inválida')
            if preco_unitario is None:
                problemas.append('VALOR_VENDA inválido')
            if problemas:
                self.avisos.append(f'vendas.csv linha {numero}: {"; ".join(problemas)}, ignorada.')
                continue

            status_bruto = (linha.get('STATUS_PGTO') or '').strip().lower()
            status = STATUS_PGTO.get(status_bruto)
            if status is None:
                self.avisos.append(
                    f'vendas.csv linha {numero}: STATUS_PGTO "{linha.get("STATUS_PGTO")}" desconhecido, '
                    'importada como pendente.'
                )
                status = Order.PENDING

            id_venda = texto(linha.get('ID_VENDA'))
            if id_venda:
                chave = f'venda:{id_venda}'
            else:
                base = '|'.join([
                    str(cliente.id), str(produto.id), texto(linha.get('DATA_VENDA')),
                    str(quantidade), str(preco_unitario),
                ])
                ocorrencias[base] += 1
                chave = f'venda:{base}#{ocorrencias[base]}'

            total = decimal_ou_none(linha.get('TOTAL'))
            if total is None:
                total = (preco_unitario * quantidade).quantize(Decimal('0.01'))
            data_venda = data_ou_none(linha.get('DATA_VENDA'))

            pedido, _ = Order.objects.update_or_create(
                id=import_id(chave),
                defaults={
                    'cliente': cliente,
                    'email_cliente': cliente.email,
                    'status': status,
                    'valor_frete': Decimal('0'),
                    'total': total,
                    'data_venda': data_venda,
                },
            )
            OrderItem.objects.update_or_create(
                id=import_id(f'{chave}:item'),
                defaults={
                    'pedido': pedido,
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                },
            )

            # Espelha a regra "pedido pago gera AccountReceivable" (o signal
            # ainda não existe). Chave por pedido = no máximo uma por pedido.
            if status == Order.PAID:
                pago_em = data_ou_none(linha.get('PGTO_EM'))
                AccountReceivable.objects.update_or_create(
                    pedido=pedido,
                    defaults={
                        'descricao': f'Venda - {cliente.nome} - {quantidade}x {produto.nome}',
                        'valor': total,
                        'data_vencimento': pago_em or data_venda or date.today(),
                        'status': AccountReceivable.RECEIVED,
                        'recebido_em': (
                            timezone.make_aware(datetime.combine(pago_em, datetime.min.time()))
                            if pago_em else None
                        ),
                    },
                )
            importadas += 1
        return importadas
