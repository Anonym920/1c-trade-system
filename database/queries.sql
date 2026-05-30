-- ============================================
-- 1C Торговля - Основные SQL Запросы
-- ============================================

USE trade_system;

-- ============================================
-- ЗАПРОСЫ ДЛЯ АНАЛИТИКИ ОСТАТКОВ
-- ============================================

-- Запрос 1: Остатки товаров на всех складах с стоимостью
-- Включает: JOIN, GROUP BY, агрегатные функции
SELECT 
    p.product_id,
    p.name,
    p.article,
    SUM(sb.quantity_in_stock) AS total_quantity,
    SUM(sb.quantity_reserved) AS total_reserved,
    SUM(sb.quantity_in_stock - sb.quantity_reserved) AS available_quantity,
    p.sale_price,
    SUM((sb.quantity_in_stock - sb.quantity_reserved) * p.sale_price) AS total_value
FROM products p
LEFT JOIN stock_balances sb ON p.product_id = sb.product_id
WHERE p.is_active = TRUE
GROUP BY p.product_id, p.name, p.article, p.sale_price
HAVING total_quantity > 0
ORDER BY total_value DESC;

-- Запрос 2: Низкие остатки (менее 100 единиц)
-- Включает: WHERE, фильтрацию, ORDER BY
SELECT 
    sb.product_id,
    p.name,
    w.name AS warehouse_name,
    sb.quantity_in_stock,
    sb.quantity_reserved,
    (sb.quantity_in_stock - sb.quantity_reserved) AS available,
    p.purchase_price,
    (sb.quantity_in_stock * p.purchase_price) AS storage_value
FROM stock_balances sb
JOIN products p ON sb.product_id = p.product_id
JOIN warehouses w ON sb.warehouse_id = w.warehouse_id
WHERE sb.quantity_in_stock < 100 AND p.is_active = TRUE
ORDER BY sb.quantity_in_stock ASC;

-- Запрос 3: Остатки по складам с процентным распределением
-- Включает: CASE, подзапросы, вычисления
SELECT 
    w.warehouse_id,
    w.name,
    COUNT(sb.product_id) AS products_count,
    SUM(sb.quantity_in_stock) AS total_quantity,
    ROUND(SUM(sb.quantity_in_stock * p.sale_price), 2) AS warehouse_value,
    ROUND(
        (SUM(sb.quantity_in_stock * p.sale_price) / 
        (SELECT SUM(sb2.quantity_in_stock * p2.sale_price) 
         FROM stock_balances sb2 
         JOIN products p2 ON sb2.product_id = p2.product_id)) * 100, 2
    ) AS percentage_of_total
FROM warehouses w
LEFT JOIN stock_balances sb ON w.warehouse_id = sb.warehouse_id
LEFT JOIN products p ON sb.product_id = p.product_id
WHERE w.is_active = TRUE
GROUP BY w.warehouse_id, w.name
ORDER BY warehouse_value DESC;

-- ============================================
-- ЗАПРОСЫ ДЛЯ АНАЛИТИКИ ПОСТУПЛЕНИЙ
-- ============================================

-- Запрос 4: Анализ поступлений по поставщикам
-- Включает: JOIN, GROUP BY, SUM, COUNT, агрегатные функции
SELECT 
    s.supplier_id,
    s.name,
    COUNT(DISTINCT w.waybill_id) AS waybills_count,
    COUNT(wi.item_id) AS items_total,
    SUM(wi.quantity) AS items_quantity,
    ROUND(SUM(wi.total_price), 2) AS total_amount,
    ROUND(AVG(wi.total_price), 2) AS avg_item_price,
    MAX(w.waybill_date) AS last_delivery_date
FROM suppliers s
LEFT JOIN waybills w ON s.supplier_id = w.supplier_id
LEFT JOIN waybill_items wi ON w.waybill_id = wi.waybill_id
WHERE s.is_active = TRUE
GROUP BY s.supplier_id, s.name
ORDER BY total_amount DESC;

-- Запрос 5: Детальный анализ накладной с товарами
-- Включает: JOIN, вложенные запросы
SELECT 
    w.waybill_id,
    w.waybill_number,
    w.waybill_date,
    s.name AS supplier_name,
    wh.name AS warehouse_name,
    p.name AS product_name,
    wi.quantity,
    wi.unit_price,
    wi.total_price,
    DATEDIFF(CURDATE(), w.waybill_date) AS days_since_arrival
FROM waybills w
JOIN suppliers s ON w.supplier_id = s.supplier_id
JOIN warehouses wh ON w.warehouse_id = wh.warehouse_id
JOIN waybill_items wi ON w.waybill_id = wi.waybill_id
JOIN products p ON wi.product_id = p.product_id
WHERE w.waybill_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
ORDER BY w.waybill_date DESC, w.waybill_number;

-- Запрос 6: Поступления по датам с итогами
-- Включает: GROUP BY, DATE TRUNC, агрегатные функции
SELECT 
    DATE(w.waybill_date) AS delivery_date,
    COUNT(DISTINCT w.waybill_id) AS waybills_count,
    SUM(wi.quantity) AS items_quantity,
    ROUND(SUM(wi.total_price), 2) AS total_amount,
    COUNT(DISTINCT s.supplier_id) AS suppliers_count
FROM waybills w
JOIN waybill_items wi ON w.waybill_id = wi.waybill_id
JOIN suppliers s ON w.supplier_id = s.supplier_id
GROUP BY DATE(w.waybill_date)
ORDER BY delivery_date DESC;

-- ============================================
-- ЗАПРОСЫ ДЛЯ АНАЛИЗА ПРОДАЖ
-- ============================================

-- Запрос 7: Анализ продаж по покупателям
-- Включает: JOIN, GROUP BY, SUM, COUNT, фильтрация
SELECT 
    c.customer_id,
    c.name,
    COUNT(DISTINCT i.invoice_id) AS invoices_count,
    COUNT(ii.item_id) AS items_total,
    SUM(ii.quantity) AS items_quantity,
    ROUND(SUM(ii.total_price), 2) AS total_sales,
    ROUND(AVG(ii.unit_price), 2) AS avg_item_price,
    MAX(i.invoice_date) AS last_sale_date
FROM customers c
LEFT JOIN invoices i ON c.customer_id = i.customer_id
LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
WHERE c.is_active = TRUE
GROUP BY c.customer_id, c.name
HAVING invoices_count > 0
ORDER BY total_sales DESC;

-- Запрос 8: Продажи по товарам с анализом рентабельности
-- Включает: JOIN, вычисления, GROUP BY
SELECT 
    p.product_id,
    p.name,
    p.article,
    SUM(ii.quantity) AS quantity_sold,
    ROUND(SUM(ii.total_price), 2) AS revenue,
    p.purchase_price,
    p.sale_price,
    ROUND((p.sale_price - p.purchase_price), 2) AS profit_per_unit,
    ROUND(SUM(ii.quantity) * (p.sale_price - p.purchase_price), 2) AS total_profit,
    ROUND((((p.sale_price - p.purchase_price) / p.purchase_price) * 100), 2) AS margin_percent
FROM products p
JOIN invoice_items ii ON p.product_id = ii.product_id
GROUP BY p.product_id, p.name, p.article, p.purchase_price, p.sale_price
ORDER BY total_profit DESC;

-- Запрос 9: Продажи по датам
-- Включает: DATE GROUP BY, агрегатные функции
SELECT 
    DATE(i.invoice_date) AS sale_date,
    COUNT(DISTINCT i.invoice_id) AS invoices_count,
    SUM(ii.quantity) AS items_quantity,
    ROUND(SUM(ii.total_price), 2) AS total_amount,
    COUNT(DISTINCT c.customer_id) AS customers_count,
    ROUND(SUM(ii.total_price) / COUNT(DISTINCT i.invoice_id), 2) AS avg_invoice_amount
FROM invoices i
JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
JOIN customers c ON i.customer_id = c.customer_id
GROUP BY DATE(i.invoice_date)
ORDER BY sale_date DESC;

-- ============================================
-- ЗАПРОСЫ ДЛЯ КОНТРОЛЯ И МОНИТОРИНГА
-- ============================================

-- Запрос 10: Несоответствие резервирования и продажи
-- Включает: LEFT JOIN, WHERE, анализ данных
SELECT 
    sb.product_id,
    p.name,
    w.name AS warehouse_name,
    sb.quantity_reserved,
    (SELECT COUNT(ii.item_id) 
     FROM invoice_items ii 
     JOIN invoices i ON ii.invoice_id = i.invoice_id
     WHERE ii.product_id = p.product_id 
     AND i.warehouse_id = w.warehouse_id
     AND i.status IN ('draft', 'issued')) AS items_in_draft_invoices,
    (sb.quantity_reserved - COALESCE((SELECT COUNT(ii.item_id) 
     FROM invoice_items ii 
     JOIN invoices i ON ii.invoice_id = i.invoice_id
     WHERE ii.product_id = p.product_id 
     AND i.warehouse_id = w.warehouse_id
     AND i.status IN ('draft', 'issued')), 0)) AS discrepancy
FROM stock_balances sb
JOIN products p ON sb.product_id = p.product_id
JOIN warehouses w ON sb.warehouse_id = w.warehouse_id
HAVING discrepancy != 0
ORDER BY discrepancy DESC;

-- Запрос 11: ТОП товаров по продажам за период
-- Включает: WHERE, DATE фильтрацию, ORDER BY, LIMIT
SELECT 
    p.product_id,
    p.name,
    p.article,
    SUM(ii.quantity) AS quantity_sold,
    ROUND(SUM(ii.total_price), 2) AS revenue,
    COUNT(DISTINCT i.invoice_id) AS sales_count,
    ROUND(SUM(ii.quantity) / COUNT(DISTINCT i.invoice_id), 2) AS avg_qty_per_sale
FROM products p
JOIN invoice_items ii ON p.product_id = ii.product_id
JOIN invoices i ON ii.invoice_id = i.invoice_id
WHERE i.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
  AND i.status = 'paid'
GROUP BY p.product_id, p.name, p.article
ORDER BY revenue DESC
LIMIT 10;

-- Запрос 12: Финансовый отчет за период
-- Включает: DATE диапазон, агрегатные функции
SELECT 
    'Поступления' AS type,
    COUNT(DISTINCT w.waybill_id) AS document_count,
    ROUND(SUM(wi.total_price), 2) AS total_amount,
    (SELECT ROUND(SUM(wi2.total_price), 2) 
     FROM waybills w2 
     JOIN waybill_items wi2 ON w2.waybill_id = wi2.waybill_id
     WHERE w2.waybill_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) AS last_30_days
FROM waybills w
JOIN waybill_items wi ON w.waybill_id = wi.waybill_id

UNION ALL

SELECT 
    'Продажи',
    COUNT(DISTINCT i.invoice_id),
    ROUND(SUM(ii.total_price), 2),
    (SELECT ROUND(SUM(ii2.total_price), 2) 
     FROM invoices i2 
     JOIN invoice_items ii2 ON i2.invoice_id = ii2.invoice_id
     WHERE i2.invoice_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY))
FROM invoices i
JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
WHERE i.status = 'paid';

COMMIT;