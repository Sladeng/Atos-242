# TASKS — Contemplart

Backlog sequencial. Cada sessão do Claude Code deve atacar 1–3 itens marcados `[ ]`, não mais. Ao concluir, marque `[x]` e faça commit.

> Antes de iniciar: confirme que os pontos "em aberto" do PRD.md, DATA_MODEL.md e RULES.md já foram preenchidos.

## Fase 0 — Setup
- [ ] Criar projeto Django (`contemplart/`) com apps vazios: `catalog`, `orders`, `payments`, `digital_delivery`, `shipping`, `cms`, `accounts`
- [ ] Configurar `settings` separados (dev/prod) e variáveis de ambiente (`.env`)
- [ ] Configurar PostgreSQL local (docker-compose ou instância dev)
- [ ] `requirements.txt` inicial (Django, DRF, Wagtail, psycopg2, django-storages)
- [ ] Git init + primeiro commit
- [ ] Confirmar que o projeto sobe local (`runserver`) sem erros

## Fase 1 — Models de catálogo
- [x] Model `Category`
- [x] Model `Product` (com `product_type`, campos físico/digital conforme DATA_MODEL.md) — falta `arquivo_digital`, imagens e `ProductVariant`
- [ ] Model `DigitalAsset`
- [x] Migrations + registrar tudo no `admin.py` pra inspeção manual (Category/Product)
- [ ] Popular alguns produtos de teste via admin (estender `seed_demo` quando `Product`/`Category` existirem)

## Fase 2 — Models de pedido
- [ ] Model `Order`
- [x] Model `OrderItem`
- [ ] Model `DigitalDownloadLink`
- [ ] Migrations + admin
- [ ] Testes unitários: regra "estoque não fica negativo", "digital não tem frete"

- [x] Comando `importar_dados`: importa clientes, produtos e vendas dos CSVs em `contemplart/dados/` (pasta fora do git — dados reais de clientes)

## Fase 2.5 — CRM e Financeiro (MVP)
- [x] Model `Customer` (adicionar campos `name`, `phone`, `notes` — ver DATA_MODEL.md)
- [x] Model `Interaction`
- [x] Model `AccountPayable`
- [x] Model `AccountReceivable` (exigiu criar `orders.Order` mínimo antes — ver nota em DATA_MODEL.md)
- [x] Migrations + admin para os models acima
- [x] Signal/hook: `Order.status → paid` cria `AccountReceivable` automaticamente
- [ ] Tela/endpoint de dashboard: total a receber, total a pagar, receita do mês, contas vencidas
- [ ] Testes: pagamento de pedido não duplica `AccountReceivable`; conta vencida aparece como `overdue`

> Pendente de validar com Postgres real (Docker não instalado na máquina de dev usada até agora) — `manage.py migrate` ainda não foi confirmado de ponta a ponta.

## Fase 3 — API (DRF)
- [ ] Serializers de `Product` e `Category`
- [ ] Endpoints de listagem/detalhe de produto (público)
- [ ] Endpoint de criação de pedido (carrinho → order)
- [ ] Testes de API para os endpoints acima

## Fase 4 — Wagtail / Layout
- [x] Instalar e configurar Wagtail no projeto
- [x] Painel de gestão em `/painel/` (produtos, clientes, pedidos com itens, financeiro, resumo na home, perfil Operador)
- [ ] Criar página institucional (história da marca) editável via painel
- [ ] Criar blocos de conteúdo para a home (banners, seções, ordem)
- [ ] Validar: editar layout no painel sem precisar de deploy

## Fase 4.5 — Loja (próxima etapa)
- [ ] Páginas públicas: catálogo e página de produto
- [ ] Cadastro/login de cliente (cria `Customer` com `usuario`)
- [ ] Carrinho e envio de pedido (entra como `pending`, sem pagamento online — ver RULES.md)
- [x] Armazenamento de uploads: volume do Railway em `MEDIA_ROOT`, `/media/` servido pelo Django (ver ARCHITECTURE.md)
- [ ] Criar o volume no serviço do Railway (mount path `/data`)
- [ ] Imagens de produto (`ProductImage`)

## Fase 5 — Frete (produtos físicos)
- [ ] Definir integração (Melhor Envio / Correios / manual)
- [ ] Cálculo de frete só sobre itens físicos do carrinho
- [ ] Testes: pedido só digital → frete zero

## Fase 6 — Pagamento
- [ ] Integração Stripe (checkout)
- [ ] Webhook de confirmação de pagamento (`Order.status → paid`)
- [ ] Testes: pedido só muda pra `paid` via webhook, nunca no clique do botão

## Fase 7 — Entrega digital
- [ ] Geração de `DigitalDownloadLink` (URL assinada S3) após `paid`
- [ ] Expiração por dias + limite de downloads
- [ ] Testes: link expirado bloqueia acesso; limite de downloads respeitado

## Fase 8 — Polimento / lançamento
- [ ] Emails transacionais (confirmação de pedido, link de download) — hoje `MAILERS` usa o backend de console (dev-only), precisa de um provedor real antes do deploy
- [ ] Revisão de todas as regras do RULES.md contra o comportamento real
- [x] Config de deploy Railway pronta (`Procfile`, `railpack.json`, `settings/prod.py`, `whitenoise`, `dj-database-url`) — falta só rodar o primeiro deploy de verdade e confirmar Python 3.13 builda ok no Railpack
- [x] Comando `seed_demo` (`contemplart/accounts/management/commands/`) com dados de demonstração de clientes, interações, pedidos e financeiro
- [ ] Deploy em ambiente de produção
- [ ] Teste de compra ponta a ponta (físico + digital no mesmo pedido)
