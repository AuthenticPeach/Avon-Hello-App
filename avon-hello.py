import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from customers_window import CustomersWindow  # Importing the Customers Window
from options_window import OptionsWindow  # Importing the Options Window

DB_PATH = "avon_hello.db"  # Default database location

class MainMenu(QMainWindow):
    """Main Menu for Avon Hello."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avon Hello - Main Menu")
        self.setGeometry(200, 200, 600, 400)  # Window size
        
        # Create Main Menu UI
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Header Label
        title_label = QLabel("Main Menu", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: blue; color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Database Info
        self.db_label = QLabel(f"Current Database File:\n{DB_PATH}", self)
        self.db_label.setStyleSheet("background-color: yellow; padding: 5px;")
        self.db_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.db_label)

        # Buttons for Customers and Options
        btn_customers = QPushButton("Customers")
        btn_customers.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_customers.clicked.connect(self.open_customers)

        btn_options = QPushButton("Options")
        btn_options.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_options.clicked.connect(self.open_options)

        layout.addWidget(btn_customers)
        layout.addWidget(btn_options)

        # Exit Button
        btn_exit = QPushButton("Exit")
        btn_exit.setStyleSheet("background-color: red; font-size: 16px; padding: 10px;")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_customers(self):
        """Opens the Customers Management Window."""
        self.customers_window = CustomersWindow()
        self.customers_window.show()

    def open_options(self):
        """Opens the Options Window."""
        self.options_window = OptionsWindow()
        self.options_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
