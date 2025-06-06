import sys
import sqlite3
import configparser
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QVBoxLayout, QWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from customers_window import CustomersWindow  # Importing the Customers Window
from options_window import OptionsWindow  # Importing the Options Window
from pathlib import Path
import traceback

from config import DB_PATH, SETTINGS_FILE, LOG_FILE
from db_utils import initialize_database


# === CONFIGURATION ===
APP_NAME = "AvonHello"
APPDATA_PATH = Path(os.getenv("APPDATA")) / APP_NAME
APPDATA_PATH.mkdir(parents=True, exist_ok=True)


# === GLOBAL EXCEPTION HANDLER ===
def log_uncaught_exceptions(ex_cls, ex, tb):
    with open(LOG_FILE, "w") as f:
        traceback.print_exception(ex_cls, ex, tb, file=f)
    sys.__excepthook__(ex_cls, ex, tb)

sys.excepthook = log_uncaught_exceptions


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def is_dark_mode_enabled():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        return config.getboolean("Appearance", "dark_mode", fallback=False)
    return False

class MainMenu(QMainWindow):
    """Main Menu for Avon Hello."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avon Hello - Main Menu")
        self.setGeometry(200, 200, 600, 400)
        icon_path = resource_path("Avon256.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Set global font
        self.setFont(QFont("Segoe UI", 10))

        # Apply global stylesheet
        if is_dark_mode_enabled():
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #121212;
                }

                QLabel#titleLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    background-color: #2f80ed;
                    padding: 12px;
                }

                QLabel#dbLabel {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    padding: 8px;
                    color: #e0e0e0;
                    font-weight: 500;
                }

                QPushButton {
                    background-color: #3a3f44;
                    color: white;
                    padding: 10px;
                    font-size: 16px;
                    border: 1px solid #555;
                    border-radius: 5px;
                }

                QPushButton:hover {
                    background-color: #50565c;
                }

                QPushButton#exitButton {
                    background-color: #c0392b;
                }

                QPushButton#exitButton:hover {
                    background-color: #96281b;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f7fa;
                }

                QLabel#titleLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    background-color: #2f80ed;
                    padding: 12px;
                }

                QLabel#dbLabel {
                    background-color: #fff3cd;
                    border: 1px solid #ffeeba;
                    padding: 8px;
                    color: #856404;
                    font-weight: 500;
                }

                QPushButton {
                    background-color: #2d9cdb;
                    color: white;
                    padding: 10px;
                    font-size: 16px;
                    border: none;
                    border-radius: 5px;
                }

                QPushButton:hover {
                    background-color: #1b7fc3;
                }

                QPushButton#exitButton {
                    background-color: #e74c3c;
                }

                QPushButton#exitButton:hover {
                    background-color: #c0392b;
                }
            """)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header Label
        title_label = QLabel("Main Menu", self)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Database Info
        self.db_label = QLabel(f"Current Database File:\n{DB_PATH}", self)
        self.db_label.setObjectName("dbLabel")
        self.db_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.db_label)

        # Buttons for Customers and Options
        btn_customers = QPushButton("Customers")
        btn_customers.clicked.connect(self.open_customers)

        btn_options = QPushButton("Options")
        btn_options.clicked.connect(self.open_options)

        layout.addWidget(btn_customers)
        layout.addWidget(btn_options)

        # Exit Button
        btn_exit = QPushButton("Exit")
        btn_exit.setObjectName("exitButton")
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
    import ctypes
    from PyQt5.QtGui import QIcon
    from db_utils import initialize_database  # ✅ Make sure this is imported

    # Taskbar icon fix
    app_id = "com.avon.hello"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    # ✅ Initialize DB before doing anything else
    initialize_database()

    app = QApplication(sys.argv)

    # Set the icon globally
    icon_path = resource_path("Avon256.ico")
    app.setWindowIcon(QIcon(icon_path))

    window = MainMenu()
    window.show()
    sys.exit(app.exec_())

