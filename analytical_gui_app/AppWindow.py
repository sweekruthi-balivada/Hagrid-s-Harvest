from PyQt5 import uic
from PyQt5.QtGui import QWindow, QPixmap, QImage
import os
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QTableWidget
from Windows import TrySQLQueryWindow, DisplayRSWindow, MarketingSegmentationWindow,\
AssociationRuleMiningWindow, TimeSeriesAnalysisWindow

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
        self.display_ss = DisplayRSWindow()
        self.ui.display_ss_button.clicked.connect(self.show_display_ss_window)

        # MarketingSegmentationWindow
        self.marketing_segmentation = MarketingSegmentationWindow()
        self.ui.marketing_segmentation_button.clicked.connect(self.show_marketing_segmentation_window)

        # AssociationRuleMiningWindow
        self.association_rule_mining = AssociationRuleMiningWindow()
        self.ui.association_rule_mining_button.clicked.connect(self.show_association_rule_mining_window)

        # TimeSeriesAnalysisWindow
        self.time_series = TimeSeriesAnalysisWindow()
        self.ui.time_series_button.clicked.connect(self.show_time_series_window)

    def show_try_sql_query_window(self):
        """
        Show the TrySQLQuery window
        """
        self.try_sql_query.show_window()

    def show_display_ss_window(self):
        """
        Show the DisplayRSWindow
        """
        self.display_ss.show_window()

    def show_marketing_segmentation_window(self):
        """
        Show the MarketingSegmentationWindow
        """
        self.marketing_segmentation.show_window()

    def show_association_rule_mining_window(self):
        """
        Show the AssociationRuleMiningWindow
        """
        self.association_rule_mining.show_window()

    def show_time_series_window(self):
        """
        Show the TimeSeriesAnalysisWindow
        """
        self.time_series.show_window()
