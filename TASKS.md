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
- [ ] Model `Category`
- [ ] Model `Product` (com `product_type`, campos físico/digital conforme DATA_MODEL.md)
- [ ] Model `DigitalAsset`
- [ ] Migrations + registrar tudo no `admin.py` pra inspeção manual
- [ ] Popular alguns produtos de teste via admin

## Fase 2 — Models de pedido
- [ ] Model `Order`
- [ ] Model `OrderItem`
- [ ] Model `DigitalDownloadLink`
- [ ] Migrations + admin
- [ ] Testes unitários: regra "estoque não fica negativo", "digital não tem frete"

## Fase 2.5 — CRM e Financeiro (MVP)
- [ ] Model `Customer` (adicionar campos `name`, `phone`, `notes` — ver DATA_MODEL.md)
- [ ] Model `Interaction`
- [ ] Model `AccountPayable`
- [ ] Model `AccountReceivable`
- [ ] Migrations + admin para os models acima
- [ ] Signal/hook: `Order.status → paid` cria `AccountReceivable` automaticamente
- [ ] Tela/endpoint de dashboard: total a receber, total a pagar, receita do mês, contas vencidas
- [ ] Testes: pagamento de pedido não duplica `AccountReceivable`; conta vencida aparece como `overdue`

## Fase 3 — API (DRF)
- [ ] Serializers de `Product` e `Category`
- [ ] Endpoints de listagem/detalhe de produto (público)
- [ ] Endpoint de criação de pedido (carrinho → order)
- [ ] Testes de API para os endpoints acima

## Fase 4 — Wagtail / Layout
- [ ] Instalar e configurar Wagtail no projeto
- [ ] Criar página institucional (história da marca) editável via painel
- [ ] Criar blocos de conteúdo para a home (banners, seções, ordem)
- [ ] Validar: editar layout no painel sem precisar de deploy

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
- [ ] Emails transacionais (confirmação de pedido, link de download)
- [ ] Revisão de todas as regras do RULES.md contra o comportamento real
- [ ] Deploy em ambiente de produção
- [ ] Teste de compra ponta a ponta (físico + digital no mesmo pedido)
