
# ✅ **MODELO — SQL SERVER (dbo)**

### **MVP do Boteco Pro**

---

# =========================

# 🎯 **CATEGORIAS**

# =========================

```sql
CREATE TABLE Categoria (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

CREATE TABLE Subcategoria (
    id_subcategoria INT IDENTITY(1,1) PRIMARY KEY,
    id_categoria INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria)
);
```

---

# =========================

# 📦 **PRODUTOS / INGREDIENTES**

# =========================

```sql
CREATE TABLE Produto (
    id_produto INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco_custo DECIMAL(10,2),
    stock_atual INT,
    stock_minimo INT,
    unidade_medida VARCHAR(20),       -- g, kg, ml, un
    tipo_produto VARCHAR(50),         -- ingrediente, revenda, etc
    ativo BIT DEFAULT 1
);
```

---

## Fornecedores

```sql
CREATE TABLE Fornecedor (
    id_fornecedor INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    telefone VARCHAR(20),
    observacoes TEXT
);

CREATE TABLE Fornecedor_Produto (
    id_produto INT NOT NULL,
    id_fornecedor INT NOT NULL,
    preco DECIMAL(10,2),
    observacoes TEXT,
    PRIMARY KEY (id_produto, id_fornecedor),
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto),
    FOREIGN KEY (id_fornecedor) REFERENCES Fornecedor(id_fornecedor)
);
```

---

# =========================

# 🍽️ **ITEM UNIFICADO (PRATO / BEBIDA / ARTIGO)**

# =========================

```sql
CREATE TABLE Item (
    id_item INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco_venda DECIMAL(10,2),
    custo_unidade DECIMAL(10,2),
    tempo_preparo TIME,
    tipo_item VARCHAR(20) NOT NULL CHECK (tipo_item IN ('prato','bebida','artigo')),
    id_categoria INT,
    id_subcategoria INT,
    ativo BIT DEFAULT 1,
    observacoes TEXT,
    FOREIGN KEY (id_categoria) REFERENCES Categoria(id_categoria),
    FOREIGN KEY (id_subcategoria) REFERENCES Subcategoria(id_subcategoria)
);
```

---

## Item composto por produtos (ingredientes)

```sql
CREATE TABLE Item_Produto (
    id_item INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade DECIMAL(10,2),
    PRIMARY KEY (id_item, id_produto),
    FOREIGN KEY (id_item) REFERENCES Item(id_item),
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto)
);
```

---

# =========================

# 🪑 **MESAS E COMANDAS**

# =========================

```sql
CREATE TABLE Mesa (
    id_mesa INT IDENTITY(1,1) PRIMARY KEY,
    numero INT NOT NULL,
    lugares INT,
    disponivel BIT DEFAULT 1
);
```

---

```sql
CREATE TABLE Comanda (
    id_comanda UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    id_mesa INT,
    estado VARCHAR(50), -- aberta, fechada, cancelada
    data_abertura DATETIME,
    data_fechamento DATETIME,
    total DECIMAL(10,2),
    FOREIGN KEY (id_mesa) REFERENCES Mesa(id_mesa)
);
```

---

# =========================

# 🧾 **PEDIDOS**

# =========================

## Pedido (1 registro por operação / movimentação)

```sql
CREATE TABLE Pedido (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_comanda UNIQUEIDENTIFIER NOT NULL,
    origem VARCHAR(50), -- mesa, takeaway, delivery
    id_funcionario INT,
    id_cliente INT,
    data_hora DATETIME DEFAULT GETDATE(),
    estado VARCHAR(50),
    observacoes TEXT,
    FOREIGN KEY (id_comanda) REFERENCES Comanda(id_comanda),
    FOREIGN KEY (id_funcionario) REFERENCES Funcionario(id_funcionario),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
);
```

---

## Pedido_Item (n itens por pedido)

```sql
CREATE TABLE Pedido_Item (
    id_pedido_item INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_item INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2),
    perc_imposto DECIMAL(10,2),
    perc_desconto DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    observacoes TEXT,
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_item) REFERENCES Item(id_item)
);
```

---

# =========================

# 👤 FUNCIONÁRIOS & CLIENTES

# =========================

```sql
CREATE TABLE Funcionario (
    id_funcionario INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100),
    nif VARCHAR(15),
    morada VARCHAR(255),
    localidade VARCHAR(100),
    codigo_postal VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(100),
    cargo VARCHAR(50),
    data_contratacao DATE,
    salario_base_hora DECIMAL(10,2)
);
```

```sql
CREATE TABLE Cliente (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(100),
    nif VARCHAR(15),
    morada VARCHAR(255),
    localidade VARCHAR(100),
    codigo_postal VARCHAR(20),
    tipo_cliente VARCHAR(50)
);
```

---

# =========================

# 💳 **FATURA**

# =========================

(Agora sem duplicações, e vinculada à COMANDA)

```sql
CREATE TABLE Fatura (
    id_fatura INT IDENTITY(1,1) PRIMARY KEY,
    id_comanda UNIQUEIDENTIFIER NOT NULL,
    valor_sem_imposto DECIMAL(10,2),
    total_imposto DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    data_fechamento DATE,
    tipo_iva_comida DECIMAL(5,2),
    tipo_iva_bebida DECIMAL(5,2),
    FOREIGN KEY (id_comanda) REFERENCES Comanda(id_comanda)
);
```
