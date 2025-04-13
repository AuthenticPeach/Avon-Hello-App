import sqlite3
import configparser
import os
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel, 
    QSpinBox, QHBoxLayout, QWidget, QGroupBox, QGridLayout, QLineEdit, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from db_utils import DB_PATH, SETTINGS_FILE



def load_settings():
    config = configparser.ConfigParser()
    if not os.path.exists(SETTINGS_FILE):
        config['Appearance'] = {'dark_mode': 'false'}
        with open(SETTINGS_FILE, 'w') as f:
            config.write(f)
    else:
        config.read(SETTINGS_FILE)
    return config

def save_settings(config):
    with open(SETTINGS_FILE, 'w') as f:
        config.write(f)

def is_dark_mode_enabled():
    config = load_settings()
    return config.getboolean("Appearance", "dark_mode", fallback=False)

def set_dark_mode(enabled):
    config = load_settings()
    config["Appearance"]["dark_mode"] = "true" if enabled else "false"
    save_settings(config)

class OptionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        self.setGeometry(250, 250, 600, 500)
        self.setWindowIcon(QIcon("Avon256.png"))
        self.init_ui()
        self.load_campaign_data()

    def apply_stylesheet(self):
        if is_dark_mode_enabled():
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    padding: 6px;
                }
                QLineEdit, QSpinBox, QComboBox {
                    background-color: #1e1e1e;
                    color: white;
                    border: 1px solid #333;
                }
                QLabel, QCheckBox {
                    color: #f0f0f0;
                }
            """)
        else:
            self.setStyleSheet("")

    def init_ui(self):
        self.apply_stylesheet()
        layout = QVBoxLayout()

        title_label = QLabel("Options", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: blue; color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        btn_layout = QHBoxLayout()
        self.btn_prev_campaign = QPushButton("Previous Campaign")
        self.btn_next_campaign = QPushButton("Next Campaign")
        self.btn_prev_campaign.clicked.connect(self.decrement_campaign)
        self.btn_next_campaign.clicked.connect(self.increment_campaign)
        btn_layout.addWidget(self.btn_prev_campaign)
        btn_layout.addWidget(self.btn_next_campaign)
        layout.addLayout(btn_layout)

        campaign_group = QGroupBox("Campaign Management")
        campaign_layout = QGridLayout()

        self.year_label = QLabel("Year")
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2035)
        self.year_spin.setSuffix("  ")

        self.campaign_label = QLabel("Number")
        self.campaign_spin = QSpinBox()
        self.campaign_spin.setRange(1, 30)

        campaign_layout.addWidget(self.year_label, 0, 0)
        campaign_layout.addWidget(self.year_spin, 0, 1)
        campaign_layout.addWidget(self.campaign_label, 1, 0)
        campaign_layout.addWidget(self.campaign_spin, 1, 1)

        self.last_campaign_label = QLabel("Last Campaign of Year")
        self.last_campaign_spin = QSpinBox()
        self.last_campaign_spin.setRange(1, 30)
        campaign_layout.addWidget(self.last_campaign_label, 0, 2)
        campaign_layout.addWidget(self.last_campaign_spin, 0, 3)

        campaign_group.setLayout(campaign_layout)
        layout.addWidget(campaign_group)

        rep_group = QGroupBox("Ambassador Information")
        rep_layout = QGridLayout()

        self.rep_name_label = QLabel("Name:")
        self.rep_name_input = QLineEdit()

        self.rep_address_label = QLabel("Address:")
        self.rep_address_input = QLineEdit()

        self.rep_cell_phone_label = QLabel("Cell Phone:")
        self.rep_cell_phone_input = QLineEdit()

        self.rep_office_phone_label = QLabel("Office Phone:")
        self.rep_office_phone_input = QLineEdit()

        self.rep_email_label = QLabel("Email:")
        self.rep_email_input = QLineEdit()

        self.rep_website_label = QLabel("Website:")
        self.rep_website_input = QLineEdit()

        rep_layout.addWidget(self.rep_name_label, 0, 0)
        rep_layout.addWidget(self.rep_name_input, 0, 1)
        rep_layout.addWidget(self.rep_address_label, 1, 0)
        rep_layout.addWidget(self.rep_address_input, 1, 1)
        rep_layout.addWidget(self.rep_cell_phone_label, 2, 0)
        rep_layout.addWidget(self.rep_cell_phone_input, 2, 1)
        rep_layout.addWidget(self.rep_office_phone_label, 3, 0)
        rep_layout.addWidget(self.rep_office_phone_input, 3, 1)
        rep_layout.addWidget(self.rep_email_label, 4, 0)
        rep_layout.addWidget(self.rep_email_input, 4, 1)
        rep_layout.addWidget(self.rep_website_label, 5, 0)
        rep_layout.addWidget(self.rep_website_input, 5, 1)

        rep_group.setLayout(rep_layout)
        layout.addWidget(rep_group)

        self.dark_mode_checkbox = QCheckBox("Enable Dark Mode")
        self.dark_mode_checkbox.setChecked(is_dark_mode_enabled())
        layout.addWidget(self.dark_mode_checkbox)

        self.btn_save_options = QPushButton("Save Options")
        self.btn_save_options.clicked.connect(self.save_options)
        layout.addWidget(self.btn_save_options)

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_campaign_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER DEFAULT 2025,
                campaign INTEGER DEFAULT 1,
                last_campaign INTEGER DEFAULT 30
            )
        """)

        cursor.execute("SELECT year, campaign, last_campaign FROM campaign_settings ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            year, campaign, last_campaign = result
        else:
            year, campaign, last_campaign = 2025, 1, 30
            cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                           (year, campaign, last_campaign))
            conn.commit()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS representative_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rep_name TEXT,
                rep_address TEXT,
                rep_cell TEXT,
                rep_office TEXT,
                rep_email TEXT,
                rep_website TEXT
            )
        """)
        cursor.execute("SELECT rep_name, rep_address, rep_cell, rep_office, rep_email, rep_website FROM representative_info ORDER BY id DESC LIMIT 1")
        rep_result = cursor.fetchone()
        conn.close()

        self.year_spin.setValue(year)
        self.campaign_spin.setValue(campaign)
        self.last_campaign_spin.setValue(last_campaign)

        if rep_result:
            self.rep_name_input.setText(rep_result[0] or "")
            self.rep_address_input.setText(rep_result[1] or "")
            self.rep_cell_phone_input.setText(rep_result[2] or "")
            self.rep_office_phone_input.setText(rep_result[3] or "")
            self.rep_email_input.setText(rep_result[4] or "")
            self.rep_website_input.setText(rep_result[5] or "")

    def save_campaign_data(self, year, campaign, last_campaign):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                       (year, campaign, last_campaign))
        conn.commit()
        conn.close()

    def save_options(self):
        year = self.year_spin.value()
        campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()
        self.save_campaign_data(year, campaign, last_campaign)

        rep_name = self.rep_name_input.text()
        rep_address = self.rep_address_input.text()
        rep_cell = self.rep_cell_phone_input.text()
        rep_office = self.rep_office_phone_input.text()
        rep_email = self.rep_email_input.text()
        rep_website = self.rep_website_input.text()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO representative_info (rep_name, rep_address, rep_cell, rep_office, rep_email, rep_website)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rep_name, rep_address, rep_cell, rep_office, rep_email, rep_website))
        conn.commit()
        conn.close()

        set_dark_mode(self.dark_mode_checkbox.isChecked())
        QMessageBox.information(self, "Saved", "Settings saved. Please restart the app to apply theme changes.")

    def increment_campaign(self):
        current_campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()
        if current_campaign < last_campaign:
            current_campaign += 1
        else:
            current_campaign = 1
            new_year = self.year_spin.value() + 1
            self.year_spin.setValue(new_year)
        self.campaign_spin.setValue(current_campaign)
        self.save_campaign_data(self.year_spin.value(), current_campaign, last_campaign)

    def decrement_campaign(self):
        current_campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()
        if current_campaign > 1:
            current_campaign -= 1
        else:
            current_campaign = last_campaign
            new_year = self.year_spin.value() - 1
            self.year_spin.setValue(new_year)
        self.campaign_spin.setValue(current_campaign)
        self.save_campaign_data(self.year_spin.value(), current_campaign, last_campaign)
