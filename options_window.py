import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QLabel, 
    QSpinBox, QHBoxLayout, QWidget, QGroupBox, QGridLayout
)
from PyQt5.QtCore import Qt

DB_PATH = "avon_hello.db"

class OptionsWindow(QMainWindow):
    """Options Window - Manage Campaigns."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Options")
        self.setGeometry(250, 250, 600, 400)

        self.init_ui()
        self.load_campaign_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header Label
        title_label = QLabel("Options", self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: blue; color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Next & Previous Campaign Buttons (Moved to Top)
        btn_layout = QHBoxLayout()
        self.btn_prev_campaign = QPushButton("Previous Campaign")
        self.btn_next_campaign = QPushButton("Next Campaign")

        self.btn_prev_campaign.clicked.connect(self.decrement_campaign)
        self.btn_next_campaign.clicked.connect(self.increment_campaign)

        btn_layout.addWidget(self.btn_prev_campaign)
        btn_layout.addWidget(self.btn_next_campaign)

        layout.addLayout(btn_layout)

        # Create a GroupBox for Campaign Information
        campaign_group = QGroupBox("Campaign Management")
        campaign_layout = QGridLayout()

        # Current Campaign Section
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

        # Last Campaign of the Year Section
        self.last_campaign_label = QLabel("Last Campaign of Year")
        self.last_campaign_spin = QSpinBox()
        self.last_campaign_spin.setRange(1, 30)

        campaign_layout.addWidget(self.last_campaign_label, 0, 2)
        campaign_layout.addWidget(self.last_campaign_spin, 0, 3)

        campaign_group.setLayout(campaign_layout)
        layout.addWidget(campaign_group)

        # Exit Button at the Bottom
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.clicked.connect(self.close)
        layout.addWidget(self.btn_exit)

        # Set Layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_campaign_data(self):
        """Load campaign data from database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ensure campaign settings table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaign_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER DEFAULT 2025,
                campaign INTEGER DEFAULT 1,
                last_campaign INTEGER DEFAULT 30
            )
        """)

        # Check if data exists
        cursor.execute("SELECT year, campaign, last_campaign FROM campaign_settings ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()

        if result:
            year, campaign, last_campaign = result
        else:
            # Insert default values if none exist
            year, campaign, last_campaign = 2025, 1, 30
            cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                           (year, campaign, last_campaign))
            conn.commit()

        conn.close()

        # Set UI values
        self.year_spin.setValue(year)
        self.campaign_spin.setValue(campaign)
        self.last_campaign_spin.setValue(last_campaign)

    def save_campaign_data(self, year, campaign, last_campaign):
        """Save updated campaign data to database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Update the latest campaign settings
        cursor.execute("INSERT INTO campaign_settings (year, campaign, last_campaign) VALUES (?, ?, ?)", 
                       (year, campaign, last_campaign))
        conn.commit()
        conn.close()

    def increment_campaign(self):
        """Increase the campaign number, reset if it exceeds last campaign of the year."""
        current_campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()

        if current_campaign < last_campaign:
            current_campaign += 1
        else:
            # Reset to first campaign of next year
            current_campaign = 1
            new_year = self.year_spin.value() + 1
            self.year_spin.setValue(new_year)

        self.campaign_spin.setValue(current_campaign)
        self.save_campaign_data(self.year_spin.value(), current_campaign, last_campaign)

    def decrement_campaign(self):
        """Decrease the campaign number, move to last campaign of previous year if below 1."""
        current_campaign = self.campaign_spin.value()
        last_campaign = self.last_campaign_spin.value()

        if current_campaign > 1:
            current_campaign -= 1
        else:
            # Move to last campaign of the previous year
            current_campaign = last_campaign
            new_year = self.year_spin.value() - 1
            self.year_spin.setValue(new_year)

        self.campaign_spin.setValue(current_campaign)
        self.save_campaign_data(self.year_spin.value(), current_campaign, last_campaign)
