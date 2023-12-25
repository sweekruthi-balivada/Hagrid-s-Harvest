from PyQt5 import uic
from PyQt5.QtGui import QWindow, QPixmap, QImage
import os
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QTableWidget
from Windows import TrySQLQueryWindow, DisplayRSWindow, ProductInsightsWindow,\
CustomerInsightsWindow, AdminPanelWindow, runSQL

'''
edit and delete category, sub, products, orders left
'''

class AppWindow(QWindow):
    """
    The main application window.
    """
    
    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()
        
        self.ui = uic.loadUi('gui_app.ui')
        self.ui.show()

        #file_name = 'main.png'
        # image = QImage(file_name)
        # if os.path.isfile(file_name):
           # pixmap = QPixmap(file_name)
           # pixmap.convertFromImage(image.scaled(pixmap.width(), pixmap.height()))
           # self.ui.display.setPixmap(pixmap)
        #else:
           # print("Error loading RS image")

        # TrySQLQuery window
        self.try_sql_query = TrySQLQueryWindow()
        self.ui.try_sql_query_button.clicked.connect(self.show_try_sql_query_window)

        # DisplayRSWindow
        self.display_rs = DisplayRSWindow()
        self.ui.display_rs_button.clicked.connect(self.show_display_rs_window)

        # ProductInsightsWindow
        self.product_insights = ProductInsightsWindow()
        self.ui.products_insights_button.clicked.connect(self.show_product_insights_window)

        # CustomerInsightsWindow
        self.customer_insights = CustomerInsightsWindow()
        self.ui.customer_insights_button.clicked.connect(self.show_customer_insights_window)

        # AdminPanelWindow
        self.admin_panel = AdminPanelWindow()
        self.ui.admin_panel_button.clicked.connect(self.show_admin_panel_window)

    def show_try_sql_query_window(self):
        """
        Show the TrySQLQuery window
        """
        self.try_sql_query.show_window()

    def show_display_rs_window(self):
        """
        Show the DisplayRSWindow
        """
        self.display_rs.show_window()

    def show_product_insights_window(self):
        """
        Show the ProductInsightsWindow
        """
        self.product_insights.show_window()

    def show_customer_insights_window(self):
        """
        Show the CustomerInsightsWindow
        """
        self.customer_insights.show_window()

    def show_admin_panel_window(self):
        """
        Show the AdminPanelWindow
        """
        self.admin_panel.show_window()
