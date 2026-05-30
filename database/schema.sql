-- ============================================
-- 1C Торговля - SQL Схема БД
-- MySQL 8.0
-- ============================================

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS trade_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE trade_system;

-- ============================================
-- СПРАВОЧНИКИ
-- ============================================

-- Таблица: Поставщики
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    inn VARCHAR(20) UNIQUE,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    contact_person VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (LENGTH(inn) IN (10, 12))
);

-- Таблица: Покупатели
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    inn VARCHAR(20) UNIQUE,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    contact_person VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (LENGTH(inn) IN (10, 12))
);

-- Таблица: Товары
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    article VARCHAR(50) UNIQUE NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'шт',
    purchase_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    sale_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (purchase_price >= 0),
    CHECK (sale_price >= 0)
);

-- Таблица: Склады
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    address VARCHAR(255),
    manager VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- ДОКУМЕНТЫ ПОСТУПЛЕНИЯ
-- ============================================

-- Таблица: Накладные (поступления товара)
CREATE TABLE IF NOT EXISTS waybills (
    waybill_id INT PRIMARY KEY AUTO_INCREMENT,
    waybill_number VARCHAR(50) UNIQUE NOT NULL,
    waybill_date DATE NOT NULL,
    supplier_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    receipt_date DATE,
    status ENUM('draft', 'received', 'confirmed') DEFAULT 'draft',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    INDEX idx_supplier (supplier_id),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_date (waybill_date)
);

-- Таблица: Строки накладной
CREATE TABLE IF NOT EXISTS waybill_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    waybill_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (quantity > 0),
    CHECK (unit_price >= 0),
    FOREIGN KEY (waybill_id) REFERENCES waybills(waybill_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_waybill (waybill_id),
    INDEX idx_product (product_id)
);

-- ============================================
-- ДОКУМЕНТЫ ПРОДАЖИ
-- ============================================

-- Таблица: Счет-фактуры (продажи)
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_date DATE NOT NULL,
    customer_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    total_amount DECIMAL(12, 2),
    status ENUM('draft', 'issued', 'paid') DEFAULT 'draft',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE RESTRICT,
    INDEX idx_customer (customer_id),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_date (invoice_date)
);

-- Таблица: Строки счета-фактуры
CREATE TABLE IF NOT EXISTS invoice_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (quantity > 0),
    CHECK (unit_price >= 0),
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT,
    INDEX idx_invoice (invoice_id),
    INDEX idx_product (product_id)
);

-- ============================================
-- УЧЕТ ОСТАТКОВ
-- ============================================

-- Таблица: Остатки товаров на складах
CREATE TABLE IF NOT EXISTS stock_balances (
    balance_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity_in_stock INT DEFAULT 0,
    quantity_reserved INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_product_warehouse (product_id, warehouse_id),
    CHECK (quantity_in_stock >= 0),
    CHECK (quantity_reserved >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
    INDEX idx_product (product_id),
    INDEX idx_warehouse (warehouse_id)
);

-- ============================================
-- ИНДЕКСЫ
-- ============================================

CREATE INDEX idx_suppliers_active ON suppliers(is_active);
CREATE INDEX idx_customers_active ON customers(is_active);
CREATE INDEX idx_products_active ON products(is_active);
CREATE INDEX idx_warehouses_active ON warehouses(is_active);
CREATE INDEX idx_waybills_status ON waybills(status);
CREATE INDEX idx_invoices_status ON invoices(status);

-- ============================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ============================================

-- Представление: Остатки товаров по складам с информацией о товарах
CREATE OR REPLACE VIEW v_stock_info AS
SELECT 
    sb.balance_id,
    sb.product_id,
    sb.warehouse_id,
    p.name AS product_name,
    p.article,
    p.unit_of_measure,
    w.name AS warehouse_name,
    sb.quantity_in_stock,
    sb.quantity_reserved,
    (sb.quantity_in_stock - sb.quantity_reserved) AS quantity_available,
    p.sale_price,
    (sb.quantity_in_stock * p.sale_price) AS total_value
FROM stock_balances sb
JOIN products p ON sb.product_id = p.product_id
JOIN warehouses w ON sb.warehouse_id = w.warehouse_id;

-- Представление: Детали накладных
CREATE OR REPLACE VIEW v_waybill_details AS
SELECT 
    w.waybill_id,
    w.waybill_number,
    w.waybill_date,
    s.name AS supplier_name,
    wh.name AS warehouse_name,
    w.status,
    COUNT(wi.item_id) AS items_count,
    SUM(wi.total_price) AS total_amount
FROM waybills w
JOIN suppliers s ON w.supplier_id = s.supplier_id
JOIN warehouses wh ON w.warehouse_id = wh.warehouse_id
LEFT JOIN waybill_items wi ON w.waybill_id = wi.waybill_id
GROUP BY w.waybill_id, w.waybill_number, w.waybill_date, s.name, wh.name, w.status;

-- Представление: Детали счет-фактур
CREATE OR REPLACE VIEW v_invoice_details AS
SELECT 
    i.invoice_id,
    i.invoice_number,
    i.invoice_date,
    c.name AS customer_name,
    wh.name AS warehouse_name,
    i.status,
    COUNT(ii.item_id) AS items_count,
    COALESCE(SUM(ii.total_price), 0) AS total_amount
FROM invoices i
JOIN customers c ON i.customer_id = c.customer_id
JOIN warehouses wh ON i.warehouse_id = wh.warehouse_id
LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
GROUP BY i.invoice_id, i.invoice_number, i.invoice_date, c.name, wh.name, i.status;

COMMIT;