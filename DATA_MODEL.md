# DATA_MODEL — Contemplart

> Rascunho de schema. Cada model aqui deve virar um `models.py` real antes do Claude Code escrever qualquer código de catálogo/pedido.

## Product
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| name | string | |
| slug | string | único |
| description | text | |
| product_type | enum | `physical` \| `digital` |
| price | decimal | |
| category | FK Category | |
| material | enum | `gesso` \| `resina` \| `pla` \| null (digital) |
| stock_quantity | int | null se digital |
| digital_file | FK DigitalAsset | null se físico |
| images | M2M/related ProductImage | |
| active | bool | |
| wholesale_price | decimal | null = sem preço de atacado específico; se preenchido, usado quando `customer.customer_type == 'wholesale'` |

## ProductVariant
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| product | FK Product | |
| size | string | null se não aplicável |
| color | string | null se não aplicável |
| finish | string | acabamento; null se não aplicável |
| stock_quantity | int | estoque por variação (substitui `Product.stock_quantity` quando produto tem variações) |
| price_override | decimal | null = usa `product.price` (ou `wholesale_price`) |

## Customer
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| user | FK auth.User (1:1) | autenticação |
| name | string | adicionado no addendum CRM/Financeiro |
| email | string | |
| phone | string | adicionado no addendum CRM/Financeiro |
| customer_type | enum | `retail` \| `wholesale` |
| notes | text | adicionado no addendum CRM/Financeiro |
| created_at | datetime | |

## Interaction
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| customer | FK Customer | |
| type | enum | `call`, `email`, `whatsapp`, `meeting` |
| notes | text | |
| date | datetime | |
| follow_up_date | datetime | nullable |

## AccountPayable (Conta a Pagar)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| description | string | ex: "fornecedor resina" |
| category | enum | `insumo`, `frete`, `taxa_gateway`, `outro` |
| amount | decimal | |
| due_date | date | |
| status | enum | `pending`, `paid`, `overdue` |
| paid_at | datetime | nullable |

## AccountReceivable (Conta a Receber)
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| order | FK Order | nullable — pode ser receita de atacado fora do site |
| description | string | |
| amount | decimal | |
| due_date | date | |
| status | enum | `pending`, `received`, `overdue` |
| received_at | datetime | nullable |

## Category
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| name | string |
| slug | string |

## DigitalAsset
| Campo | Tipo | Notas |
|---|---|---|
| id | UUID/PK | |
| file | FileField (S3) | |
| max_downloads | int | ex: 5 |
| expires_after_days | int | ex: 7 a partir da compra |

## Order
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| customer | FK Customer |
| customer_email | string |
| status | enum: `pending`, `paid`, `shipped`, `completed`, `cancelled` |
| shipping_address | FK Address (null se só digital) |
| shipping_cost | decimal (0 se só digital) |
| total | decimal |
| created_at | datetime |

## OrderItem
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| order | FK Order |
| product | FK Product |
| quantity | int |
| unit_price | decimal |

## DigitalDownloadLink
| Campo | Tipo |
|---|---|
| id | UUID/PK |
| order_item | FK OrderItem |
| signed_url | string |
| downloads_used | int |
| expires_at | datetime |

## Regras derivadas do schema
- Se `product.product_type == 'digital'` → `stock_quantity` não se aplica; `shipping_cost` do pedido não considera esse item.
- `DigitalDownloadLink` só é criado após `Order.status == 'paid'`.
- Se `product` tem `ProductVariant`(s), o estoque e preço efetivo vêm da variação escolhida, não do `Product` diretamente.
- Preço efetivo de um item = `variant.price_override` (se houver) → senão `product.wholesale_price` (se `customer.customer_type == 'wholesale'` e preenchido) → senão `product.price`.
- Quando `Order.status` muda para `paid`, criar automaticamente uma `AccountReceivable` vinculada (status `received`, `received_at` = data do pagamento). Vendas de atacado fora do site entram como `AccountReceivable` manual, sem `order` vinculado.
