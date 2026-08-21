# ARCHITECTURE — Contemplart

## Stack
- **Backend**: Django + Django REST Framework
- **CMS/Layout**: Wagtail (sobre Django) — permite editar páginas e blocos de layout via painel, sem tocar em código
- **Banco de dados**: PostgreSQL (gerenciado — RDS, Cloud SQL, ou Supabase Postgres)
- **Armazenamento de arquivos digitais**: S3 (ou equivalente) com URLs assinadas e expiração
- **Pagamento**: Stripe (avaliar suporte a produto digital + físico no mesmo checkout)
- **Frontend**: (Django+Wagtail templates)
- **Deploy**: Railway (Postgres addon do próprio Railway — injeta `DATABASE_URL`; `gunicorn` + `whitenoise` para servir estático; ver `Procfile` e `contemplart/settings/prod.py`)


## Estrutura de apps Django (proposta)
```
contemplart/
├── catalog/        # produtos, categorias, variações
├── orders/         # pedidos, itens de pedido, status
├── payments/       # integração com gateway de pagamento
├── digital_delivery/  # geração e controle de links de download
├── shipping/       # cálculo de frete (produtos físicos)
├── cms/            # páginas Wagtail, blocos de layout, banners
├── accounts/       # contas de cliente (Customer, retail/wholesale)
├── crm/            # clientes, leads, histórico de interação
└── finance/        # contas a pagar/receber, dashboard financeiro
```

Nota: `finance` consome dados de `orders` (receita de vendas) e adiciona lançamentos manuais (despesas, receitas de atacado fora do site). Não duplicar: pedido pago em `orders` gera automaticamente uma `AccountReceivable` — não lançar duas vezes.

## Princípios
1. Um único banco de dados — sem sincronização entre sistemas.
2. Produto físico e produto digital são o mesmo model base (`Product`), diferenciados por `product_type`, com regras de checkout diferentes.
3. Nenhuma lógica de negócio duplicada entre painel admin e loja — ambos usam os mesmos models e services.
4. Toda alteração de layout (home, banners, textos) passa pelo Wagtail — não deve existir HTML/texto hardcoded que só o desenvolvedor consiga mudar.

## Fora de escopo da arquitetura v1
- Multi-tenant / múltiplas lojas.
- Cache distribuído (Redis) — só entra se houver problema real de performance.
- Filas assíncronas (Celery) — só entra quando houver processamento pesado (ex: geração de nota fiscal).
