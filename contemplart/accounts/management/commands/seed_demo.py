import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from contemplart.accounts.models import Customer
from contemplart.crm.models import Interaction
from contemplart.finance.models import AccountPayable, AccountReceivable
from contemplart.orders.models import Order

# IDs derivados de uma chave fixa: rodar o comando de novo atualiza os
# mesmos registros em vez de duplicar.
NAMESPACE = uuid.UUID('6f1c2b8e-3d4a-4e5f-9a7b-1c2d3e4f5a6b')


def demo_id(chave):
    return uuid.uuid5(NAMESPACE, chave)


CUSTOMERS = [
    # (username, nome, email, telefone, tipo_cliente)
    ('demo_maria', 'Maria Aparecida Souza', 'maria.demo@example.com', '(11) 98888-0001', Customer.RETAIL),
    ('demo_joao', 'João Batista Lima', 'joao.demo@example.com', '(21) 97777-0002', Customer.RETAIL),
    ('demo_ana', 'Ana Clara Ferreira', 'ana.demo@example.com', '(31) 96666-0003', Customer.RETAIL),
    ('demo_loja_sagrado', 'Loja Sagrado Coração', 'compras.sagrado@example.com', '(11) 3333-1000', Customer.WHOLESALE),
    ('demo_paroquia_sf', 'Paróquia São Francisco', 'secretaria.psf@example.com', '(19) 3222-2000', Customer.WHOLESALE),
]

INTERACTIONS = [
    # (chave, username, tipo, dias_atras, observacoes, retorno_em_dias)
    ('int-1', 'demo_loja_sagrado', Interaction.WHATSAPP, 40, 'Primeiro contato: interesse em imagens de gesso 30cm.', None),
    ('int-2', 'demo_loja_sagrado', Interaction.MEETING, 25, 'Apresentação do catálogo e tabela de atacado.', -5),
    ('int-3', 'demo_paroquia_sf', Interaction.CALL, 20, 'Pedido de orçamento para presépio de Natal.', 3),
    ('int-4', 'demo_maria', Interaction.EMAIL, 10, 'Dúvida sobre prazo de entrega.', None),
]

ORDERS = [
    # (chave, username, status, dias_atras, total, frete, endereco)
    ('ped-1', 'demo_maria', Order.PAID, 50, '189.90', '25.00', 'Rua das Flores, 100 - São Paulo/SP'),
    ('ped-2', 'demo_joao', Order.COMPLETED, 35, '79.90', '0.00', None),
    ('ped-3', 'demo_ana', Order.SHIPPED, 12, '249.80', '30.00', 'Av. Afonso Pena, 500 - Belo Horizonte/MG'),
    ('ped-4', 'demo_loja_sagrado', Order.PAID, 8, '1250.00', '80.00', 'Rua XV de Novembro, 20 - São Paulo/SP'),
    ('ped-5', 'demo_maria', Order.PENDING, 1, '59.90', '0.00', None),
    ('ped-6', 'demo_joao', Order.CANCELLED, 15, '120.00', '20.00', 'Rua do Catete, 10 - Rio de Janeiro/RJ'),
]

PAYABLES = [
    # (chave, descricao, categoria, valor, vencimento_em_dias, pago)
    ('cp-1', 'Fornecedor de resina (lote setembro)', AccountPayable.INSUMO, '640.00', -30, True),
    ('cp-2', 'Gesso cerâmico 20kg', AccountPayable.INSUMO, '180.00', -5, False),  # vencida
    ('cp-3', 'Filamento PLA marfim', AccountPayable.INSUMO, '210.00', 10, False),
    ('cp-4', 'Frete transportadora (atacado)', AccountPayable.FRETE, '95.00', -2, False),  # vencida
    ('cp-5', 'Taxas Stripe do mês', AccountPayable.TAXA_GATEWAY, '42.30', 15, False),
    ('cp-6', 'Embalagens e plástico bolha', AccountPayable.OUTRO, '75.00', -20, True),
]

MANUAL_RECEIVABLES = [
    # Vendas de atacado fora do site (sem pedido vinculado).
    # (chave, descricao, valor, vencimento_em_dias, recebido)
    ('cr-1', 'Atacado fora do site - Paróquia São Francisco (presépio)', '890.00', 7, False),
    ('cr-2', 'Atacado fora do site - feira de artigos religiosos', '430.00', -12, True),
    ('cr-3', 'Atacado fora do site - Loja Sagrado Coração (boleto)', '600.00', -3, False),  # vencida
]


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração (clientes, interações, pedidos e financeiro). Idempotente.'

    @transaction.atomic
    def handle(self, *args, **options):
        agora = timezone.now()
        hoje = timezone.localdate()

        clientes = {}
        User = get_user_model()
        for username, nome, email, telefone, tipo in CUSTOMERS:
            usuario, criado = User.objects.get_or_create(username=username, defaults={'email': email})
            if criado:
                usuario.set_unusable_password()
                usuario.save()
            clientes[username], _ = Customer.objects.update_or_create(
                usuario=usuario,
                defaults={'nome': nome, 'email': email, 'telefone': telefone, 'tipo_cliente': tipo},
            )

        for chave, username, tipo, dias_atras, observacoes, retorno in INTERACTIONS:
            data = agora - timedelta(days=dias_atras)
            Interaction.objects.update_or_create(
                id=demo_id(chave),
                defaults={
                    'cliente': clientes[username],
                    'tipo': tipo,
                    'observacoes': observacoes,
                    'data': data,
                    'data_retorno': agora + timedelta(days=retorno) if retorno is not None else None,
                },
            )

        for chave, username, status, dias_atras, total, frete, endereco in ORDERS:
            cliente = clientes[username]
            pedido, _ = Order.objects.update_or_create(
                id=demo_id(chave),
                defaults={
                    'cliente': cliente,
                    'email_cliente': cliente.email,
                    'status': status,
                    'endereco_entrega': endereco,
                    'valor_frete': Decimal(frete),
                    'total': Decimal(total),
                },
            )
            # criado_em é auto_now_add; espalha os pedidos no tempo para o dashboard.
            criado_em = agora - timedelta(days=dias_atras)
            Order.objects.filter(pk=pedido.pk).update(criado_em=criado_em)

            # Espelha a regra "pedido pago gera AccountReceivable" (o signal
            # ainda não existe). Chave por pedido = no máximo uma por pedido.
            if status in (Order.PAID, Order.SHIPPED, Order.COMPLETED):
                AccountReceivable.objects.update_or_create(
                    pedido=pedido,
                    defaults={
                        'descricao': f'Venda no site - {cliente.nome}',
                        'valor': pedido.total,
                        'data_vencimento': criado_em.date(),
                        'status': AccountReceivable.RECEIVED,
                        'recebido_em': criado_em,
                    },
                )

        for chave, descricao, categoria, valor, vencimento, pago in PAYABLES:
            data_vencimento = hoje + timedelta(days=vencimento)
            # Vencidas ficam como `pending` com data no passado: `overdue` é
            # calculado no dashboard (RULES.md), não gravado.
            AccountPayable.objects.update_or_create(
                id=demo_id(chave),
                defaults={
                    'descricao': descricao,
                    'categoria': categoria,
                    'valor': Decimal(valor),
                    'data_vencimento': data_vencimento,
                    'status': AccountPayable.PAID if pago else AccountPayable.PENDING,
                    'pago_em': agora + timedelta(days=vencimento) if pago else None,
                },
            )

        for chave, descricao, valor, vencimento, recebido in MANUAL_RECEIVABLES:
            AccountReceivable.objects.update_or_create(
                id=demo_id(chave),
                defaults={
                    'pedido': None,
                    'descricao': descricao,
                    'valor': Decimal(valor),
                    'data_vencimento': hoje + timedelta(days=vencimento),
                    'status': AccountReceivable.RECEIVED if recebido else AccountReceivable.PENDING,
                    'recebido_em': agora + timedelta(days=vencimento) if recebido else None,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Dados de demonstração prontos: {len(CUSTOMERS)} clientes, {len(INTERACTIONS)} interações, '
            f'{len(ORDERS)} pedidos, {len(PAYABLES)} contas a pagar, '
            f'{AccountReceivable.objects.count()} contas a receber.'
        ))
