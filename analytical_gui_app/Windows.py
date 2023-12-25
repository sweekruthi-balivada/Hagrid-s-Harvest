import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTextEdit, QTableWidget, QTableWidgetItem, QPlainTextEdit, QLabel, QPushButton, QDialogButtonBox
from DATA225utils import make_connection
from PyQt5.QtGui import QPixmap
import re
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import calendar

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


class BasicWindowWithTable(QDialog):
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


class BasicWindow(QDialog):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        self.ui = None
    
    def show_window(self):
        """
        Show this dialog.
        """
        if self.ui != None:
            self.ui.show()


class TrySQLQueryWindow(BasicWindowWithTable):
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
        self.ui = uic.loadUi('display_ss.ui')

        file_name = 'ss.png'
        if os.path.isfile(file_name):
            pixmap = QPixmap(file_name)
            self.ui.display.setPixmap(pixmap)
            self.ui.display.resize(pixmap.width(), pixmap.height())
        else:
            print("Error loading RS image")


class MarketingSegmentationWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('marketing_segmentation.ui')
        self.initialize_state_menu()
        self.initialize_graph()
        self.initialize_graph2()
        self.ui.stateMenu.currentIndexChanged.connect(self.create_graph_for_state)

    def initialize_state_menu(self):
        sql = """
            SELECT DISTINCT state
            FROM Customer_Address_D
            ORDER BY State;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            state = str(row[0])
            self.ui.stateMenu.addItem(state, row)

    def initialize_graph(self):
        children = []
        for i in range(self.ui.graph_layout.count()):
            child = self.ui.graph_layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
        self.ui.graph_layout.addWidget(FigureCanvas(plt.figure()))
        
        sql = """
            SELECT State, COUNT(*) AS NumberOfCustomers
            FROM Customer_Address_D
            GROUP BY State
            LIMIT 35;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        states, nums = [], []
        for row in rows:
            state, num = row[0], row[1]
            states.append(state)
            nums.append(num)
        plt.bar(states, nums, label='Number of customers')        
        title = (f'State wise distribution')
        plt.title(title)
        plt.xlabel('State')
        plt.ylabel('Number of customer')
        plt.legend()
        plt.xticks(rotation='vertical')
        plt.close()

    def initialize_graph2(self):
        children = []
        for i in range(self.ui.graph_layout_2.count()):
            child = self.ui.graph_layout_2.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()

    def create_graph_for_state(self):
        state = self.ui.stateMenu.currentData()[0]
        self.initialize_graph2()
        self.ui.graph_layout_2.addWidget(FigureCanvas(plt.figure()))
        sql = f"""
            SELECT City, COUNT(*) AS NumberOfCustomers
            FROM Customer_Address_D
            WHERE State = '{state}'
            GROUP BY City
            LIMIT 35;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        states, nums = [], []
        for row in rows:
            state, num = row[0], row[1]
            states.append(state)
            nums.append(num)
        plt.bar(states, nums, label='Number of customers')        
        title = (f'City wise distribution')
        plt.title(title)
        plt.xlabel('City')
        plt.ylabel('Number of customer')
        plt.legend()
        plt.xticks(rotation='vertical')
        plt.close()
        

class AssociationRuleMiningWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('association_rule_mining.ui')
        self.initialize_menus()
        self.initialize_graph()
        self.initialize_graph2()
        self.ui.categoryMenu.currentIndexChanged.connect(self.create_pie_chart_for_inventory)
        self.ui.stateMenu.currentIndexChanged.connect(self.create_pie_chart_for_customer)

    def initialize_menus(self):
        sql = """
            SELECT DISTINCT CategoryName
            FROM Product_D;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            state = str(row[0])
            self.ui.categoryMenu.addItem(state, row)
        
        sql = """
            SELECT DISTINCT state
            FROM Customer_Address_D
            ORDER BY State;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            state = str(row[0])
            self.ui.stateMenu.addItem(state, row)
    
    def initialize_graph(self):
        children = []
        for i in range(self.ui.graph_layout.count()):
            child = self.ui.graph_layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
    
    def initialize_graph2(self):
        children = []
        for i in range(self.ui.graph_layout_2.count()):
            child = self.ui.graph_layout_2.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()

    def create_pie_chart_for_inventory(self):
        category = self.ui.categoryMenu.currentData()[0]
        self.initialize_graph()
        self.ui.graph_layout.addWidget(FigureCanvas(plt.figure()))

        sql = f"""
            SELECT count(*), InStock
            FROM Product_D
            WHERE CategoryName = '{category}'
            GROUP BY InStock
            ORDER BY InStock;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        counts, stocks = [], ["Out of Stock", "In Stock"]
        for row in rows:
            count, inStock = row[0], row[1]
            counts.append(count)
        plt.pie(counts, labels=stocks, autopct='%1.1f%%')
        title = (f'Inventory Analysis for category: {category}')
        plt.title(title)
        plt.legend()
        plt.close()
    
    def create_pie_chart_for_customer(self):
        state = self.ui.stateMenu.currentData()[0]
        self.initialize_graph2()
        self.ui.graph_layout_2.addWidget(FigureCanvas(plt.figure()))

        sql = f"""
            SELECT
                COUNT(DISTINCT CASE WHEN orders_count = 1 THEN c.CustomerId END) AS customers_with_1_order,
                COUNT(DISTINCT CASE WHEN orders_count > 1 THEN c.CustomerId END) AS customers_with_more_than_1_order
            FROM
                Customer_D AS c
                INNER JOIN (
                    SELECT
                        CustomerId,
                        COUNT(*) AS orders_count
                    FROM
                        Sales AS s
                        INNER JOIN Order_D AS o ON s.OrderId = o.OrderId
                        INNER JOIN Customer_Address_D AS ca ON s.AddressId = ca.AddressId
                    WHERE
                        ca.State = '{state}'
                    GROUP BY
                        CustomerId
                ) AS so ON c.CustomerId = so.CustomerId;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        customers = []
        customers.append(rows[0][0])
        customers.append(rows[0][1])
        labels = ["New Customers", "Returning Customers"]
        plt.pie(customers, labels=labels, autopct='%1.1f%%')
        title = (f'New vs Returning Customer for state: {state}')
        plt.title(title)
        plt.legend()
        plt.close()


class TimeSeriesAnalysisWindow(BasicWindow):
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        # Load the dialog components.
        self.ui = uic.loadUi('time_series_analysis.ui')
        self.initialize_menus()
        self.initialize_graph()
        self.initialize_graph2()
        self.ui.yearMenu.currentIndexChanged.connect(self.create_graph_for_total_sales)
        self.ui.categoryMenu.currentIndexChanged.connect(self.create_graph_for_category)

    def initialize_menus(self):
        sql = """
            SELECT DISTINCT CategoryName
            FROM Product_D;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            state = str(row[0])
            self.ui.categoryMenu.addItem(state, row)
        
        sql = """
            SELECT DISTINCT YEAR(OrderDate) 
            FROM Order_D
            ORDER BY YEAR(OrderDate) ASC;
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        for row in rows:
            state = str(row[0])
            self.ui.yearMenu.addItem(state, row)

    def initialize_graph(self):
        children = []
        for i in range(self.ui.graph_layout.count()):
            child = self.ui.graph_layout.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
    
    def initialize_graph2(self):
        children = []
        for i in range(self.ui.graph_layout_2.count()):
            child = self.ui.graph_layout_2.itemAt(i).widget()
            if child:
                children.append(child)
        for child in children:
            child.deleteLater()
    
    def create_graph_for_total_sales(self):
        year = self.ui.yearMenu.currentData()[0]
        self.initialize_graph()
        self.initialize_graph2()
        self.ui.graph_layout.addWidget(FigureCanvas(plt.figure()))
        
        sql = f"""
            SELECT
                MONTH(o.OrderDate) AS Month,
                SUM(s.Amount) AS TotalSales
            FROM
                Order_D AS o
                INNER JOIN Sales AS s ON o.OrderId = s.OrderId
            WHERE YEAR(o.OrderDate) = {year}
            GROUP BY MONTH(o.OrderDate)
            ORDER BY MONTH(o.OrderDate);
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        months, sales = [], []
        for row in rows:
            month, sale = row[0], row[1]
            month_name = calendar.month_name[month]
            months.append(month_name)
            sales.append(sale)
        plt.plot(months, sales, label='Sales in USD')
        title = (f'Total Sales by Month for {year}')
        plt.title(title)
        plt.xlabel('Sales')
        plt.ylabel('Month')
        plt.legend()
        plt.xticks(rotation='vertical')
        plt.close()

    def create_graph_for_category(self):
        category = self.ui.categoryMenu.currentData()[0]
        year = self.ui.yearMenu.currentData()[0]
        self.initialize_graph2()
        self.ui.graph_layout_2.addWidget(FigureCanvas(plt.figure()))
        sql = f"""
            SELECT
                MONTH(o.OrderDate) AS Month,
                SUM(s.Amount) AS TotalSales
            FROM
                Order_D AS o
                INNER JOIN Sales AS s ON o.OrderId = s.OrderId
                INNER JOIN Product_D AS p ON s.ProductId = p.ProductId
            WHERE
                YEAR(o.OrderDate) = {year}
                AND p.CategoryName = '{category}'
            GROUP BY MONTH(o.OrderDate)
            ORDER BY MONTH(o.OrderDate);
            """
        rows, num_rows, num_cols, col_names = runSQL(sql)
        months, sales = [], []
        for row in rows:
            month, sale = row[0], row[1]
            month_name = calendar.month_name[month]
            months.append(month_name)
            sales.append(sale)
        plt.plot(months, sales, label='Sales in USD')
        title = (f'Total Sales by Month for {year} and category: {category}')
        plt.title(title)
        plt.xlabel('Sales')
        plt.ylabel('Month')
        plt.legend()
        plt.xticks(rotation='vertical')
        plt.close()
