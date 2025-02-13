from PyQt5.QtCore import Qt
import sqlite3
import os

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QTreeWidget, 
    QTreeWidgetItem, QWidget, QLabel, QLineEdit, QHBoxLayout, 
    QRadioButton, QMessageBox, QDialog, QComboBox, QGroupBox,
    QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem
)

from db_utils import get_representative_info
from db_utils import get_current_campaign_settings
from datetime import datetime

DB_PATH = "avon_hello.db"

class CustomersWindow(QMainWindow):
    """Customers Search with Editable Customer Window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Customer Search")
        self.setGeometry(250, 250, 800, 500)

        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Header Label
        header_label = QLabel("Customer Search", self)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; background-color: blue; color: white; padding: 10px;")
        layout.addWidget(header_label)

        # Search Fields
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

        # Search Results Sorting Options
        self.sort_by_first = QRadioButton("By First Name")
        self.sort_by_last = QRadioButton("By Last Name")
        self.sort_by_last.setChecked(True)  # Default selection

        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Group By:"))
        sort_layout.addWidget(self.sort_by_last)
        sort_layout.addWidget(self.sort_by_first)

        layout.addLayout(sort_layout)

        # Customer Tree Structure
        self.customer_tree = QTreeWidget()
        self.customer_tree.setHeaderLabels(["Customer Name", "Details"])

        # Set column width for better spacing
        self.customer_tree.setColumnWidth(0, 250)  # Adjust width of the "Customer Name" column

        self.customer_tree.itemDoubleClicked.connect(self.open_edit_customer)  # Double-click opens edit
        layout.addWidget(self.customer_tree)

        # Buttons for Expand/Collapse
        btn_tree_layout = QHBoxLayout()
        self.btn_expand = QPushButton("Expand All")
        self.btn_collapse = QPushButton("Collapse All")
        self.btn_refresh_tree = QPushButton("Refresh Tree")

        self.btn_expand.clicked.connect(self.expand_tree)
        self.btn_collapse.clicked.connect(self.collapse_tree)
        self.btn_refresh_tree.clicked.connect(self.load_customers)

        btn_tree_layout.addWidget(self.btn_expand)
        btn_tree_layout.addWidget(self.btn_collapse)
        btn_tree_layout.addWidget(self.btn_refresh_tree)
        layout.addLayout(btn_tree_layout)

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.btn_all_customers = QPushButton("All Customers")
        self.btn_add_customer = QPushButton("Add Customer")
        self.btn_exit = QPushButton("Exit")

        btn_layout.addWidget(self.btn_all_customers)
        btn_layout.addWidget(self.btn_add_customer)
        btn_layout.addWidget(self.btn_exit)

        layout.addLayout(btn_layout)

        # Connect Buttons
        self.btn_all_customers.clicked.connect(self.load_customers)
        self.btn_add_customer.clicked.connect(self.add_customer_dialog)
        self.btn_exit.clicked.connect(self.close)

        # Set Layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Load All Customers Initially
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

        # Determine sorting type
        if self.sort_by_first.isChecked():
            sort_key = 1  # First Name
        else:
            sort_key = 2  # Last Name

        # Organize customers by first letter of their name
        for row in rows:
            customer_id, first_name, last_name = row
            key = first_name[0].upper() if self.sort_by_first.isChecked() else last_name[0].upper()

            if key not in letter_groups:
                letter_groups[key] = QTreeWidgetItem(self.customer_tree, [key])
                self.customer_tree.addTopLevelItem(letter_groups[key])

            customer_item = QTreeWidgetItem(letter_groups[key], [f"{first_name} {last_name} (#{customer_id})"])
            customer_item.setData(0, Qt.UserRole, customer_id)  # Store customer ID for easy lookup
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
        self.setWindowTitle("Edit Customer")
        self.customer_id = customer_id
        
        layout = QVBoxLayout()

        # Fetch customer data
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT first_name, last_name, address, city, state, zip_code, phone, email, status FROM customers WHERE customer_id = ?",
            (customer_id,)
        )
        customer = cursor.fetchone()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                campaign_year INTEGER,
                campaign_number INTEGER,
                order_total REAL DEFAULT 0,
                previous_balance REAL DEFAULT 0,
                payment REAL DEFAULT 0,
                net_due REAL DEFAULT 0
            )
        """)
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, previous_balance, payment, net_due
            FROM orders WHERE customer_id = ? ORDER BY campaign_year DESC, campaign_number DESC LIMIT 1
        """, (customer_id,))
        order_data = cursor.fetchone()
        conn.close()

        if not customer:
            QMessageBox.critical(self, "Error", "Customer not found in database!")
            self.reject()
            return

        # Create fields
        self.first_name_input = QLineEdit(customer[0])
        self.last_name_input = QLineEdit(customer[1])
        self.address_input = QLineEdit(customer[2])
        self.city_input = QLineEdit(customer[3])
        self.state_input = QLineEdit(customer[4])
        self.zip_code_input = QLineEdit(customer[5])
        self.phone_input = QLineEdit(customer[6])
        self.email_input = QLineEdit(customer[7])

        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Closed", "Deleted"])
        self.status_input.setCurrentText(customer[8])

        # Layout fields
        layout.addWidget(QLabel("First Name:"))
        layout.addWidget(self.first_name_input)
        layout.addWidget(QLabel("Last Name:"))
        layout.addWidget(self.last_name_input)
        layout.addWidget(QLabel("Address:"))
        layout.addWidget(self.address_input)
        layout.addWidget(QLabel("City:"))
        layout.addWidget(self.city_input)
        layout.addWidget(QLabel("State:"))
        layout.addWidget(self.state_input)
        layout.addWidget(QLabel("ZIP Code:"))
        layout.addWidget(self.zip_code_input)
        layout.addWidget(QLabel("Phone:"))
        layout.addWidget(self.phone_input)
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Status:"))
        layout.addWidget(self.status_input)

        # Order Summary Section
        order_group = QGroupBox("Order Summary (Current Campaign)")
        order_layout = QVBoxLayout()

        # Use current campaign settings from options_window
        current_year, current_campaign = get_current_campaign_settings()       
        self.order_year = QLabel(f"Campaign Year: {current_year}")
        self.order_campaign = QLabel(f"Campaign Number: {current_campaign}")

        # Populate order summary based on order_data if it exists
        if order_data:
            self.order_total = QLabel(f"Order Total: ${order_data[2]:.2f}")
            self.previous_balance = QLabel(f"Previous Balance: ${order_data[3]:.2f}")
            self.payment = QLabel(f"Payment: ${order_data[4]:.2f}")
            self.net_due = QLabel(f"Net Due: ${order_data[5]:.2f}")
        else:
            self.order_total = QLabel("Order Total: $0.00")
            self.previous_balance = QLabel("Previous Balance: $0.00")
            self.payment = QLabel("Payment: $0.00")
            self.net_due = QLabel("Net Due: $0.00")

        self.time_submitted_label = QLabel("Time Submitted: N/A")
        self.last_edited_label = QLabel("Last Edited: N/A")

        order_layout.addWidget(self.order_year)
        order_layout.addWidget(self.order_campaign)
        order_layout.addWidget(self.order_total)
        order_layout.addWidget(self.previous_balance)
        order_layout.addWidget(self.payment)
        order_layout.addWidget(self.net_due)
        order_layout.addWidget(self.time_submitted_label)
        order_layout.addWidget(self.last_edited_label)         
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)

        # Order Entry Button
        self.btn_order_entry = QPushButton("New Order Entry")
        self.btn_order_entry.clicked.connect(self.open_order_entry)
        layout.addWidget(self.btn_order_entry)

        # --- Order History Section ---
        self.order_history = QComboBox()
        self.order_history.currentIndexChanged.connect(self.display_order_details)
        layout.addWidget(QLabel("Order History:"))
        layout.addWidget(self.order_history)
        self.load_order_history()

        # Refresh Order Summary Button
        btn_refresh_summary = QPushButton("Refresh Order Summary")
        btn_refresh_summary.clicked.connect(self.refresh_order_summary)
        layout.addWidget(btn_refresh_summary)

        # View Order Details Button
        self.btn_view_order = QPushButton("View Order Details")
        self.btn_view_order.clicked.connect(self.view_order_details)
        layout.addWidget(self.btn_view_order)

        # Save & Delete Buttons
        btn_save = QPushButton("Save Changes")
        btn_save.clicked.connect(self.save_customer)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def open_order_entry(self):
        """Open Order Entry Window using current campaign settings."""
        current_year, current_campaign = get_current_campaign_settings()
        self.order_entry_dialog = OrderEntryDialog(self.customer_id, current_year, current_campaign, self)
        self.order_entry_dialog.exec_()
        # Automatically refresh the summary after closing the order entry dialog
        self.refresh_order_summary()

    def refresh_order_summary(self):
        """Refresh the order summary information and Order History list for the current customer."""
        print("Refreshing order summary for customer:", self.customer_id)  # Debug print
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Note: We now select two extra columns: time_submitted and last_edited.
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, previous_balance, payment, net_due, time_submitted, last_edited
            FROM orders 
            WHERE customer_id = ? 
            ORDER BY time_submitted DESC LIMIT 1
        """, (self.customer_id,))
        order_data = cursor.fetchone()
        conn.close()
        print("Fetched order_data:", order_data)  # Debug print

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

        # Refresh the Order History list as well.
        self.load_order_history()

       
    def save_customer(self):
        """Save updated customer details to database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE customers 
            SET first_name=?, last_name=?, address=?, city=?, state=?, zip_code=?, phone=?, email=?, status=?
            WHERE customer_id=?
        """, (
            self.first_name_input.text(), self.last_name_input.text(), self.address_input.text(),
            self.city_input.text(), self.state_input.text(), self.zip_code_input.text(),
            self.phone_input.text(), self.email_input.text(), self.status_input.currentText(), self.customer_id
        ))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Customer details updated successfully!")
        self.accept()

    def load_order_history(self):
        """Load past orders for the customer into the order history combo box."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Updated: Order by time_submitted instead of order_date
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
        if order_id is None:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, previous_balance, payment, net_due
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
        if order_id is None:
            return
        # Open OrderEntryDialog with the selected order's details.
        # We pass the order_id so that the dialog knows to load existing data.
        # (The campaign_year and campaign_number parameters will be overridden by the loaded order details.)
        dialog = OrderEntryDialog(self.customer_id, 0, 0, self, order_id=order_id)
        dialog.exec_()
    
           
class AddCustomerDialog(QDialog):
    """Dialog to Add a New Customer."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer")
        
        layout = QVBoxLayout()

        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()

        layout.addWidget(QLabel("First Name:"))
        layout.addWidget(self.first_name_input)
        layout.addWidget(QLabel("Last Name:"))
        layout.addWidget(self.last_name_input)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_customer)

        layout.addWidget(btn_save)
        self.setLayout(layout)

        # Order History List
        self.order_history = QComboBox()
        self.load_order_history()  # Load previous orders on open
        layout.addWidget(QLabel("Order History:"))
        layout.addWidget(self.order_history)


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
            "Product Number", "Page", "Description", "Shade/Fragrance", "Size", "QTY",
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
        """Calculate total order price dynamically and auto-format price fields."""
        # Only auto-format if changed_item is provided.
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
                qty = float(qty_item.text()) if qty_item and qty_item.text().strip() else 0

                unit_price_item = self.order_table.item(row, 6)
                unit_price_text = unit_price_item.text() if unit_price_item and unit_price_item.text().strip() else "$0.00"
                unit_price = float(unit_price_text.replace("$", ""))

                discount_item = self.order_table.item(row, 9)
                discount = float(discount_item.text()) if discount_item and discount_item.text().strip() else 0

                # Calculate final price with discount
                final_price = (unit_price * qty) * ((100 - discount) / 100)

                # Check for tax (column 8 widget)
                tax_checkbox = self.order_table.cellWidget(row, 8)
                if tax_checkbox and tax_checkbox.isChecked():
                    final_price *= 1.1  # 10% tax

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
                    unit_price = float(self.order_table.item(row, 6).text().replace("$", ""))
                    reg_price = float(self.order_table.item(row, 7).text().replace("$", ""))
                    tax_checkbox = self.order_table.cellWidget(row, 8)
                    tax = 1 if tax_checkbox and tax_checkbox.isChecked() else 0
                    discount = float(self.order_table.item(row, 9).text())
                    total_price = float(self.order_table.item(row, 10).text().replace("$", ""))
                    
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
        """Generate a formatted order printout."""
        rep_info = get_representative_info()
        
        print_file = "order_summary.txt"
        with open(print_file, "w") as f:
            f.write(" " * 20 + "AVON BY MONICA\n")
            f.write(" " * 18 + "*** CUSTOMER ORDER ***\n\n")

            f.write(f"Campaign # {self.campaign_number} \n")
            f.write(f"{self.order_date}\n\n")

            # Use representative details from the database
            f.write(f"Campaign # {self.campaign_number} - {self.campaign_year}\n")
            f.write("Tuesday, January 28, 2025\n\n")
            f.write(f"{rep_info['rep_name']}\n")
            f.write(f"{rep_info['rep_address']}\n")
            f.write(f"{rep_info['rep_phone']}\n")
            f.write(f"Email: {rep_info['rep_email']}\n")
            f.write(f"Website: {rep_info['rep_website']}\n\n")

            # Column headers
            f.write(f"{'Page':<8}{'Product #':<12}{'Product':<40}{'Qty':>6}{'Price':>10}{'Total':>10}\n")
            f.write("-" * 90 + "\n")

            total_price = 0
            for row in range(self.order_table.rowCount()):
                page = self.order_table.item(row, 1).text() if self.order_table.item(row, 1) else ""
                product_number = self.order_table.item(row, 0).text() if self.order_table.item(row, 0) else ""
                description = self.order_table.item(row, 2).text() if self.order_table.item(row, 2) else ""
                qty = self.order_table.item(row, 5).text() if self.order_table.item(row, 5) else "0"
                price = self.order_table.item(row, 6).text() if self.order_table.item(row, 6) else "$0.00"
                total = self.order_table.item(row, 10).text() if self.order_table.item(row, 10) else "$0.00"

                f.write(f"{page:<8}{product_number:<12}{description:<40}{qty:>6}{price:>10}{total:>10}\n")
                total_price += float(total.replace("$", ""))

            f.write("-" * 90 + "\n")
            processing_charge = 0.50
            tax_rate = 9.386 / 100
            tax_amount = total_price * tax_rate
            grand_total = total_price + processing_charge + tax_amount

            f.write(f"{'':<60}{'Sub Total':<15}${total_price:.2f}\n")
            f.write(f"{'':<60}{'Processing Charge':<15}${processing_charge:.2f}\n")
            f.write(f"{'':<60}{'TAX1 9.386%':<15}${tax_amount:.2f}\n")
            f.write(f"{'':<60}{'Grand Total':<15}${grand_total:.2f}\n\n")

            f.write(" " * 30 + "Thank You\n")
            f.write("_" * 90 + "\n")

        import os
        os.startfile(print_file, "print")
        QMessageBox.information(self, "Print", "Order sent to printer!")