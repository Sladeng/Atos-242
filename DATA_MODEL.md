# DATA_MODEL — Contemplart

> Rascunho de schema. Cada model aqui deve virar um `models.py` real antes do Claude Code escrever qualquer código de catálogo/pedido.

> Convenção (definida durante a implementação do CRM/Financeiro): nomes de **campo** são em português (`nome`, `preco`, `criado_em`...). Nomes de **model**/tabela continuam em inglês (`Product`, `Order`...). Valores internos de `enum`/`choices` (os que vão pro banco, ex.: `'wholesale'`, `'paid'`) continuam em inglês — só o rótulo exibido (`get_..._display()`) é em português. Ver `CLAUDE.md` → Convenções de código.

## Product
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| nome | string | |
| slug | string | único; gerado a partir do `nome` quando vazio |
| descricao | text | |
| tipo_produto | enum | `physical` \| `digital` |
| preco | decimal | |
| categoria | FK Category | nullable — produtos importados da planilha ainda não têm categoria |
| material | enum | `gesso` \| `resina` \| `pla` \| null (digital) |
| quantidade_estoque | int | null se digital |
| arquivo_digital | FK DigitalAsset | null se físico — **ainda não implementado** (DigitalAsset pendente) |
| imagens | M2M/related ProductImage | **ainda não implementado** |
| ativo | bool | |
| preco_atacado | decimal | null = sem preço de atacado específico; se preenchido, usado quando `cliente.tipo_cliente == 'wholesale'` |
| custo | decimal | nullable — custo de produção (veio da planilha de produtos) |
| peso_g | decimal | nullable — peso em gramas |
| tempo_impressao | duration | nullable — tempo de impressão 3D |

## ProductVariant
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| produto | FK Product | |
| tamanho | string | null se não aplicável |
| cor | string | null se não aplicável |
| acabamento | string | null se não aplicável |
| quantidade_estoque | int | estoque por variação (substitui `Product.quantidade_estoque` quando produto tem variações) |
| preco_personalizado | decimal | null = usa `product.preco` (ou `preco_atacado`) |

## Customer
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| usuario | FK auth.User (1:1) | autenticação; **nullable** — cliente cadastrado pela equipe no painel não tem login (quem se cadastra na loja tem) |
| nome | string | adicionado no addendum CRM/Financeiro |
| email | string | opcional (blank) |
| telefone | string | adicionado no addendum CRM/Financeiro |
| endereco | text | blank — adicionado na importação da planilha de clientes |
| cpf_cnpj | string | blank — adicionado na importação da planilha de clientes |
| pessoa_contato | string | blank — nome do contato (ex.: pároco, comprador); adicionado na importação |
| tipo_cliente | enum | `retail` \| `wholesale` |
| observacoes | text | adicionado no addendum CRM/Financeiro |
| criado_em | datetime | |

## Interaction
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| cliente | FK Customer | |
| tipo | enum | `call`, `email`, `whatsapp`, `meeting` |
| observacoes | text | |
| data | datetime | |
| data_retorno | datetime | nullable |

## AccountPayable (Conta a Pagar)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| descricao | string | ex: "fornecedor resina" |
| categoria | enum | `insumo`, `frete`, `taxa_gateway`, `outro` |
| valor | decimal | |
| data_vencimento | date | |
| status | enum | `pending`, `paid`, `overdue` |
| pago_em | datetime | nullable |

## AccountReceivable (Conta a Receber)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| pedido | FK Order | nullable — pode ser receita de atacado fora do site |
| descricao | string | |
| valor | decimal | |
| data_vencimento | date | |
| status | enum | `pending`, `received`, `overdue` |
| recebido_em | datetime | nullable |

## Category
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| nome | string |
| slug | string |

## DigitalAsset
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| arquivo | FileField (S3) | |
| limite_downloads | int | ex: 5 |
| dias_para_expirar | int | ex: 7 a partir da compra |

## Order
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| cliente | FK Customer | |
| email_cliente | string | opcional; preenchido com o e-mail do cliente ao salvar pelo painel |
| status | enum: `pending`, `paid`, `shipped`, `completed`, `cancelled` | |
| endereco_entrega | FK Address (null se só digital) | **Pendente**: model `Address` nunca foi definido aqui. Implementado por ora como `TextField` livre (`contemplart/orders/models.py`) — ajustar quando o model `Address` for desenhado (Fase 2 completa) |
| valor_frete | decimal (0 se só digital) | |
| total | decimal | calculado = soma dos itens (`quantidade × preco_unitario`) + `valor_frete` (`orders/services.py`); pedido sem itens mantém o valor gravado |
| data_venda | date | nullable — data real da venda (vendas importadas da planilha podem não ter); `criado_em` é a data do registro no sistema |
| criado_em | datetime | |

> Nota: `Order` e `OrderItem` estão implementados (este último criado para a importação de vendas da planilha — cada linha de `vendas.csv` vira um `Order` com um `OrderItem`, porque o status de pagamento varia por linha). Checkout, pagamento e entrega digital (Fase 2 completa do TASKS.md) ainda não existem.

## OrderItem
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| pedido | FK Order |
| produto | FK Product |
| quantidade | int |
| preco_unitario | decimal (vazio no formulário = preço efetivo do produto para o cliente, ver Regras derivadas) |

## DigitalDownloadLink
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| item_pedido | FK OrderItem |
| url_assinada | string |
| downloads_utilizados | int |
| expira_em | datetime |

## Regras derivadas do schema
- Se `product.tipo_produto == 'digital'` → `quantidade_estoque` não se aplica; `valor_frete` do pedido não considera esse item.
- `DigitalDownloadLink` só é criado após `Order.status == 'paid'`.
- Se `product` tem `ProductVariant`(s), o estoque e preço efetivo vêm da variação escolhida, não do `Product` diretamente.
- Preço efetivo de um item = `variant.preco_personalizado` (se houver) → senão `product.preco_atacado` (se `cliente.tipo_cliente == 'wholesale'` e preenchido) → senão `product.preco`.
- Quando `Order.status` muda para `paid` (ou já está em `shipped`/`completed`), criar automaticamente uma `AccountReceivable` vinculada (status `received`, `recebido_em` = data do pagamento). Vendas de atacado fora do site entram como `AccountReceivable` manual, sem `pedido` vinculado.
