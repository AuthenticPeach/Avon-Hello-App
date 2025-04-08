from PyQt5.QtCore import Qt
import sqlite3
import os
import configparser

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QTreeWidget, 
    QTreeWidgetItem, QWidget, QLabel, QLineEdit, QHBoxLayout, 
    QRadioButton, QMessageBox, QDialog, QComboBox, QGroupBox,
    QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem, QCheckBox
)

from db_utils import get_representative_info
from db_utils import get_current_campaign_settings
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle

DB_PATH = "avon_hello.db"
SETTINGS_FILE = "settings.conf"

def is_dark_mode_enabled():
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
        return config.getboolean("Appearance", "dark_mode", fallback=False)
    return False

class CustomersWindow(QMainWindow):
    """Customers Search with Editable Customer Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Search")
        self.setWindowIcon(QIcon("Avon256.png"))
        self.setGeometry(250, 250, 800, 500)
        self.init_ui()

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
                QLineEdit, QComboBox, QTreeWidget {
                    background-color: #1e1e1e;
                    color: white;
                    border: 1px solid #333;
                }
                QTreeWidget::item {
                    color: #f0f0f0;
                }
                QLabel, QRadioButton {
                    color: #f0f0f0;
                }
                QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 4px;
                border: 1px solid #444;
                }                              
            """)
        else:
            self.setStyleSheet("")

    def init_ui(self):
        self.apply_stylesheet()

        layout = QVBoxLayout()

        header_label = QLabel("Customer Search", self)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: #2c3e50; color: white; padding: 10px;")
        layout.addWidget(header_label)

        search_layout = QHBoxLayout()
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("First Name")
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Last Name")

        search_layout.addWidget(QLabel("First Name:"))
        search_layout.addWidget(self.first_name_input)
        search_layout.addWidget(QLabel("Last Name:"))
        search_layout.addWidget(self.last_name_input)

        layout.addLayout(search_layout)

        self.sort_by_first = QRadioButton("By First Name")
        self.sort_by_last = QRadioButton("By Last Name")
        self.sort_by_last.setChecked(True)

        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Group By:"))
        sort_layout.addWidget(self.sort_by_last)
        sort_layout.addWidget(self.sort_by_first)

        layout.addLayout(sort_layout)

        self.customer_tree = QTreeWidget()
        self.customer_tree.setHeaderLabels(["Customer Name", "Details"])
        self.customer_tree.setColumnWidth(0, 250)
        self.customer_tree.itemDoubleClicked.connect(self.open_edit_customer)
        layout.addWidget(self.customer_tree)

        btn_tree_layout = QHBoxLayout()
        self.btn_expand = QPushButton("Expand All")
        self.btn_collapse = QPushButton("Collapse All")
        self.btn_refresh_tree = QPushButton("Refresh Tree")

        for btn in (self.btn_expand, self.btn_collapse, self.btn_refresh_tree):
            btn.setStyleSheet("padding: 6px; font-size: 13px;")

        self.btn_expand.clicked.connect(self.expand_tree)
        self.btn_collapse.clicked.connect(self.collapse_tree)
        self.btn_refresh_tree.clicked.connect(self.load_customers)

        btn_tree_layout.addWidget(self.btn_expand)
        btn_tree_layout.addWidget(self.btn_collapse)
        btn_tree_layout.addWidget(self.btn_refresh_tree)
        layout.addLayout(btn_tree_layout)

        btn_layout = QHBoxLayout()
        self.btn_all_customers = QPushButton("All Customers")
        self.btn_add_customer = QPushButton("Add Customer")
        self.btn_exit = QPushButton("Exit")

        self.btn_all_customers.setStyleSheet("background-color: #3498db; color: white; font-size: 14px; padding: 6px;")
        self.btn_add_customer.setStyleSheet("background-color: #2ecc71; color: white; font-size: 14px; padding: 6px;")
        self.btn_exit.setStyleSheet("background-color: #e74c3c; color: white; font-size: 14px; padding: 6px;")

        btn_layout.addWidget(self.btn_all_customers)
        btn_layout.addWidget(self.btn_add_customer)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)

        self.btn_all_customers.clicked.connect(self.load_customers)
        self.btn_add_customer.clicked.connect(self.add_customer_dialog)
        self.btn_exit.clicked.connect(self.close)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.load_customers()

    def add_customer_dialog(self):
        """Open Add Customer Dialog."""
        dialog = AddCustomerDialog(self)
        if dialog.exec_():  # If dialog was accepted (customer added)
            self.load_customers()  # Refresh the list

    def load_customers(self):
        """Load all customers and display in a tree view."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, first_name, last_name FROM customers")
        rows = cursor.fetchall()
        conn.close()

        self.populate_tree(rows)

    def populate_tree(self, rows):
        """Display customers in a tree view grouped by first letter."""
        self.customer_tree.clear()
        letter_groups = {}

        sort_key = 1 if self.sort_by_first.isChecked() else 2

        for row in rows:
            customer_id, first_name, last_name = row
            key = first_name[0].upper() if self.sort_by_first.isChecked() else last_name[0].upper()

            if key not in letter_groups:
                letter_groups[key] = QTreeWidgetItem(self.customer_tree, [key])
                self.customer_tree.addTopLevelItem(letter_groups[key])

            customer_item = QTreeWidgetItem(letter_groups[key], [f"{first_name} {last_name} (#{customer_id})"])
            customer_item.setData(0, Qt.UserRole, customer_id)
            letter_groups[key].addChild(customer_item)

        self.customer_tree.expandAll()

    def expand_tree(self):
        """Expand all tree items."""
        self.customer_tree.expandAll()

    def collapse_tree(self):
        """Collapse all tree items."""
        self.customer_tree.collapseAll()

    def open_edit_customer(self, item, column):
        """Open the Edit Customer Window when a customer is double-clicked."""
        customer_id = item.data(0, Qt.UserRole)
        if customer_id:
            self.edit_customer_dialog = EditCustomerDialog(customer_id, self)
            self.edit_customer_dialog.exec_()
            self.load_customers()  # Refresh after edit

class EditCustomerDialog(QDialog):
    """Dialog to Edit a Customer and View Orders."""

    def __init__(self, customer_id, parent=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.setWindowTitle("Edit Customer")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Fetch customer data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT first_name, last_name, address, city, state, zip_code, 
                   cell_phone, office_phone, email, status 
            FROM customers 
            WHERE customer_id = ?
        """, (customer_id,))
        customer = cursor.fetchone()
        conn.close()

        if not customer:
            QMessageBox.critical(self, "Error", "Customer not found in database!")
            self.reject()
            return

        # Customer fields
        self.first_name_input = QLineEdit(customer[0])
        self.last_name_input = QLineEdit(customer[1])
        self.address_input = QLineEdit(customer[2])
        self.city_input = QLineEdit(customer[3])
        self.state_input = QLineEdit(customer[4])
        self.zip_code_input = QLineEdit(customer[5])
        self.cell_phone_input = QLineEdit(customer[6])
        self.office_phone_input = QLineEdit(customer[7])
        self.email_input = QLineEdit(customer[8])

        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Closed", "Deleted"])
        self.status_input.setCurrentText(customer[9])

        form_fields = [
            ("First Name:", self.first_name_input),
            ("Last Name:", self.last_name_input),
            ("Address:", self.address_input),
            ("City:", self.city_input),
            ("State:", self.state_input),
            ("ZIP Code:", self.zip_code_input),
            ("Cell Phone:", self.cell_phone_input),
            ("Office Phone:", self.office_phone_input),
            ("Email:", self.email_input),
            ("Status:", self.status_input),
        ]
        for label, widget in form_fields:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        # Order Summary
        order_group = QGroupBox("Order Summary (Current Campaign)")
        order_layout = QVBoxLayout()

        current_year, current_campaign = get_current_campaign_settings()
        self.order_year = QLabel(f"Campaign Year: {current_year}")
        self.order_campaign = QLabel(f"Campaign Number: {current_campaign}")

        self.order_total = QLabel("Order Total: $0.00")
        self.previous_balance = QLabel("Previous Balance: $0.00")
        self.payment = QLabel("Payment: $0.00")
        self.net_due = QLabel("Net Due: $0.00")
        self.time_submitted_label = QLabel("Time Submitted: N/A")
        self.last_edited_label = QLabel("Last Edited: N/A")

        for lbl in [
            self.order_year, self.order_campaign, self.order_total,
            self.previous_balance, self.payment, self.net_due,
            self.time_submitted_label, self.last_edited_label
        ]:
            order_layout.addWidget(lbl)

        order_group.setLayout(order_layout)
        layout.addWidget(order_group)

        # Buttons and controls
        self.btn_order_entry = QPushButton("New Order Entry")
        self.btn_order_entry.clicked.connect(self.open_order_entry)
        layout.addWidget(self.btn_order_entry)

        self.order_history = QComboBox()
        self.order_history.currentIndexChanged.connect(self.display_order_details)
        layout.addWidget(QLabel("Order History:"))
        layout.addWidget(self.order_history)

        btn_refresh_summary = QPushButton("Refresh Order Summary")
        btn_refresh_summary.clicked.connect(self.refresh_order_summary)
        layout.addWidget(btn_refresh_summary)

        self.btn_view_order = QPushButton("View Order Details")
        self.btn_view_order.clicked.connect(self.view_order_details)
        layout.addWidget(self.btn_view_order)

        btn_save = QPushButton("Save Changes")
        btn_save.clicked.connect(self.save_customer)
        layout.addWidget(btn_save)

        self.setLayout(layout)
        self.refresh_order_summary()

    def open_order_entry(self):
        current_year, current_campaign = get_current_campaign_settings()
        self.order_entry_dialog = OrderEntryDialog(
            self.customer_id, current_year, current_campaign, self
        )
        self.order_entry_dialog.exec_()
        self.refresh_order_summary()

    def refresh_order_summary(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, 
                   previous_balance, payment, net_due, 
                   time_submitted, last_edited
            FROM orders
            WHERE customer_id = ?
            ORDER BY time_submitted DESC
            LIMIT 1
        """, (self.customer_id,))
        order_data = cursor.fetchone()
        conn.close()

        current_year, current_campaign = get_current_campaign_settings()
        self.order_year.setText(f"Campaign Year: {current_year}")
        self.order_campaign.setText(f"Campaign Number: {current_campaign}")

        if order_data:
            self.order_total.setText(f"Order Total: ${order_data[2]:.2f}")
            self.previous_balance.setText(f"Previous Balance: ${order_data[3]:.2f}")
            self.payment.setText(f"Payment: ${order_data[4]:.2f}")
            self.net_due.setText(f"Net Due: ${order_data[5]:.2f}")
            self.time_submitted_label.setText(f"Time Submitted: {order_data[6]}")
            self.last_edited_label.setText(f"Last Edited: {order_data[7]}")
        else:
            self.order_total.setText("Order Total: $0.00")
            self.previous_balance.setText("Previous Balance: $0.00")
            self.payment.setText("Payment: $0.00")
            self.net_due.setText("Net Due: $0.00")
            self.time_submitted_label.setText("Time Submitted: N/A")
            self.last_edited_label.setText("Last Edited: N/A")

        self.load_order_history()

    def load_order_history(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT order_id, campaign_year, campaign_number, order_total, net_due
            FROM orders
            WHERE customer_id = ?
            ORDER BY time_submitted DESC
        """, (self.customer_id,))
        orders = cursor.fetchall()
        conn.close()

        self.order_history.clear()
        for order in orders:
            order_id, year, campaign, total, net_due = order
            display_text = f"Campaign {campaign} ({year}): Total ${total:.2f}, Due ${net_due:.2f}"
            self.order_history.addItem(display_text, order_id)

    def display_order_details(self, index):
        if index < 0:
            return
        order_id = self.order_history.itemData(index)
        if not order_id:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, 
                   previous_balance, payment, net_due
            FROM orders
            WHERE order_id = ?
        """, (order_id,))
        order = cursor.fetchone()
        conn.close()

        if order:
            self.order_year.setText(f"Campaign Year: {order[0]}")
            self.order_campaign.setText(f"Campaign Number: {order[1]}")
            self.order_total.setText(f"Order Total: ${order[2]:.2f}")
            self.previous_balance.setText(f"Previous Balance: ${order[3]:.2f}")
            self.payment.setText(f"Payment: ${order[4]:.2f}")
            self.net_due.setText(f"Net Due: ${order[5]:.2f}")

    def view_order_details(self):
        index = self.order_history.currentIndex()
        if index < 0:
            return
        order_id = self.order_history.itemData(index)
        if not order_id:
            return
        dialog = OrderEntryDialog(self.customer_id, 0, 0, self, order_id=order_id)
        dialog.exec_()

    def save_customer(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers SET
                first_name = ?, last_name = ?, address = ?, city = ?, 
                state = ?, zip_code = ?, 
                cell_phone = ?, office_phone = ?, 
                email = ?, status = ?
            WHERE customer_id = ?
        """, (
            self.first_name_input.text(), self.last_name_input.text(), self.address_input.text(),
            self.city_input.text(), self.state_input.text(), self.zip_code_input.text(),
            self.cell_phone_input.text(), self.office_phone_input.text(),
            self.email_input.text(), self.status_input.currentText(), self.customer_id
        ))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success", "Customer updated successfully!")
        self.accept()

class AddCustomerDialog(QDialog):
    """Dialog to Add a New Customer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        layout = QVBoxLayout()

        # Field inputs
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.city_input = QLineEdit()
        self.state_input = QLineEdit()
        self.zip_code_input = QLineEdit()
        self.cell_phone_input = QLineEdit()
        self.office_phone_input = QLineEdit()
        self.email_input = QLineEdit()

        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Closed", "Deleted"])
        self.status_input.setCurrentText("Active")

        # Add form fields to layout
        for label_text, widget in [
            ("First Name:", self.first_name_input),
            ("Last Name:", self.last_name_input),
            ("Address:", self.address_input),
            ("City:", self.city_input),
            ("State:", self.state_input),
            ("ZIP Code:", self.zip_code_input),
            ("Cell Phone:", self.cell_phone_input),
            ("Office Phone:", self.office_phone_input),
            ("Email:", self.email_input),
            ("Status:", self.status_input),
        ]:
            layout.addWidget(QLabel(label_text))
            layout.addWidget(widget)

        # Save button
        btn_save = QPushButton("Save Customer")
        btn_save.clicked.connect(self.save_customer)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def save_customer(self):

        """Insert new customer into the database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (
                first_name, last_name, address, city, state, zip_code,
                cell_phone, office_phone, email, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.first_name_input.text(),
            self.last_name_input.text(),
            self.address_input.text(),
            self.city_input.text(),
            self.state_input.text(),
            self.zip_code_input.text(),
            self.cell_phone_input.text(),
            self.office_phone_input.text(),
            self.email_input.text(),
            self.status_input.currentText()
        ))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Customer added successfully!")
        self.accept()


class OrderEntryDialog(QDialog):
    """Dialog to Enter Order Details for a Customer."""
    
    def __init__(self, customer_id, campaign_year, campaign_number, parent=None, order_id=None):
        super().__init__(parent)
        self.setWindowTitle("Order Entry")
        self.setGeometry(300, 200, 1000, 500)
        self.customer_id = customer_id
        # If order_id is provided, we will load that order’s details.
        self.order_id = order_id
        # Otherwise, use the provided campaign settings for a new order.
        self.campaign_year = campaign_year
        self.campaign_number = campaign_number

        # Define order_date as the current date/time (or later overwritten if loading an existing order)
        self.order_date = datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        
        # Representative info can be set here or loaded from your database.
        self.rep_name = "Representative Name"
        self.rep_address = "Representative Address"
        self.rep_phone = "Representative Phone"
        self.rep_email = "Representative Email"
        self.rep_website = "Representative Website"

        layout = QVBoxLayout()

        # Set up Order Table
        self.order_table = QTableWidget(0, 11)
        self.order_table.setHorizontalHeaderLabels([
            "Product #", "Page", "Description", "Shade/Fragrance", "Size", "QTY",
            "Unit Price", "Reg Price", "Tax", "Discount %", "Total Price"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.order_table)

        # Connect the itemChanged signal once.
        self.order_table.itemChanged.connect(self.update_total)

        # Buttons for actions
        btn_layout = QHBoxLayout()
        self.btn_add_row = QPushButton("Add Product")
        self.btn_save_order = QPushButton("Save Order")
        self.btn_print_order = QPushButton("Print Order")
        self.btn_add_row.clicked.connect(self.add_order_row)
        self.btn_save_order.clicked.connect(self.save_order)
        self.btn_print_order.clicked.connect(self.print_order)
        btn_layout.addWidget(self.btn_add_row)
        btn_layout.addWidget(self.btn_save_order)
        btn_layout.addWidget(self.btn_print_order)
        layout.addLayout(btn_layout)

        # Total Order Summary Label
        self.total_label = QLabel("Total: $0.00")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

        # If an order_id was provided, load its details.
        if self.order_id is not None:
            self.load_order_details(self.order_id)

    def add_order_row(self):
        """Add a new row to the order table."""
        row_position = self.order_table.rowCount()
        self.order_table.insertRow(row_position)

        # Adding input fields to each column
        self.order_table.setItem(row_position, 0, QTableWidgetItem(""))  # Product Number
        self.order_table.setItem(row_position, 1, QTableWidgetItem(""))  # Page
        self.order_table.setItem(row_position, 2, QTableWidgetItem(""))  # Description
        self.order_table.setItem(row_position, 3, QTableWidgetItem(""))  # Shade/Fragrance
        self.order_table.setItem(row_position, 4, QTableWidgetItem(""))  # Size
        self.order_table.setItem(row_position, 5, QTableWidgetItem("1"))  # QTY (Default: 1)
        self.order_table.setItem(row_position, 6, QTableWidgetItem("$0.00"))  # Unit Price (Default)
        self.order_table.setItem(row_position, 7, QTableWidgetItem("$0.00"))  # Reg Price (Default)

        # Checkbox for Tax
        tax_checkbox = QCheckBox()
        tax_checkbox.setChecked(False)
        self.order_table.setCellWidget(row_position, 8, tax_checkbox)

        self.order_table.setItem(row_position, 9, QTableWidgetItem("0"))  # Discount %

        # Ensure Total Price column starts with "$0.00"
        self.order_table.setItem(row_position, 10, QTableWidgetItem("$0.00"))

        # Connect events
        self.order_table.itemChanged.connect(self.update_total)

    def update_total(self, changed_item):
        if changed_item is not None and changed_item.column() in (6, 7):
            text = changed_item.text()
            if text and not text.startswith("$"):
                self.order_table.blockSignals(True)
                cleaned_text = text.replace("$", "")
                changed_item.setText(f"${cleaned_text}")
                self.order_table.blockSignals(False)

        total = 0.0
        for row in range(self.order_table.rowCount()):
            try:
                qty_item = self.order_table.item(row, 5)
                unit_price_item = self.order_table.item(row, 6)
                discount_item = self.order_table.item(row, 9)
                tax_checkbox = self.order_table.cellWidget(row, 8)

                qty = float(qty_item.text()) if qty_item and qty_item.text().strip() else 0
                unit_price = float(unit_price_item.text().replace("$", "")) if unit_price_item and unit_price_item.text().strip() else 0
                discount = float(discount_item.text()) if discount_item and discount_item.text().strip() else 0

                # Base and discounted price
                base_price = unit_price * qty
                discounted_price = base_price * ((100 - discount) / 100)

                # Add tax if checked
                if tax_checkbox and tax_checkbox.isChecked():
                    tax_amount = discounted_price * 0.09386
                else:
                    tax_amount = 0.0

                final_price = discounted_price + tax_amount

                # Update total column
                total_price_item = self.order_table.item(row, 10)
                if not total_price_item:
                    self.order_table.setItem(row, 10, QTableWidgetItem(f"${final_price:.2f}"))
                else:
                    total_price_item.setText(f"${final_price:.2f}")

                total += final_price
            except ValueError:
                continue

        self.total_label.setText(f"Total: ${total:.2f}")


    def open_order_entry(self):
        """Open Order Entry Window using current campaign settings."""
        current_year, current_campaign = get_current_campaign_settings()
        self.order_entry_dialog = OrderEntryDialog(self.customer_id, current_year, current_campaign, self)
        self.order_entry_dialog.exec_()
        # Refresh the order summary after closing the Order Entry dialog
        self.refresh_order_summary()

    def load_order_details(self, order_id):
        """Load the order details and products from the database into the dialog."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Updated query: use time_submitted instead of order_date
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, previous_balance, payment, net_due, time_submitted
            FROM orders
            WHERE order_id = ?
        """, (order_id,))
        order_data = cursor.fetchone()
        if order_data:
            self.campaign_year = order_data[0]
            self.campaign_number = order_data[1]
            # Update internal variable for display, if desired
            self.order_date = order_data[6]  # now using time_submitted
            self.total_label.setText(f"Total: ${order_data[2]:.2f}")
        # Load the associated products (unchanged)
        cursor.execute("""
            SELECT product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price
            FROM order_products
            WHERE order_id = ?
        """, (order_id,))
        products = cursor.fetchall()
        conn.close()
        for product in products:
            row_position = self.order_table.rowCount()
            self.order_table.insertRow(row_position)
            self.order_table.setItem(row_position, 0, QTableWidgetItem(product[0]))
            self.order_table.setItem(row_position, 1, QTableWidgetItem(product[1]))
            self.order_table.setItem(row_position, 2, QTableWidgetItem(product[2]))
            self.order_table.setItem(row_position, 3, QTableWidgetItem(product[3]))
            self.order_table.setItem(row_position, 4, QTableWidgetItem(product[4]))
            self.order_table.setItem(row_position, 5, QTableWidgetItem(str(product[5])))
            self.order_table.setItem(row_position, 6, QTableWidgetItem(f"${product[6]:.2f}"))
            self.order_table.setItem(row_position, 7, QTableWidgetItem(f"${product[7]:.2f}"))
            tax_checkbox = QCheckBox()
            tax_checkbox.setChecked(bool(product[8]))
            self.order_table.setCellWidget(row_position, 8, tax_checkbox)
            self.order_table.setItem(row_position, 9, QTableWidgetItem(str(product[9])))
            self.order_table.setItem(row_position, 10, QTableWidgetItem(f"${product[10]:.2f}"))
        self.update_total(None)

    def save_order(self):
        """Save order to the database and update order history."""
        print("Save Order button clicked.")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            # Ensure orders table exists
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
                    last_edited TEXT DEFAULT (datetime('now', 'localtime'))
                )
            """)

            # Calculate order_total by summing each product’s total
            order_total = 0.0
            for row in range(self.order_table.rowCount()):
                total_price_item = self.order_table.item(row, 10)
                if total_price_item and total_price_item.text().strip():
                    try:
                        row_total = float(total_price_item.text().replace("$", ""))
                        order_total += row_total
                    except ValueError:
                        print(f"Invalid total at row {row}: {total_price_item.text()}")
                        continue

            print(f"Calculated order total: {order_total}")

            # Insert new order using the current campaign settings from the dialog
            cursor.execute("""
                INSERT INTO orders (customer_id, campaign_year, campaign_number, order_total, previous_balance, payment, net_due)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.customer_id,
                self.campaign_year,
                self.campaign_number,
                order_total,
                0,           # previous_balance; update if needed
                0,           # payment; update if needed
                order_total  # net_due; for now assume net_due equals order_total
            ))
            order_id = cursor.lastrowid  # Get the inserted order ID
            print(f"Order inserted with order_id: {order_id}")

            # Ensure order_products table exists
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
                    discount REAL,
                    total_price REAL
                )
            """)

            # Insert each product into order_products table
            for row in range(self.order_table.rowCount()):
                try:
                    product_number = self.order_table.item(row, 0).text()
                    page = self.order_table.item(row, 1).text()
                    description = self.order_table.item(row, 2).text()
                    shade = self.order_table.item(row, 3).text()
                    size = self.order_table.item(row, 4).text()
                    qty = int(self.order_table.item(row, 5).text())
                    unit_price = float(self.order_table.item(row, 6).text().replace("$", "").strip())
                    reg_price = float(self.order_table.item(row, 7).text().replace("$", "").strip())
                    tax_checkbox = self.order_table.cellWidget(row, 8)
                    tax = 1 if tax_checkbox and tax_checkbox.isChecked() else 0
                    discount = float(self.order_table.item(row, 9).text())
                    total_price = float(self.order_table.item(row, 10).text().replace("$", "").strip())
                    
                    cursor.execute("""
                        INSERT INTO order_products 
                        (order_id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (order_id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price))
                    print(f"Inserted product for row {row}")
                except Exception as e:
                    print(f"Error inserting product for row {row}: {e}")
                    continue  # Skip rows with invalid data

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Saved", "Order saved successfully!")
            self.accept()  # Close the order entry dialog

        except Exception as e:
            print("Error in save_order:", e)
            QMessageBox.critical(self, "Error", f"An error occurred while saving the order: {e}")

    def print_order(self):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib.units import inch
        from datetime import datetime
        from db_utils import get_representative_info
        import math

        def format_phone(raw):
            digits = ''.join(filter(str.isdigit, raw))
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else raw
        
        def round_up(value):
            return math.ceil(value * 100) / 100  # Always round up to the next cent


        rep_info = get_representative_info()
        campaign_number = self.parent().campaign_number if hasattr(self.parent(), "campaign_number") else "7"
        campaign_date = datetime.now().strftime("%A, %B %d, %Y")
        today_str = datetime.now().strftime("%Y-%m-%d")

        # --- Customer info ---
        customer_name = f"{self.parent().first_name_input.text()} {self.parent().last_name_input.text()}"
        customer_address = self.parent().address_input.text()
        customer_cell = self.parent().cell_phone_input.text()
        customer_office = self.parent().office_phone_input.text()

        filename = f"invoice-{customer_name.replace(' ', '_').lower()}-{today_str}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # --- Header ---
        c.setFont("Helvetica", 9)

        # Customer Info (Top Left)
        y_cust = 770
        c.drawString(40, y_cust, customer_name)
        y_cust -= 15
        c.drawString(40, y_cust, customer_address)
        if customer_cell.strip():
            y_cust -= 15
            c.drawString(40, y_cust, f"Cell: {format_phone(customer_cell)}")
        if customer_office.strip():
            y_cust -= 15
            c.drawString(40, y_cust, f"Office: {format_phone(customer_office)}")

        # Rep Info (Top Right)
        y_rep = 770
        c.drawRightString(width - 40, y_rep, rep_info["rep_name"])
        c.drawRightString(width - 40, y_rep - 15, rep_info["rep_address"])
        if rep_info.get("rep_office_phone", "").strip():
            c.drawRightString(width - 40, y_rep - 30, f"Office: {format_phone(rep_info['rep_office_phone'])}")
        if rep_info.get("rep_email", "").strip():
            c.drawRightString(width - 40, y_rep - 45, f"Email: {rep_info['rep_email']}")
        if rep_info.get("rep_website", "").strip():
            c.drawRightString(width - 40, y_rep - 60, f"Visit my website at: {rep_info['rep_website']}")
        if rep_info.get("rep_cell_phone", "").strip():
            c.drawRightString(width - 40, y_rep - 75, f"Cell/Text: {format_phone(rep_info['rep_cell_phone'])}")

        # Centered Title
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(width / 2, 735, f"AVON BY {rep_info['rep_name']}")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width / 2, 720, "*** CUSTOMER ORDER ***")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, 705, f"Campaign #{campaign_number}")
        c.drawCentredString(width / 2, 690, campaign_date)

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]

        # Order Table
        data = [["Page", "Product #", "Product", "Qty", "Unit Price", "Total"]]
        subtotal = 0.0
        total_discount = 0.0
        apply_processing = False
        apply_tax = False

        for row in range(self.order_table.rowCount()):
            try:
                page = self.order_table.item(row, 1).text()
                product_number = self.order_table.item(row, 0).text()
                description = self.order_table.item(row, 2).text()
                qty = int(self.order_table.item(row, 5).text())
                unit_price = float(self.order_table.item(row, 6).text().replace("$", "").strip())
                reg_price = float(self.order_table.item(row, 7).text().replace("$", "").strip())
                discount_percent = float(self.order_table.item(row, 9).text() or 0)

                tax_widget = self.order_table.cellWidget(row, 8)
                proc_widget = self.order_table.cellWidget(row, 7)
                tax_checked = tax_widget and tax_widget.isChecked()
                proc_checked = proc_widget and proc_widget.isChecked()

                if proc_checked:
                    apply_processing = True
                if tax_checked:
                    apply_tax = True

                unit_discount = reg_price * (discount_percent / 100)
                discounted_price = unit_price - unit_discount
                total_price = round_up(discounted_price * qty)

                if discount_percent > 0:
                    discount_total = round_up(unit_discount * qty)
                    description += f" (Discount {int(discount_percent)}% for -${discount_total:.2f})"
                    total_discount += discount_total

                subtotal += total_price

                data.append([
                    page,
                    product_number,
                    Paragraph(description, ParagraphStyle(name='Normal', fontName='Helvetica', fontSize=9)),
                    str(qty),
                    f"${unit_price:.2f}",
                    f"${total_price:.2f}"
                ])
            except Exception as e:
                print(f"Error in row {row}: {e}")

        table = Table(data, colWidths=[0.7*inch, 1*inch, 2.4*inch, 0.6*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
            ('FONT', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONT', (0,1), (-1,-1), 'Helvetica'),
        ]))
        table.wrapOn(c, width, height)
        table.drawOn(c, 60, 520)

        # Totals Section
        tax_rate = 9.386 / 100
        tax_amount = round_up(subtotal * tax_rate) if apply_tax else 0.0
        processing_charge = 0.50 if apply_processing else 0.0
        grand_total = round_up(subtotal + tax_amount + processing_charge)

        totals_data = [["Sub Total:", f"${subtotal:.2f}"]]
        if total_discount > 0:
            totals_data.append(["Line Item Discounts:", f"-${total_discount:.2f}"])
        if apply_processing:
            totals_data.append(["Processing:", f"${processing_charge:.2f}"])
        if apply_tax:
            totals_data.append(["Tax (9.386%):", f"${tax_amount:.2f}"])
        totals_data.append(["Grand Total:", f"${grand_total:.2f}"])

        totals_table = Table(totals_data, colWidths=[1.5 * inch, 1 * inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONT', (0, 0), (-1, -2), 'Helvetica'),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        totals_table.wrapOn(c, width, height)
        totals_table.drawOn(c, width - 220, 400)

        # --- Thank You Message (just under totals) ---
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width / 2, 385, "Thank you for your order!")
        c.save()

        # Auto open the PDF
        import subprocess
        subprocess.Popen([filename], shell=True)