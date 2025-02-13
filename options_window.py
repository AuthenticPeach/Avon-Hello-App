import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel, 
    QSpinBox, QHBoxLayout, QWidget, QGroupBox, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt

DB_PATH = "avon_hello.db"

class OptionsWindow(QMainWindow):
    """Options Window - Manage Campaigns and Representative Info."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        self.setGeometry(250, 250, 600, 500)
        self.init_ui()
        self.load_campaign_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header Label
        title_label = QLabel("Options", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: blue; color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Campaign Navigation Buttons
        btn_layout = QHBoxLayout()
        self.btn_prev_campaign = QPushButton("Previous Campaign")
        self.btn_next_campaign = QPushButton("Next Campaign")
        self.btn_prev_campaign.clicked.connect(self.decrement_campaign)
        self.btn_next_campaign.clicked.connect(self.increment_campaign)
        btn_layout.addWidget(self.btn_prev_campaign)
        btn_layout.addWidget(self.btn_next_campaign)
        layout.addLayout(btn_layout)

        # Campaign Management Group
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

        # Representative Information Group
        rep_group = QGroupBox("Representative Information")
        rep_layout = QGridLayout()

        self.rep_name_label = QLabel("Name:")
        self.rep_name_input = QLineEdit()

        self.rep_address_label = QLabel("Address:")
        self.rep_address_input = QLineEdit()

        self.rep_phone_label = QLabel("Phone:")
        self.rep_phone_input = QLineEdit()

        self.rep_email_label = QLabel("Email:")
        self.rep_email_input = QLineEdit()

        self.rep_website_label = QLabel("Website:")
        self.rep_website_input = QLineEdit()

        rep_layout.addWidget(self.rep_name_label, 0, 0)
        rep_layout.addWidget(self.rep_name_input, 0, 1)
        rep_layout.addWidget(self.rep_address_label, 1, 0)
        rep_layout.addWidget(self.rep_address_input, 1, 1)
        rep_layout.addWidget(self.rep_phone_label, 2, 0)
        rep_layout.addWidget(self.rep_phone_input, 2, 1)
        rep_layout.addWidget(self.rep_email_label, 3, 0)
        rep_layout.addWidget(self.rep_email_input, 3, 1)
        rep_layout.addWidget(self.rep_website_label, 4, 0)
        rep_layout.addWidget(self.rep_website_input, 4, 1)

        rep_group.setLayout(rep_layout)
        layout.addWidget(rep_group)

        # Save Options Button
        self.btn_save_options = QPushButton("Save Options")
        self.btn_save_options.clicked.connect(self.save_options)
        layout.addWidget(self.btn_save_options)

        # Exit Button
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_campaign_data(self):
        """Load campaign and representative data from the database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ensure campaign_settings table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER DEFAULT 2025,
                campaign INTEGER DEFAULT 1,
                last_campaign INTEGER DEFAULT 30
            )
        """)

        # Get campaign settings
        cursor.execute("SELECT year, campaign, last_campaign FROM campaign_settings ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            year, campaign, last_campaign = result
        else:
            year, campaign, last_campaign = 2025, 1, 30
            cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                           (year, campaign, last_campaign))
            conn.commit()

        # Ensure representative_info table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS representative_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rep_name TEXT,
                rep_address TEXT,
                rep_phone TEXT,
                rep_email TEXT,
                rep_website TEXT
            )
        """)
        cursor.execute("SELECT rep_name, rep_address, rep_phone, rep_email, rep_website FROM representative_info ORDER BY id DESC LIMIT 1")
        rep_result = cursor.fetchone()
        conn.close()

        # Set campaign values
        self.year_spin.setValue(year)
        self.campaign_spin.setValue(campaign)
        self.last_campaign_spin.setValue(last_campaign)

        # Set representative fields
        if rep_result:
            self.rep_name_input.setText(rep_result[0] if rep_result[0] else "")
            self.rep_address_input.setText(rep_result[1] if rep_result[1] else "")
            self.rep_phone_input.setText(rep_result[2] if rep_result[2] else "")
            self.rep_email_input.setText(rep_result[3] if rep_result[3] else "")
            self.rep_website_input.setText(rep_result[4] if rep_result[4] else "")

    def save_campaign_data(self, year, campaign, last_campaign):
        """Save campaign data by inserting a new row."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                       (year, campaign, last_campaign))
        conn.commit()
        conn.close()

    def save_options(self):
        """Save both campaign settings and representative info."""
        # Save campaign settings
        year = self.year_spin.value()
        campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()
        self.save_campaign_data(year, campaign, last_campaign)

        # Save representative info
        rep_name = self.rep_name_input.text()
        rep_address = self.rep_address_input.text()
        rep_phone = self.rep_phone_input.text()
        rep_email = self.rep_email_input.text()
        rep_website = self.rep_website_input.text()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO representative_info (rep_name, rep_address, rep_phone, rep_email, rep_website)
            VALUES (?, ?, ?, ?, ?)
        """, (rep_name, rep_address, rep_phone, rep_email, rep_website))
        conn.commit()
        conn.close()

    def increment_campaign(self):
        """Increase the campaign number (or move to next year)."""
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
        """Decrease the campaign number (or move to previous year)."""
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
