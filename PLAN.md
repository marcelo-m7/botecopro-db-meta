A ideia é: ter **um único YAML** descrevendo o domínio do BotecoPro e, a partir dele, gerar:

* modelos Dart (Flutter),
* modelos Python (p.ex. SQLAlchemy / Pydantic),
* SQL (`CREATE TABLE` etc).

Abaixo, um mini-“DSL” em YAML** + um exemplo já baseado no MVP do BotecoPro (products, orders, order_items, tables, payments, stock_moves) conforme a proposta técnica [001_domain.yaml].

Na pasta 'PLAN' voce irá encrontrar os arquivos relacionados ao plano. Tenha em mente que o repositorio atual é um icebreaker que deve ser melhorado para compensar as nessecidades detalhadas aqui nesse documento

---

## 1. Estrutura geral do YAML

A sugestão é separar em blocos:

```yaml
version: 1
project: boteco_pro

targets:
  dart:
    null_safety: true
  python:
    orm: sqlalchemy
  sql:
    dialect: postgres

types:
  money:
    base: int        # armazenado em centavos
    description: Monetary value in cents.
  uuid_pk:
    base: uuid
    primary_key: true
    default: gen_random_uuid()

schemas:
  app_config:
    description: Configuração global e multi-tenancy.
  org:
    description: Schemas por organização (org_{slug})

entities:
  ...
```

Depois, dentro de `entities`, você descreve as tabelas.

---

## 2. Modelo de entidade (tabelas)

Padrão sugerido para cada entidade:

```yaml
entities:
  products:
    schema: org          # será 'org_{slug}' na geração de SQL
    table_name: products
    description: Product catalog.
    fields:
      id:
        type: uuid_pk
      sku:
        type: string
        max_length: 64
        unique: true
        nullable: true
      name:
        type: string
        max_length: 255
        nullable: false
      price_cents:
        type: money
        nullable: false
      tax:
        type: numeric
        precision: 10
        scale: 2
        default: 0
      active:
        type: bool
        default: true
      updated_at:
        type: timestamptz
        default: now()
    indexes:
      - name: idx_products_active
        fields: [active]
```

### Campos suportados (sugestão)

Para cada `field`:

* `type`: tipo lógico (string, int, bool, date, datetime, uuid, numeric, json, money, uuid_pk…)
* `nullable`: `true/false`
* `default`: string livre para a camada SQL (ex: `now()`, `gen_random_uuid()`).
* `unique`: bool
* `max_length`: para strings
* `precision / scale`: para numéricos
* `ref`: referência FK — `schema.entity.field` ou apenas `entity.field` (assumindo mesmo schema).

Exemplo de campo com FK:

```yaml
table_id:
  type: uuid
  ref: tables.id    # gera FK para org.tables(id)
  nullable: false
```

---

## 3. Exemplo completo: MVP BotecoPro em YAML

Abaixo um **YAML único** com as 6 tabelas mínimas citadas na proposta técnica: Products, Orders, OrderItems, Tables, Payments, StockMoves. 

```yaml
version: 1
project: boteco_pro

targets:
  dart:
    null_safety: true
  python:
    orm: sqlalchemy
  sql:
    dialect: postgres

types:
  uuid_pk:
    base: uuid
    primary_key: true
    default: gen_random_uuid()

  money:
    base: int
    description: Monetary value in cents.

schemas:
  app_config:
    description: Global configuration and multi-tenancy.
  org:
    description: Per-organization schemas (org_{slug})

entities:
  products:
    schema: org
    table_name: products
    description: Product catalog (menu items, SKUs).
    fields:
      id:
        type: uuid_pk
      sku:
        type: string
        max_length: 64
        unique: true
        nullable: true
      name:
        type: string
        max_length: 255
        nullable: false
      price_cents:
        type: money
        nullable: false
      tax:
        type: numeric
        precision: 10
        scale: 2
        default: 0
      active:
        type: bool
        default: true
      updated_at:
        type: timestamptz
        default: now()
    indexes:
      - name: idx_products_active
        fields: [active]

  tables:
    schema: org
    table_name: tables
    description: Physical tables in the restaurant/bar.
    fields:
      id:
        type: uuid_pk
      name:
        type: string
        max_length: 64
        nullable: false
      status:
        type: string
        enum: [free, occupied, reserved]
        default: free
      seats:
        type: int
        default: 0

  orders:
    schema: org
    table_name: orders
    description: Orders associated with tables.
    fields:
      id:
        type: uuid_pk
      table_id:
        type: uuid
        ref: tables.id         # FK
        nullable: false
      status:
        type: string
        enum: [open, closed, cancelled]
        default: open
      total_cents:
        type: money
        default: 0
      opened_at:
        type: timestamptz
        default: now()
      closed_at:
        type: timestamptz
        nullable: true
    indexes:
      - name: idx_orders_table_status
        fields: [table_id, status]

  order_items:
    schema: org
    table_name: order_items
    description: Items inside an order.
    fields:
      id:
        type: uuid_pk
      order_id:
        type: uuid
        ref: orders.id
        nullable: false
      product_id:
        type: uuid
        ref: products.id
        nullable: false
      qty:
        type: numeric
        precision: 10
        scale: 2
        default: 1
      note:
        type: string
        max_length: 512
        nullable: true
      price_cents:
        type: money
        nullable: false

  payments:
    schema: org
    table_name: payments
    description: Payments associated with an order.
    fields:
      id:
        type: uuid_pk
      order_id:
        type: uuid
        ref: orders.id
        nullable: false
      method:
        type: string
        enum: [cash, card, pix, voucher]
        nullable: false
      amount_cents:
        type: money
        nullable: false
      paid_at:
        type: timestamptz
        default: now()

  stock_moves:
    schema: org
    table_name: stock_moves
    description: Stock movements for products.
    fields:
      id:
        type: uuid_pk
      product_id:
        type: uuid
        ref: products.id
        nullable: false
      qty_delta:
        type: numeric
        precision: 10
        scale: 3
        nullable: false
      reason:
        type: string
        max_length: 128
        nullable: false
      at:
        type: timestamptz
        default: now()
```

O arquivo deve ser suficiente para:

* gerar SQL (`CREATE TABLE`, `ALTER TABLE ADD CONSTRAINT`, índices…),
* gerar classes Dart,
* gerar modelos Python.

---

## 4. Como mapear para cada linguagem (ideia de geração)

### Dart (Freezed / json_serializable)

A partir do YAML, o gerador pode mapear:

* `uuid` → `String` ou classe `UuidValue`
* `timestamptz` → `DateTime`
* `money` → `int` (cents)
* enums → `enum Status { open, closed, cancelled }`

Por exemplo, o `orders` viraria:

```dart
@freezed
class Order with _$Order {
  const factory Order({
    required String id,
    required String tableId,
    @Default('open') String status,
    @Default(0) int totalCents,
    required DateTime openedAt,
    DateTime? closedAt,
  }) = _Order;

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
}
```

### Python (SQLAlchemy)

Mapeando tipos:

* `uuid` → `UUID(as_uuid=True)`
* `timestamptz` → `DateTime(timezone=True)`
* `money` → `Integer`

Orders:

```python
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id"), nullable=False)
    status = Column(String, default="open")
    total_cents = Column(Integer, default=0)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
```

### SQL (Postgres)

Para `orders`:

```sql
create table org_{slug}.orders (
  id uuid primary key default gen_random_uuid(),
  table_id uuid not null references org_{slug}.tables(id),
  status text not null default 'open',
  total_cents int not null default 0,
  opened_at timestamptz not null default now(),
  closed_at timestamptz
);

create index idx_orders_table_status
  on org_{slug}.orders(table_id, status);
```

---

## 5. Próximos passos práticos recomendados

1. **Ajustar esse YAML** para incluir mais tabelas do teu plano (estoque avançado, fornecedores, funcionários etc.).
2. Sugerir a estrutura de um **script gerador** (por ex. em Python) que:

   * lê esse YAML,
   * gera arquivos `.sql`,
   * gera `.dart` (com Freezed),
   * gera modelos Python.

Mas com esse modelo acima você já tem uma **base sólida de “single source of truth”** pro BotecoPro.
