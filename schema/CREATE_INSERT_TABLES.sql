CREATE TABLE employees (
    employee_id INT PRIMARY KEY IDENTITY(1,1),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);
CREATE TABLE purchases (
    purchase_id INT PRIMARY KEY IDENTITY(1,1),
    purchase_date DATE NOT NULL,
    employee_id INT NOT NULL,
    amount FLOAT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

INSERT INTO employees (name, email) VALUES
('João Silva', 'joao.silva@example.com'),
('Maria Oliveira', 'maria.oliveira@example.com'),
('Carlos Pereira', 'carlos.pereira@example.com'),
('Ana Santos', 'ana.santos@example.com'),
('Pedro Costa', 'pedro.costa@example.com');

INSERT INTO purchases (purchase_date, employee_id, amount, product_name) VALUES
('2024-01-05', 1, 120.50, 'Monitor 24"'),
('2024-01-12', 2, 75.25, 'Mouse sem fio'),
('2024-01-18', 3, 349.99, 'Notebook Acer'),
('2024-02-03', 4, 29.99, 'Teclado USB'),
('2024-02-15', 5, 180.00, 'Impressora laser'),
('2024-02-20', 1, 55.50, 'Cadeira gamer'),
('2024-03-01', 2, 300.00, 'Smartphone Samsung'),
('2024-03-07', 3, 79.99, 'Headset gamer'),
('2024-03-14', 4, 150.00, 'Fone de ouvido Bluetooth'),
('2024-03-28', 5, 299.99, 'Tablet Lenovo');
