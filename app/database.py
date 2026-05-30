# ============================================
# 1C Торговля - Модуль работы с базой данных
# ============================================

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Класс для управления подключением к MySQL и выполнением запросов"""
    
    def __init__(self):
        self.connection = None
        self.connected = False
    
    def connect(self):
        """Подключиться к базе данных"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.connected = True
                logger.info("✓ Подключение к MySQL успешно")
                return True
        except Error as e:
            logger.error(f"✗ Ошибка подключения: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Отключиться от базы данных"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connected = False
            logger.info("✓ Соединение закрыто")
    
    def execute_query(self, query, params=None):
        """Выполнить SELECT запрос"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"✗ Ошибка запроса: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Выполнить INSERT/UPDATE/DELETE"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            logger.info(f"✓ Затронуто строк: {cursor.rowcount}")
            cursor.close()
            return True
        except Error as e:
            self.connection.rollback()
            logger.error(f"✗ Ошибка: {e}")
            return False
    
    def get_one(self, query, params=None):
        """Получить одну строку"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"✗ Ошибка запроса: {e}")
            return None


# ============================================
# ФУНКЦИИ ДЛЯ СПРАВОЧНИКОВ
# ============================================

class SupplierManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = "SELECT * FROM suppliers WHERE is_active = TRUE ORDER BY name"
        return self.db.execute_query(query)
    
    def get_by_id(self, supplier_id):
        query = "SELECT * FROM suppliers WHERE supplier_id = %s"
        return self.db.get_one(query, (supplier_id,))
    
    def add(self, name, inn, address, phone, email, contact_person):
        query = """INSERT INTO suppliers (name, inn, address, phone, email, contact_person)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        return self.db.execute_update(query, (name, inn, address, phone, email, contact_person))
    
    def update(self, supplier_id, name, inn, address, phone, email, contact_person):
        query = """UPDATE suppliers SET name=%s, inn=%s, address=%s, phone=%s, email=%s, contact_person=%s
                   WHERE supplier_id=%s"""
        return self.db.execute_update(query, (name, inn, address, phone, email, contact_person, supplier_id))
    
    def delete(self, supplier_id):
        query = "UPDATE suppliers SET is_active = FALSE WHERE supplier_id = %s"
        return self.db.execute_update(query, (supplier_id,))


class CustomerManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = "SELECT * FROM customers WHERE is_active = TRUE ORDER BY name"
        return self.db.execute_query(query)
    
    def get_by_id(self, customer_id):
        query = "SELECT * FROM customers WHERE customer_id = %s"
        return self.db.get_one(query, (customer_id,))
    
    def add(self, name, inn, address, phone, email, contact_person):
        query = """INSERT INTO customers (name, inn, address, phone, email, contact_person)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        return self.db.execute_update(query, (name, inn, address, phone, email, contact_person))
    
    def update(self, customer_id, name, inn, address, phone, email, contact_person):
        query = """UPDATE customers SET name=%s, inn=%s, address=%s, phone=%s, email=%s, contact_person=%s
                   WHERE customer_id=%s"""
        return self.db.execute_update(query, (name, inn, address, phone, email, contact_person, customer_id))
    
    def delete(self, customer_id):
        query = "UPDATE customers SET is_active = FALSE WHERE customer_id = %s"
        return self.db.execute_update(query, (customer_id,))


class ProductManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = "SELECT * FROM products WHERE is_active = TRUE ORDER BY name"
        return self.db.execute_query(query)
    
    def get_by_id(self, product_id):
        query = "SELECT * FROM products WHERE product_id = %s"
        return self.db.get_one(query, (product_id,))
    
    def add(self, name, article, unit_of_measure, purchase_price, sale_price, description):
        query = """INSERT INTO products (name, article, unit_of_measure, purchase_price, sale_price, description)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        return self.db.execute_update(query, (name, article, unit_of_measure, purchase_price, sale_price, description))
    
    def update(self, product_id, name, article, unit_of_measure, purchase_price, sale_price, description):
        query = """UPDATE products SET name=%s, article=%s, unit_of_measure=%s, purchase_price=%s, sale_price=%s, description=%s
                   WHERE product_id=%s"""
        return self.db.execute_update(query, (name, article, unit_of_measure, purchase_price, sale_price, description, product_id))
    
    def delete(self, product_id):
        query = "UPDATE products SET is_active = FALSE WHERE product_id = %s"
        return self.db.execute_update(query, (product_id,))


class WarehouseManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = "SELECT * FROM warehouses WHERE is_active = TRUE ORDER BY name"
        return self.db.execute_query(query)
    
    def get_by_id(self, warehouse_id):
        query = "SELECT * FROM warehouses WHERE warehouse_id = %s"
        return self.db.get_one(query, (warehouse_id,))
    
    def add(self, name, address, manager, phone):
        query = """INSERT INTO warehouses (name, address, manager, phone)
                   VALUES (%s, %s, %s, %s)"""
        return self.db.execute_update(query, (name, address, manager, phone))
    
    def update(self, warehouse_id, name, address, manager, phone):
        query = """UPDATE warehouses SET name=%s, address=%s, manager=%s, phone=%s
                   WHERE warehouse_id=%s"""
        return self.db.execute_update(query, (name, address, manager, phone, warehouse_id))
    
    def delete(self, warehouse_id):
        query = "UPDATE warehouses SET is_active = FALSE WHERE warehouse_id = %s"
        return self.db.execute_update(query, (warehouse_id,))


class WaybillManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = """SELECT w.*, s.name as supplier_name, wh.name as warehouse_name
                   FROM waybills w
                   JOIN suppliers s ON w.supplier_id = s.supplier_id
                   JOIN warehouses wh ON w.warehouse_id = wh.warehouse_id
                   ORDER BY w.waybill_date DESC"""
        return self.db.execute_query(query)
    
    def get_by_id(self, waybill_id):
        query = """SELECT w.*, s.name as supplier_name, wh.name as warehouse_name
                   FROM waybills w
                   JOIN suppliers s ON w.supplier_id = s.supplier_id
                   JOIN warehouses wh ON w.warehouse_id = wh.warehouse_id
                   WHERE w.waybill_id = %s"""
        return self.db.get_one(query, (waybill_id,))
    
    def get_items(self, waybill_id):
        query = """SELECT wi.*, p.name as product_name, p.article
                   FROM waybill_items wi
                   JOIN products p ON wi.product_id = p.product_id
                   WHERE wi.waybill_id = %s"""
        return self.db.execute_query(query, (waybill_id,))
    
    def add(self, waybill_number, waybill_date, supplier_id, warehouse_id, notes):
        query = """INSERT INTO waybills (waybill_number, waybill_date, supplier_id, warehouse_id, notes, status)
                   VALUES (%s, %s, %s, %s, %s, 'draft')"""
        return self.db.execute_update(query, (waybill_number, waybill_date, supplier_id, warehouse_id, notes))
    
    def add_item(self, waybill_id, product_id, quantity, unit_price):
        query = """INSERT INTO waybill_items (waybill_id, product_id, quantity, unit_price)
                   VALUES (%s, %s, %s, %s)"""
        return self.db.execute_update(query, (waybill_id, product_id, quantity, unit_price))


class InvoiceManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = """SELECT i.*, c.name as customer_name, wh.name as warehouse_name
                   FROM invoices i
                   JOIN customers c ON i.customer_id = c.customer_id
                   JOIN warehouses wh ON i.warehouse_id = wh.warehouse_id
                   ORDER BY i.invoice_date DESC"""
        return self.db.execute_query(query)
    
    def get_by_id(self, invoice_id):
        query = """SELECT i.*, c.name as customer_name, wh.name as warehouse_name
                   FROM invoices i
                   JOIN customers c ON i.customer_id = c.customer_id
                   JOIN warehouses wh ON i.warehouse_id = wh.warehouse_id
                   WHERE i.invoice_id = %s"""
        return self.db.get_one(query, (invoice_id,))
    
    def get_items(self, invoice_id):
        query = """SELECT ii.*, p.name as product_name, p.article
                   FROM invoice_items ii
                   JOIN products p ON ii.product_id = p.product_id
                   WHERE ii.invoice_id = %s"""
        return self.db.execute_query(query, (invoice_id,))
    
    def add(self, invoice_number, invoice_date, customer_id, warehouse_id, notes):
        query = """INSERT INTO invoices (invoice_number, invoice_date, customer_id, warehouse_id, notes, status)
                   VALUES (%s, %s, %s, %s, %s, 'draft')"""
        return self.db.execute_update(query, (invoice_number, invoice_date, customer_id, warehouse_id, notes))
    
    def add_item(self, invoice_id, product_id, quantity, unit_price):
        query = """INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price)
                   VALUES (%s, %s, %s, %s)"""
        return self.db.execute_update(query, (invoice_id, product_id, quantity, unit_price))


class StockManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_all(self):
        query = """SELECT sb.*, p.name as product_name, p.article, w.name as warehouse_name,
                   (sb.quantity_in_stock - sb.quantity_reserved) as available
                   FROM stock_balances sb
                   JOIN products p ON sb.product_id = p.product_id
                   JOIN warehouses w ON sb.warehouse_id = w.warehouse_id
                   ORDER BY p.name"""
        return self.db.execute_query(query)
    
    def get_low_stock(self, threshold=100):
        query = """SELECT sb.*, p.name as product_name, w.name as warehouse_name,
                   (sb.quantity_in_stock - sb.quantity_reserved) as available
                   FROM stock_balances sb
                   JOIN products p ON sb.product_id = p.product_id
                   JOIN warehouses w ON sb.warehouse_id = w.warehouse_id
                   WHERE sb.quantity_in_stock < %s
                   ORDER BY sb.quantity_in_stock"""
        return self.db.execute_query(query, (threshold,))
