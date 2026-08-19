# RULES — Regras de negócio (Contemplart)

Regras que não são óbvias a partir do código e devem ser respeitadas em qualquer implementação.

## Produtos
- Produto digital nunca tem frete calculado, mesmo se estiver no mesmo carrinho de um produto físico.
- Produto físico com `stock_quantity == 0` não pode ser comprado (exceto se decidirmos permitir "sob encomenda" — a definir).
- Estoque físico nunca fica negativo.

## Checkout / Pedido
- Um pedido pode misturar itens físicos e digitais.
- Frete só é calculado sobre o subtotal dos itens físicos.
- Pedido só muda para `paid` após confirmação real do gateway de pagamento (webhook), nunca no clique de "finalizar compra".

## Entrega digital
- Link de download só é gerado após `Order.status == 'paid'`.
- Link expira em N dias (default 7) a partir da geração.
- Link tem limite de downloads (default 5); após o limite, bloqueado.
- Nunca expor a URL real do arquivo no S3 — sempre via URL assinada temporária.

## Layout / Conteúdo
- Qualquer texto, banner ou ordem de seção editável pelo Wagtail — não deve haver conteúdo de marketing hardcoded no template que exija deploy para mudar.
- Alterações de layout não devem exigir migração de banco (usar campos de conteúdo genéricos do Wagtail, não models rígidos).

## Contas de cliente
- Checkout exige conta (`Customer`) — não há checkout como convidado no v1.
- `Customer.customer_type` define `retail` ou `wholesale`; controla o preço aplicado no carrinho (ver DATA_MODEL.md).

## Atacado (canal incluído no v1)
- Cliente `wholesale` recebe `product.wholesale_price` quando preenchido; se `wholesale_price` for null, usa `product.price` normalmente (sem desconto automático).
- Aprovar/definir `customer_type == 'wholesale'` é uma ação administrativa (admin define manualmente quem é atacadista) — não há auto-cadastro como atacadista no v1.
- Regras de frete e entrega digital valem igualmente para clientes `retail` e `wholesale` (não há tratamento especial de frete por tipo de cliente no v1).

## Frete
- Cálculo de frete no v1 é manual/fixo (sem integração automática com Correios/Melhor Envio) — ver ARCHITECTURE.md/PRD.md.

## CRM
- Todo cliente de atacado (`customer_type == wholesale`) deve ter ao menos um registro de `Interaction` antes de virar `Order` — histórico mínimo de negociação.

## Financeiro
- Toda venda paga no site gera `AccountReceivable` automaticamente — nunca lançar manualmente uma receita que já existe como `Order` pago (evitar duplicidade).
- `AccountPayable` com `due_date` no passado e `status == pending` deve aparecer como `overdue` no dashboard (calculado, não é preciso job assíncrono no MVP).
- Dashboard financeiro é somente leitura — nenhuma tela de dashboard deve permitir editar valores diretamente; edição sempre pelas telas de Conta a Pagar/Receber.
