# PRD — Contemplart (Loja Online)

## 1. Visão
A Contemplart é um ateliê de arte sacra que combina moldes de silicone e gesso artesanal com impressão 3D. O site tem dois objetivos:

1. Vender peças físicas (gesso, resina, PLA) e produtos digitais (modelos 3D, conteúdo devocional, etc).
2. Reduzir a dependência de um único cliente atacadista, abrindo canal direto com o consumidor final.

Identidade visual: logo do anjo com turíbulo (Apocalipse 8:3), paleta marsala e marfim.

## 2. Público-alvo
- Consumidor final interessado em arte sacra / devocional.
- Lojistas/varejistas que compram no atacado, párocos, lojas de arigos católicos.
- Makers com impressora 3D? 

## 3. Escopo do produto

### 3.1 Catálogo
- Produtos físicos: peças em gesso, resina e PLA. Variações (tamanho, acabamento, cor).
- Produtos digitais: arquivos para download (ex: modelos 3D em STL, conteúdo devocional em PDF).
- Categorias e coleções (ex: por santo, por técnica, lançamentos, devoção).

### 3.2 Compra
- Carrinho com produtos físicos e digitais misturados.
- Checkout com frete (Correios/transportadora) só quando há item físico.
- Entrega digital automática (download com expiração) após pagamento confirmado.
- Pagamento via Stripe (ver ARCHITECTURE.md).

### 3.3 Gestão de conteúdo / layout
- Administrador (Sérgio) pode editar textos, banners e ordem de seções da home sem depender de código.
- Página institucional contando a história/marca da Contemplart.

### 3.4 Fora de escopo (v1)
- Marketplace multi-vendedor.
- Assinatura recorrente.
- App mobile nativo.

### 3.5 CRM
Cadastro de clientes (varejo e atacado) com histórico de contato/pedidos.
Acompanhamento de leads de atacado (novos lojistas em prospecção).
### 3.6 Financeiro
Contas a pagar e a receber completo (fornecedores, insumos, frete, taxas de gateway).
Dashboard de vendas e receita (visão consolidada, não só lista de lançamentos).

## 4. Métricas de sucesso (definir)
- Nº de vendas diretas (fora do atacado) por mês.
- Taxa de conversão do site.
- Nº de produtos digitais vendidos.

## 5. Decisões (antes abertas)
- Produtos digitais iniciais: modelos 3D (STL) de santos.
- Frete: cálculo manual/fixo no v1 (sem integração automática com Correios/Melhor Envio por enquanto).
- Conta de cliente: sim, desde já — model `Customer` com histórico de pedidos e downloads (não é checkout convidado).
- Atacado: incluído no v1. Cliente tem `customer_type` (varejo/atacado) e recebe preço diferenciado — ver `DATA_MODEL.md` e `RULES.md`.
