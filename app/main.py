# ============================================
# 1C Торговля - Главное приложение PyQt6
# ============================================

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
    QDialog, QLabel, QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QFormLayout, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont
from app.database import (
    DatabaseManager, SupplierManager, CustomerManager, ProductManager,
    WarehouseManager, WaybillManager, InvoiceManager, StockManager
)
from config import APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WAYBILL_STATUSES, INVOICE_STATUSES
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Инициализация БД
        self.db = DatabaseManager()
        if not self.db.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            sys.exit()
        
        # Инициализация менеджеров
        self.suppliers_mgr = SupplierManager(self.db)
        self.customers_mgr = CustomerManager(self.db)
        self.products_mgr = ProductManager(self.db)
        self.warehouses_mgr = WarehouseManager(self.db)
        self.waybills_mgr = WaybillManager(self.db)
        self.invoices_mgr = InvoiceManager(self.db)
        self.stock_mgr = StockManager(self.db)
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout()
        
        # Табы
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_suppliers_tab(), "Поставщики")
        self.tabs.addTab(self.create_customers_tab(), "Покупатели")
        self.tabs.addTab(self.create_products_tab(), "Товары")
        self.tabs.addTab(self.create_warehouses_tab(), "Склады")
        self.tabs.addTab(self.create_waybills_tab(), "Накладные")
        self.tabs.addTab(self.create_invoices_tab(), "Счета-фактуры")
        self.tabs.addTab(self.create_stock_tab(), "Остатки")
        self.tabs.addTab(self.create_reports_tab(), "Отчёты")
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
    
    def create_suppliers_tab(self):
        """Вкладка Поставщики"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Таблица
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels(["ID", "Название", "ИНН", "Адрес", "Телефон", "Email", "Контакт"])
        self.suppliers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.suppliers_table)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_edit = QPushButton("✎ Редактировать")
        btn_delete = QPushButton("✗ Удалить")
        btn_refresh = QPushButton("↻ Обновить")
        
        btn_add.clicked.connect(self.add_supplier)
        btn_edit.clicked.connect(self.edit_supplier)
        btn_delete.clicked.connect(self.delete_supplier)
        btn_refresh.clicked.connect(self.load_suppliers)
        
        buttons_layout.addWidget(btn_add)
        buttons_layout.addWidget(btn_edit)
        buttons_layout.addWidget(btn_delete)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_suppliers()
        return widget
    
    def load_suppliers(self):
        """Загрузить поставщиков в таблицу"""
        suppliers = self.suppliers_mgr.get_all()
        self.suppliers_table.setRowCount(0)
        
        if suppliers:
            for row, supplier in enumerate(suppliers):
                self.suppliers_table.insertRow(row)
                self.suppliers_table.setItem(row, 0, QTableWidgetItem(str(supplier['supplier_id'])))
                self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier['name']))
                self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier['inn'] or ""))
                self.suppliers_table.setItem(row, 3, QTableWidgetItem(supplier['address'] or ""))
                self.suppliers_table.setItem(row, 4, QTableWidgetItem(supplier['phone'] or ""))
                self.suppliers_table.setItem(row, 5, QTableWidgetItem(supplier['email'] or ""))
                self.suppliers_table.setItem(row, 6, QTableWidgetItem(supplier['contact_person'] or ""))
    
    def add_supplier(self):
        """Добавить нового поставщика"""
        dialog = AddSupplierDialog(self)
        if dialog.exec():
            name, inn, address, phone, email, contact = dialog.get_data()
            if self.suppliers_mgr.add(name, inn, address, phone, email, contact):
                QMessageBox.information(self, "Успех", "Поставщик добавлен")
                self.load_suppliers()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить поставщика")
    
    def edit_supplier(self):
        """Редактировать поставщика"""
        row = self.suppliers_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поставщика")
            return
        
        supplier_id = int(self.suppliers_table.item(row, 0).text())
        supplier = self.suppliers_mgr.get_by_id(supplier_id)
        
        dialog = AddSupplierDialog(self, supplier)
        if dialog.exec():
            name, inn, address, phone, email, contact = dialog.get_data()
            if self.suppliers_mgr.update(supplier_id, name, inn, address, phone, email, contact):
                QMessageBox.information(self, "Успех", "Поставщик обновлён")
                self.load_suppliers()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить поставщика")
    
    def delete_supplier(self):
        """Удалить поставщика"""
        row = self.suppliers_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите поставщика")
            return
        
        supplier_id = int(self.suppliers_table.item(row, 0).text())
        if QMessageBox.question(self, "Подтверждение", "Удалить поставщика?") == QMessageBox.StandardButton.Yes:
            if self.suppliers_mgr.delete(supplier_id):
                QMessageBox.information(self, "Успех", "Поставщик удалён")
                self.load_suppliers()
    
    def create_customers_tab(self):
        """Вкладка Покупатели (аналогично поставщикам)"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels(["ID", "Название", "ИНН", "Адрес", "Телефон", "Email", "Контакт"])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.customers_table)
        
        buttons_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_refresh = QPushButton("↻ Обновить")
        btn_add.clicked.connect(lambda: QMessageBox.information(self, "Info", "Функция в разработке"))
        btn_refresh.clicked.connect(self.load_customers)
        buttons_layout.addWidget(btn_add)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_customers()
        return widget
    
    def load_customers(self):
        """Загрузить покупателей"""
        customers = self.customers_mgr.get_all()
        self.customers_table.setRowCount(0)
        
        if customers:
            for row, customer in enumerate(customers):
                self.customers_table.insertRow(row)
                self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer['customer_id'])))
                self.customers_table.setItem(row, 1, QTableWidgetItem(customer['name']))
                self.customers_table.setItem(row, 2, QTableWidgetItem(customer['inn'] or ""))
                self.customers_table.setItem(row, 3, QTableWidgetItem(customer['address'] or ""))
                self.customers_table.setItem(row, 4, QTableWidgetItem(customer['phone'] or ""))
                self.customers_table.setItem(row, 5, QTableWidgetItem(customer['email'] or ""))
                self.customers_table.setItem(row, 6, QTableWidgetItem(customer['contact_person'] or ""))
    
    def create_products_tab(self):
        """Вкладка Товары"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(["ID", "Название", "Артикул", "Ед. изм.", "Цена закупки", "Цена продажи", "Описание"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.products_table)
        
        buttons_layout = QHBoxLayout()
        btn_add = QPushButton("+ Добавить")
        btn_refresh = QPushButton("↻ Обновить")
        btn_add.clicked.connect(lambda: QMessageBox.information(self, "Info", "Функция в разработке"))
        btn_refresh.clicked.connect(self.load_products)
        buttons_layout.addWidget(btn_add)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_products()
        return widget
    
    def load_products(self):
        """Загрузить товары"""
        products = self.products_mgr.get_all()
        self.products_table.setRowCount(0)
        
        if products:
            for row, product in enumerate(products):
                self.products_table.insertRow(row)
                self.products_table.setItem(row, 0, QTableWidgetItem(str(product['product_id'])))
                self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
                self.products_table.setItem(row, 2, QTableWidgetItem(product['article']))
                self.products_table.setItem(row, 3, QTableWidgetItem(product['unit_of_measure']))
                self.products_table.setItem(row, 4, QTableWidgetItem(str(product['purchase_price'])))
                self.products_table.setItem(row, 5, QTableWidgetItem(str(product['sale_price'])))
                self.products_table.setItem(row, 6, QTableWidgetItem(product['description'] or ""))
    
    def create_warehouses_tab(self):
        """Вкладка Склады"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.warehouses_table = QTableWidget()
        self.warehouses_table.setColumnCount(5)
        self.warehouses_table.setHorizontalHeaderLabels(["ID", "Название", "Адрес", "Менеджер", "Телефон"])
        self.warehouses_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.warehouses_table)
        
        buttons_layout = QHBoxLayout()
        btn_refresh = QPushButton("↻ Обновить")
        btn_refresh.clicked.connect(self.load_warehouses)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_warehouses()
        return widget
    
    def load_warehouses(self):
        """Загрузить склады"""
        warehouses = self.warehouses_mgr.get_all()
        self.warehouses_table.setRowCount(0)
        
        if warehouses:
            for row, warehouse in enumerate(warehouses):
                self.warehouses_table.insertRow(row)
                self.warehouses_table.setItem(row, 0, QTableWidgetItem(str(warehouse['warehouse_id'])))
                self.warehouses_table.setItem(row, 1, QTableWidgetItem(warehouse['name']))
                self.warehouses_table.setItem(row, 2, QTableWidgetItem(warehouse['address'] or ""))
                self.warehouses_table.setItem(row, 3, QTableWidgetItem(warehouse['manager'] or ""))
                self.warehouses_table.setItem(row, 4, QTableWidgetItem(warehouse['phone'] or ""))
    
    def create_waybills_tab(self):
        """Вкладка Накладные"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.waybills_table = QTableWidget()
        self.waybills_table.setColumnCount(6)
        self.waybills_table.setHorizontalHeaderLabels(["ID", "Номер", "Дата", "Поставщик", "Склад", "Статус"])
        self.waybills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.waybills_table)
        
        buttons_layout = QHBoxLayout()
        btn_refresh = QPushButton("↻ Обновить")
        btn_refresh.clicked.connect(self.load_waybills)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_waybills()
        return widget
    
    def load_waybills(self):
        """Загрузить накладные"""
        waybills = self.waybills_mgr.get_all()
        self.waybills_table.setRowCount(0)
        
        if waybills:
            for row, waybill in enumerate(waybills):
                self.waybills_table.insertRow(row)
                self.waybills_table.setItem(row, 0, QTableWidgetItem(str(waybill['waybill_id'])))
                self.waybills_table.setItem(row, 1, QTableWidgetItem(waybill['waybill_number']))
                self.waybills_table.setItem(row, 2, QTableWidgetItem(str(waybill['waybill_date'])))
                self.waybills_table.setItem(row, 3, QTableWidgetItem(waybill['supplier_name']))
                self.waybills_table.setItem(row, 4, QTableWidgetItem(waybill['warehouse_name']))
                self.waybills_table.setItem(row, 5, QTableWidgetItem(WAYBILL_STATUSES.get(waybill['status'], waybill['status'])))
    
    def create_invoices_tab(self):
        """Вкладка Счета-фактуры"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels(["ID", "Номер", "Дата", "Покупатель", "Сумма", "Статус"])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.invoices_table)
        
        buttons_layout = QHBoxLayout()
        btn_refresh = QPushButton("↻ Обновить")
        btn_refresh.clicked.connect(self.load_invoices)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_invoices()
        return widget
    
    def load_invoices(self):
        """Загрузить счета-фактуры"""
        invoices = self.invoices_mgr.get_all()
        self.invoices_table.setRowCount(0)
        
        if invoices:
            for row, invoice in enumerate(invoices):
                self.invoices_table.insertRow(row)
                self.invoices_table.setItem(row, 0, QTableWidgetItem(str(invoice['invoice_id'])))
                self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice['invoice_number']))
                self.invoices_table.setItem(row, 2, QTableWidgetItem(str(invoice['invoice_date'])))
                self.invoices_table.setItem(row, 3, QTableWidgetItem(invoice['customer_name']))
                self.invoices_table.setItem(row, 4, QTableWidgetItem(str(invoice['total_amount'] or 0)))
                self.invoices_table.setItem(row, 5, QTableWidgetItem(INVOICE_STATUSES.get(invoice['status'], invoice['status'])))
    
    def create_stock_tab(self):
        """Вкладка Остатки товаров"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(7)
        self.stock_table.setHorizontalHeaderLabels(["Товар", "Артикул", "Склад", "На складе", "Зарезервировано", "Доступно", "Стоимость"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.stock_table)
        
        buttons_layout = QHBoxLayout()
        btn_low = QPushButton("⚠ Низкие остатки")
        btn_refresh = QPushButton("↻ Обновить")
        btn_low.clicked.connect(self.load_low_stock)
        btn_refresh.clicked.connect(self.load_stock)
        buttons_layout.addWidget(btn_low)
        buttons_layout.addWidget(btn_refresh)
        layout.addLayout(buttons_layout)
        
        widget.setLayout(layout)
        self.load_stock()
        return widget
    
    def load_stock(self):
        """Загрузить остатки"""
        stocks = self.stock_mgr.get_all()
        self.stock_table.setRowCount(0)
        
        if stocks:
            for row, stock in enumerate(stocks):
                self.stock_table.insertRow(row)
                self.stock_table.setItem(row, 0, QTableWidgetItem(stock['product_name']))
                self.stock_table.setItem(row, 1, QTableWidgetItem(stock['article']))
                self.stock_table.setItem(row, 2, QTableWidgetItem(stock['warehouse_name']))
                self.stock_table.setItem(row, 3, QTableWidgetItem(str(stock['quantity_in_stock'])))
                self.stock_table.setItem(row, 4, QTableWidgetItem(str(stock['quantity_reserved'])))
                self.stock_table.setItem(row, 5, QTableWidgetItem(str(stock['available'])))
                total_value = stock['available'] * stock.get('sale_price', 0)
                self.stock_table.setItem(row, 6, QTableWidgetItem(f"{total_value:.2f}"))
    
    def load_low_stock(self):
        """Загрузить низкие остатки"""
        stocks = self.stock_mgr.get_low_stock(100)
        self.stock_table.setRowCount(0)
        
        if stocks:
            for row, stock in enumerate(stocks):
                self.stock_table.insertRow(row)
                self.stock_table.setItem(row, 0, QTableWidgetItem(stock['product_name']))
                self.stock_table.setItem(row, 1, QTableWidgetItem(stock['article']))
                self.stock_table.setItem(row, 2, QTableWidgetItem(stock['warehouse_name']))
                self.stock_table.setItem(row, 3, QTableWidgetItem(str(stock['quantity_in_stock'])))
                self.stock_table.setItem(row, 4, QTableWidgetItem(str(stock['quantity_reserved'])))
                self.stock_table.setItem(row, 5, QTableWidgetItem(str(stock['available'])))
        else:
            QMessageBox.information(self, "Информация", "Низких остатков не найдено")
    
    def create_reports_tab(self):
        """Вкладка Отчёты"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("Отчёты (в разработке)")
        label.setFont(QFont("Arial", 14))
        layout.addWidget(label)
        
        buttons_layout = QHBoxLayout()
        btn_sales = QPushButton("📊 Отчёт по продажам")
        btn_purchases = QPushButton("📦 Отчёт по поступлениям")
        btn_stock = QPushButton("📈 Отчёт по остаткам")
        
        btn_sales.clicked.connect(lambda: QMessageBox.information(self, "Info", "Функция в разработке"))
        btn_purchases.clicked.connect(lambda: QMessageBox.information(self, "Info", "Функция в разработке"))
        btn_stock.clicked.connect(lambda: QMessageBox.information(self, "Info", "Функция в разработке"))
        
        buttons_layout.addWidget(btn_sales)
        buttons_layout.addWidget(btn_purchases)
        buttons_layout.addWidget(btn_stock)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def closeEvent(self, event):
        """Закрытие приложения"""
        self.db.disconnect()
        event.accept()


class AddSupplierDialog(QDialog):
    """Диалог добавления/редактирования поставщика"""
    
    def __init__(self, parent=None, supplier=None):
        super().__init__(parent)
        self.setWindowTitle("Поставщик")
        self.supplier = supplier
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.inn_input = QLineEdit()
        self.address_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.contact_input = QLineEdit()
        
        if self.supplier:
            self.name_input.setText(self.supplier['name'])
            self.inn_input.setText(self.supplier['inn'] or "")
            self.address_input.setText(self.supplier['address'] or "")
            self.phone_input.setText(self.supplier['phone'] or "")
            self.email_input.setText(self.supplier['email'] or "")
            self.contact_input.setText(self.supplier['contact_person'] or "")
        
        layout.addRow("Название:", self.name_input)
        layout.addRow("ИНН:", self.inn_input)
        layout.addRow("Адрес:", self.address_input)
        layout.addRow("Телефон:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Контактное лицо:", self.contact_input)
        
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Отмена")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        self.setLayout(layout)
    
    def get_data(self):
        return (
            self.name_input.text(),
            self.inn_input.text(),
            self.address_input.text(),
            self.phone_input.text(),
            self.email_input.text(),
            self.contact_input.text()
        )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
