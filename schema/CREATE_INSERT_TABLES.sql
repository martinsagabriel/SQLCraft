CREATE TABLE Loja (
    id_loja INT IDENTITY(1,1) PRIMARY KEY, 
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(9),   
    telefone VARCHAR(20)
);
GO

CREATE TABLE Produto (
    id_produto INT IDENTITY(1,1) PRIMARY KEY,
    codigo_sku VARCHAR(50) UNIQUE,
    nome VARCHAR(150) NOT NULL,
    descricao VARCHAR(MAX),       
    preco_unitario DECIMAL(10, 2) NOT NULL CHECK (preco_unitario >= 0),
    categoria VARCHAR(50),
    unidade_medida VARCHAR(10)    
);
GO

CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cpf_cnpj VARCHAR(18) UNIQUE,
    email VARCHAR(100) UNIQUE,
    telefone VARCHAR(20),
    endereco VARCHAR(255),
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(9),
    data_cadastro DATE DEFAULT GETDATE()
);
GO

CREATE TABLE Vendedor (
    id_vendedor INT IDENTITY(1,1) PRIMARY KEY,
    id_loja INT NOT NULL,         
    nome VARCHAR(150) NOT NULL,
    cpf VARCHAR(14) UNIQUE,       
    email VARCHAR(100) UNIQUE,    
    telefone VARCHAR(20),
    percentual_comissao DECIMAL(5, 2) DEFAULT 0.00 CHECK (percentual_comissao >= 0),
    CONSTRAINT FK_Vendedor_Loja FOREIGN KEY (id_loja) REFERENCES Loja(id_loja)
    
    
);
GO

CREATE TABLE Vendas (
    id_venda INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,      
    id_vendedor INT NOT NULL,     
    id_loja INT NOT NULL,         
    data_hora_venda DATETIME2 DEFAULT GETDATE(),
    valor_total DECIMAL(12, 2) NOT NULL CHECK (valor_total >= 0),
    forma_pagamento VARCHAR(50),
    status_venda VARCHAR(30) DEFAULT 'Concluída',
    CONSTRAINT FK_Vendas_Clientes FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    CONSTRAINT FK_Vendas_Vendedor FOREIGN KEY (id_vendedor) REFERENCES Vendedor(id_vendedor),
    CONSTRAINT FK_Vendas_Loja FOREIGN KEY (id_loja) REFERENCES Loja(id_loja)
);
GO

CREATE TABLE ItensVenda (
    id_venda INT NOT NULL,        
    id_produto INT NOT NULL,      
    quantidade DECIMAL(10, 3) NOT NULL CHECK (quantidade > 0),
    preco_unitario_venda DECIMAL(10, 2) NOT NULL CHECK (preco_unitario_venda >= 0),
    CONSTRAINT PK_ItensVenda PRIMARY KEY (id_venda, id_produto),
    CONSTRAINT FK_ItensVenda_Vendas FOREIGN KEY (id_venda)
        REFERENCES Vendas(id_venda)
        ON DELETE CASCADE,
    CONSTRAINT FK_ItensVenda_Produto FOREIGN KEY (id_produto)
        REFERENCES Produto(id_produto)
);
GO
