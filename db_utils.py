import sqlite3
import os
from config import DB_PATH, SETTINGS_FILE, LOG_FILE
import configparser

def initialize_database():
    """Initialize all required database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Customers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            office_phone TEXT,
            cell_phone TEXT,
            email TEXT,
            status TEXT
        )
    """)

    # Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            campaign_year INTEGER,
            campaign_number INTEGER,
            order_total REAL DEFAULT 0,
            previous_balance REAL DEFAULT 0,
            payment REAL DEFAULT 0,
            net_due REAL DEFAULT 0,
            time_submitted TEXT DEFAULT (datetime('now', 'localtime')),
            last_edited TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Order Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_number TEXT,
            page TEXT,
            description TEXT,
            shade TEXT,
            size TEXT,
            qty INTEGER,
            unit_price REAL,
            reg_price REAL,
            tax INTEGER,
            processing INTEGER,
            discount REAL,
            total_price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)

    # Campaign Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER DEFAULT 2025,
            campaign INTEGER DEFAULT 1,
            last_campaign INTEGER DEFAULT 30
        )
    """)

    # Representative Info Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS representative_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rep_name TEXT,
            rep_address TEXT,
            rep_office TEXT,
            rep_cell TEXT,
            rep_email TEXT,
            rep_website TEXT
        )
    """)

    conn.commit()
    conn.close()

def get_representative_info():
    """Fetch representative info from the settings file."""
    config = configparser.ConfigParser()
    if not os.path.exists(SETTINGS_FILE):
        return {}

    config.read(SETTINGS_FILE)
    return {
        "rep_name": config.get("Representative", "rep_name", fallback=""),
        "rep_address": config.get("Representative", "rep_address", fallback=""),
        "rep_office": config.get("Representative", "rep_office", fallback=""),
        "rep_cell": config.get("Representative", "rep_cell", fallback=""),
        "rep_email": config.get("Representative", "rep_email", fallback=""),
        "rep_website": config.get("Representative", "rep_website", fallback="")
    }

def get_current_campaign_settings():
    """Retrieve the current campaign year and campaign number from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT year, campaign FROM campaign_settings ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result
    return (2025, 1)
