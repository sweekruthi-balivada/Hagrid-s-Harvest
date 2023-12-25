import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTextEdit, QTableWidget, QTableWidgetItem, QPlainTextEdit, QLabel, QPushButton, QDialogButtonBox
from DATA225utils import make_connection
from PyQt5.QtGui import QPixmap
import re

CONN = 'remote.ini'

def runSQL(sql):
    try:
        conn = make_connection(config_file = CONN)
        cursor = conn.cursor()
        cursor.execute(sql)
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        num_rows = len(rows)
        num_cols = len(rows[0]) if rows else 0
    except Exception as e:
        rows, col_names = [], []
        num_rows, num_cols = 0, 0
    finally:
        cursor.close()
        conn.close()
        return rows, num_rows, num_cols, col_names

def runSQLCatchError(sql):
    try:
        conn = make_connection(config_file = CONN)
        cursor = conn.cursor()
        cursor.execute(sql)
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        num_rows = len(rows)
        num_cols = len(rows[0]) if rows else 0
    except Exception as e:
        rows, col_names = [], [e]
        num_rows, num_cols = 0, 0
    finally:
        cursor.close()
        conn.close()
    return rows, num_rows, num_cols, col_names

def insertSQL(sql, data):
    result = 0
    try:
        conn = make_connection(config_file = CONN)
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        result = 1
    except Exception as e:
        pass
    finally:
        cursor.close()
        conn.close()
    return result

def updateSQL(sql):
    result = 0
    try:
        conn = make_connection(config_file = CONN)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        result = 1
    except Exception as e:
        pass
    finally:
        cursor.close()
        conn.close()
    return result

def runSP(sp_name, input_param_list):
    try:
        conn = make_connection(config_file = CONN)
        cursor = conn.cursor()
        cursor.callproc(sp_name, input_param_list)
        rows = []
        for result in cursor.stored_results():
            output = result.fetchall()
            for row in output:
                rows.append(row)
        col_names = [desc[0] for desc in cursor.description]
        num_rows = len(rows)
        num_cols = len(rows[0]) if rows else 0
    except Exception as e:
        rows, col_names = [], []
        num_rows, num_cols = 0, 0
    finally:
        cursor.close()
        conn.close()
    return rows, num_rows, num_cols, col_names


class BasicWindow(QDialog):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        self.ui = None
        self.display_table = None
    
    def show_window(self):
        """
        Show this dialog.
        """
        if self.ui != None:
            self.ui.show()

    def initialize_display_table(self):
        """
        Init display table.
        """
        if self.display_table != None:
            self.display_table.clear()
    
    def populate_display_table(self, num_rows, num_cols, col_names, rows):
        """
        Populate display table with rows.
        """
        if self.display_table == None:
            return
        self.display_table.clear()
        self.display_table.setRowCount(num_rows)
        self.display_table.setColumnCount(num_cols)
        self.display_table.setHorizontalHeaderLabels(col_names)
        row_index = 0
        for row in rows:
            column_index = 0
            for data in row:
                item = QTableWidgetItem(str(data))
                self.display_table.setItem(row_index, column_index, item)
                column_index += 1
            row_index += 1
        self.display_table.resizeColumnsToContents()
    
    def populate_display_table_with_edit(self, num_rows, num_cols, col_names, rows):
        """
        Populate display table with rows and a edit button column.
        """
        if self.display_table == None:
            return
        col_names.append("Update")
        num_cols += 1
        self.display_table.clear()
        self.display_table.setRowCount(num_rows)
        self.display_table.setColumnCount(num_cols)
        self.display_table.setHorizontalHeaderLabels(col_names)
        row_index = 0
        for row in rows:
            column_index = 0
            for data in row:
                item = QTableWidgetItem(str(data))
                self.display_table.setItem(row_index, column_index, item)
                column_index += 1
            editButton = QPushButton("Update")
            editButton.clicked.connect(self.editItem)
            self.display_table.setCellWidget(row_index, column_index, editButton)
            row_index += 1
        self.display_table.resizeColumnsToContents()

    def editItem(self):
        """
        Must be implemented in child class if populate_display_table_with_edit is used
        """
        pass


class TrySQLQueryWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('try_sql_query.ui')

        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)

        self.ui.query_button.clicked.connect(self.run_sql_query)
        self.ui.clear_button.clicked.connect(self.clear_text_box)
        self.initialize_display_table()
        
    def is_valid_read_query(self, query):
        # Regular expression to match insert, update, and delete statements
        iud_pattern = r'^\s*(INSERT|UPDATE|DELETE)\s+.*\s*$'

        # Check if the query does not match the iud pattern
        if not re.match(iud_pattern, query, re.IGNORECASE):
            return True
        return False

    def run_sql_query(self):
        sql_text_box = self.ui.findChild(QTextEdit, 'sql_text_box')
        text_input = sql_text_box.toPlainText()
        result_box = self.ui.findChild(QTextEdit, 'result_box')
        result_box.setReadOnly(False)
        if not self.is_valid_read_query(text_input):
            result_box.setPlaceholderText("ERROR - Query is not valid, Please run read only queries.")
            return
        sql = text_input
        self.display_table.clear()
        rows, num_rows, num_cols, col_names = runSQLCatchError(sql)
        
        if isinstance(col_names[0], Exception):
            result_box_text = f"ERROR - {str(col_names[0])}"
        else:
            result_box_text = f"OUTPUT - {num_rows} row(s) returned having {num_cols} column(s)"
        result_box.setPlaceholderText(result_box_text)
            
        if isinstance(col_names[0], Exception):
            return

        self.populate_display_table(num_rows, num_cols, col_names, rows)

    def clear_text_box(self):
        self.ui.findChild(QTextEdit, 'sql_text_box').clear()


class DisplayRSWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('display_rs.ui')

        file_name = 'rs.png'
        if os.path.isfile(file_name):
            pixmap = QPixmap(file_name)
            self.ui.display.setPixmap(pixmap)
            self.ui.display.resize(pixmap.width(), pixmap.height())
        else:
            print("Error loading RS image")


class ProductInsightsWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('product_insights.ui')
        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)
        self.initialize_display_table()
        self.ui.numProductsInCategory.toggled.connect(self.onCategoryButtonToggled)
        self.ui.mostPopularProducts.toggled.connect(self.onCategoryButtonToggled)
        self.ui.productInfoSubCategoryButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.categoryMenu.currentIndexChanged.connect(self.initialize_display_table_with_category_menu)
        self.hmap = {}
        self.ui.categoryButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.subcategoryButton.toggled.connect(self.onCategoryButtonToggled)
        self.initialize_category_menu()
        self.ui.productPriceSlider.valueChanged.connect(self.on_slider_value_changed)
        self.slider_label = self.ui.findChild(QLabel, "label_5")
        self.slider_label.setText(str(self.ui.productPriceSlider.value()))

    def onCategoryButtonToggled(self):
        if self.ui.categoryButton.isChecked():
            sql = ("SELECT Name AS 'Category Name' FROM Category")
        elif self.ui.subcategoryButton.isChecked():
            sql = ("SELECT Name AS 'Sub-Category Name' FROM Sub_Category")
        elif self.ui.numProductsInCategory.isChecked():
            sql = (f"""
            SELECT Category.Name AS 'Category Name', count(*) AS 'Number of Products'
            FROM Products, Category
            WHERE Products.CategoryId = Category.Id
            GROUP BY CategoryId;
            """)
        elif self.ui.mostPopularProducts.isChecked():
            sql = (f"""
            SELECT p.ProductName AS ProductName, COUNT(*) AS TimesOrdered
            FROM Products p
            JOIN Order_Details od ON p.ProductId = od.ProductId
            GROUP BY p.ProductName
            ORDER BY TimesOrdered DESC
            LIMIT 10;
            """)
        elif self.ui.productInfoSubCategoryButton.isChecked():
            category = self.ui.categoryMenu.currentData()[0]
            cid = self.hmap[category]
            rows, num_rows, num_cols, col_names = runSP("SubCategoryInCategoryWithProductsInfo", [cid])
            col_names = ["Category ID", "Category Name", "Num Of Products", "Average Product Price"]
            self.populate_display_table(num_rows, num_cols, col_names, rows)
            return
        else:
            return

        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)
    
    def on_slider_value_changed(self, value):
        self.ui.label_5.setText(str(value))
        sql = (f"""
            SELECT *
            FROM Products
            WHERE ProductPrice < {value}
            LIMIT 1000;
            """)
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)

    def initialize_display_table_with_category_menu(self):
        self.display_table.clear()
        self.onCategoryButtonToggled()
    
    def initialize_category_menu(self):
        sql = """
            SELECT Name
            FROM Category
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        row_index = 1
        for row in rows:
            category = str(row[0])
            self.ui.categoryMenu.addItem(category, row)
            self.hmap[category] = row_index
            row_index += 1


class CustomerInsightsWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('customer_insights.ui')
        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)
        self.initialize_display_table()

        self.ui.topCustomerButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.orderPaymentModeButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.monthSpinBox.valueChanged.connect(self.on_spin_box_value_changed)
        self.ui.customerLifetimeValueButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.top10salesButton.toggled.connect(self.onCategoryButtonToggled)
        self.ui.customerLocationOrderFreqButton.toggled.connect(self.onCategoryButtonToggled)

        self.ui.paymentModeMenu.currentIndexChanged.connect(self.initialize_display_table_with_menu)
        self.initialize_payment_mode_menu()
        self.ui.customerMenu.currentIndexChanged.connect(self.initialize_display_table_with_menu)
        self.initialize_customer_menu()
    
    def onCategoryButtonToggled(self):
        if self.ui.topCustomerButton.isChecked():
            sql = (f"""
            SELECT CONCAT(FirstName, ' ', LastName) AS 'FullName', count(OrderId) AS 'TotalOrders' FROM Orders, Customer
            WHERE Orders.customerId = Customer.CustomerId
            GROUP BY Orders.customerId
            ORDER BY count(OrderId) DESC
            LIMIT 10;
            """)
        elif self.ui.orderPaymentModeButton.isChecked():
            payment_mode = self.ui.paymentModeMenu.currentData()[0]
            sql = (f"""
            SELECT count(*) AS 'Payment Mode Usage Count'
            FROM Payment
            WHERE PaymentMode = '{payment_mode}';
            """)
        elif self.ui.customerLifetimeValueButton.isChecked():
            sql = (f"""
            SELECT *
            FROM CustomerLifetimeValue;
            """)
        elif self.ui.top10salesButton.isChecked():
            sql = """
            SELECT ca.State, SUM(p.ProductPrice * od.Quantity) as TotalSales
            FROM Customer_Address ca
            JOIN Customer c ON ca.CustomerId = c.CustomerId
            JOIN Orders o ON c.CustomerId = o.CustomerId
            JOIN Order_Details od ON o.OrderId = od.OrderId
            JOIN Products p ON od.ProductId = p.ProductId
            GROUP BY ca.State
            ORDER BY TotalSales DESC
            LIMIT 10;            
            """
        elif self.ui.customerLocationOrderFreqButton.isChecked():
            sql = """
            SELECT * FROM CustomerLocationOrderFrequency
            """
        elif self.ui.customerOrderButton.isChecked():
            cust_id = self.ui.customerMenu.currentData()[2]
            rows, num_rows, num_cols, col_names = runSP("GetOrderHistoryForCustomer", [cust_id])
            col_names = ["Order ID", "Order Date", "Product Name", "Quantity", "Product Price", "Order Total"]
            self.populate_display_table(num_rows, num_cols, col_names, rows)
            return
        else:
            return

        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)
    
    def on_spin_box_value_changed(self, value):
        sql = (f"""
            SELECT DATE_FORMAT(OrderDate, '%m') AS Month, ROUND(SUM(Payment.Amount), 2) AS 'TotalRevenue (in USD)'
            FROM Orders
            INNER JOIN Payment ON Orders.OrderId = Payment.OrderId
            WHERE DATE_FORMAT(OrderDate, '%m') = {value}
            GROUP BY Month;
            """)
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)

    def initialize_display_table_with_menu(self):
        """
        Clear the display table.
        """
        self.display_table.clear()
        self.onCategoryButtonToggled()
    
    def initialize_payment_mode_menu(self):
        sql = """
            SELECT DISTINCT PaymentMode
            FROM Payment
            ORDER BY PaymentMode;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            self.ui.paymentModeMenu.addItem(str(row[0]), row)

    def initialize_customer_menu(self):
        sql = """
            SELECT DISTINCT FirstName, LastName, Customer.CustomerId
            FROM Customer, Orders
            WHERE Customer.CustomerId = Orders.CustomerId;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            full_name = str(row[0] + " " + row[1])
            self.ui.customerMenu.addItem(full_name, row)


class AdminCategoryWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('admin_category.ui')

        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)

        self.initialize_display_table()
        self.ui.submit_button.clicked.connect(self.insert_category)
        self.ui.cancel_button.clicked.connect(self.clear_input_text)
        self.update_category_obj = None

    def initialize_display_table(self):
        sql = ("SELECT Id, Name AS 'Category Name' FROM Category")
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table_with_edit(num_rows, num_cols, col_names, rows)
        self.last_id = len(rows) + 1
    
    def insert_category(self):
        new_category = self.ui.findChild(QPlainTextEdit, 'input_text').toPlainText()
        sql = "INSERT INTO Category VALUES (%s, %s)"
        data = (self.last_id, new_category)
        if insertSQL(sql, data) == 1:
            self.initialize_display_table()
            self.clear_input_text()
            self.ui.close()    
    
    def clear_input_text(self):
        self.ui.findChild(QPlainTextEdit, 'input_text').clear()
    
    def editItem(self):
        button = self.sender()
        index = self.display_table.indexAt(button.pos())
        row = index.row()
        column = 0
        item = self.display_table.item(row, column)
        cat_id = item.text()
        self.update_category_obj = UpdateCategoryWindow(cat_id, self)
        self.update_category_obj.ui.show()


class UpdateCategoryWindow(BasicWindow):
    def __init__(self, cat_id, edit_cat_window_obj):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        self.cat_id = int(cat_id)
        self.edit_cat_window_obj = edit_cat_window_obj
        # Load the dialog components.
        self.ui = uic.loadUi('update_category.ui')

        self.ui.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.update_category)
        self.ui.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.cancel_update)
        self.ui.label.setText(f"Category ID : {self.cat_id}")
        sql = f"""
        SELECT Name FROM Category
        where Id = {self.cat_id};
        """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.ui.textEdit.setText(rows[0][0])
    
    def update_category(self):
        sql = f"""
        UPDATE Category
        SET Name = '{self.ui.textEdit.toPlainText()}'
        WHERE Id = {self.cat_id};
        """
        result = updateSQL(sql)
        self.edit_cat_window_obj.initialize_display_table()
        self.ui.close()

    def cancel_update(self):
        self.ui.close()


class AdminSubCategoryWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('admin_sub_category.ui')

        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)
        self.initialize_display_table()
        self.ui.submit_button.clicked.connect(self.insert_sub_category)
        self.ui.cancel_button.clicked.connect(self.clear_input_text)
        self.update_sub_category_obj = None

    def initialize_display_table(self):
        sql = ("SELECT Id, Name AS 'Sub-Category Name' FROM Sub_Category")
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table_with_edit(num_rows, num_cols, col_names, rows)
        self.last_id = len(rows) + 1

    def insert_sub_category(self):
        new_sub_category = self.ui.findChild(QPlainTextEdit, 'input_text').toPlainText()
        sql = "INSERT INTO Sub_Category VALUES (%s, %s)"
        data = (self.last_id, new_sub_category)
        if insertSQL(sql, data) == 1:
            self.initialize_display_table()
            self.clear_input_text()
            self.ui.close()
    
    def clear_input_text(self):
        self.ui.findChild(QPlainTextEdit, 'input_text').clear()

    def editItem(self):
        button = self.sender()
        index = self.display_table.indexAt(button.pos())
        row = index.row()
        column = 0
        item = self.display_table.item(row, column)
        sub_cat_id = item.text()
        self.update_sub_category_obj = UpdateSubCategoryWindow(sub_cat_id, self)
        self.update_sub_category_obj.ui.show()


class UpdateSubCategoryWindow(BasicWindow):
    def __init__(self, sub_cat_id, edit_sub_cat_window_obj):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        self.sub_cat_id = int(sub_cat_id)
        self.edit_sub_cat_window_obj = edit_sub_cat_window_obj

        # Load the dialog components.
        self.ui = uic.loadUi('update_sub_category.ui')

        self.ui.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.update_sub_category)
        self.ui.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.cancel_update)
        self.ui.label.setText(f"Sub-Category ID : {self.sub_cat_id}")
        sql = f"""
        SELECT Name FROM Sub_Category
        where Id = {self.sub_cat_id};
        """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.ui.textEdit.setText(rows[0][0])
    
    def update_sub_category(self):
        sql = f"""
        UPDATE Sub_Category
        SET Name = '{self.ui.textEdit.toPlainText()}'
        WHERE Id = {self.sub_cat_id};
        """
        result = updateSQL(sql)
        self.edit_sub_cat_window_obj.initialize_display_table()
        self.ui.close()

    def cancel_update(self):
        self.ui.close()


class AdminProductsWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('admin_products.ui')

        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)
        self.initialize_display_table()
        self.ui.submit_button.clicked.connect(self.insert_products)
        self.ui.cancel_button.clicked.connect(self.clear_input_text)
        self.cat_hmap = {}
        self.subcat_hmap = {}
        self.initialize_menus()

    def initialize_display_table(self):
        sql = '''
                SELECT ProductId, ProductName, ProductPrice, InStock, Category.Name AS CategoryName, Sub_Category.Name AS SubCategoryName
                FROM Products, Category, Sub_Category
                WHERE Category.Id = Products.CategoryId
                AND Sub_Category.Id = Products.SubCategoryId
                ORDER BY ProductId;
              '''
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)
        self.last_id = len(rows) + 1
    
    def initialize_menus(self):
        sql = """
            SELECT Name
            FROM Category
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        row_index = 1
        for row in rows:
            category = str(row[0])
            self.ui.categoryMenu.addItem(category, row)
            self.cat_hmap[category] = row_index
            row_index += 1
        
        sql = """
            SELECT Name
            FROM Sub_Category
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        row_index = 1
        for row in rows:
            category = str(row[0])
            self.ui.subcategoryMenu.addItem(category, row)
            self.subcat_hmap[category] = row_index
            row_index += 1

    def insert_products(self):
        product = self.ui.findChild(QPlainTextEdit, 'input_text').toPlainText()
        price = float(self.ui.findChild(QPlainTextEdit, 'input_text_2').toPlainText())
        instock = self.ui.inStock.isChecked()
        category = self.ui.categoryMenu.currentData()[0]
        cid = self.cat_hmap[category]
        sub_category = self.ui.subcategoryMenu.currentData()[0]
        subcid = self.subcat_hmap[sub_category]
        sql = "INSERT INTO Products VALUES (%s, %s, %s, %s, %s, %s)"
        data = (self.last_id, product, price, instock, subcid, cid)
        if insertSQL(sql, data) == 1:
            self.initialize_display_table()
            self.clear_input_text()
            self.ui.close()    
    
    def clear_input_text(self):
        self.ui.findChild(QPlainTextEdit, 'input_text').clear()
        self.ui.findChild(QPlainTextEdit, 'input_text_2').clear()


class AdminOrdersWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('admin_orders.ui')

        self.display_table = self.ui.scrollArea.findChild(QTableWidget, "display_table")
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setWidget(self.display_table)
        self.initialize_display_table()

    def initialize_display_table(self):
        sql = '''
                SELECT Orders.OrderId, OrderDate, Orders.CustomerId, PaymentId, FirstName, LastName, Amount, PaymentMode
                FROM Orders, Payment, Customer
                WHERE Orders.OrderId = Payment.OrderId
                AND Orders.CustomerId = Customer.CustomerId;
              '''
        rows, num_rows, num_cols, col_names = runSQL(sql)
        self.populate_display_table(num_rows, num_cols, col_names, rows)
        self.last_id = len(rows) + 1


class AdminPanelWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('admin_panel.ui')

        # AdminCategory window
        self.admin_category = AdminCategoryWindow()
        self.ui.admin_category_button.clicked.connect(self.show_admin_category_window)

        # AdminSubCategory window
        self.admin_sub_category = AdminSubCategoryWindow()
        self.ui.admin_sub_category_button.clicked.connect(self.show_admin_sub_category_window)

        # AdminProducts window
        self.admin_products = AdminProductsWindow()
        self.ui.admin_product_button.clicked.connect(self.show_admin_products_window)

        # AdminOrdersWindow window
        self.admin_orders = AdminOrdersWindow()
        self.ui.admin_order_button.clicked.connect(self.show_admin_orders_window)
    
    def show_admin_category_window(self):
        """
        Show the AdminCategory
        """
        self.admin_category.show_window()

    def show_admin_sub_category_window(self):
        """
        Show the AdminSubCategory
        """
        self.admin_sub_category.show_window()
    
    def show_admin_products_window(self):
        """
        Show the AdminProductsWindow
        """
        self.admin_products.show_window()
    
    def show_admin_orders_window(self):
        """
        Show the AdminOrdersWindow
        """
        self.admin_orders.show_window()
