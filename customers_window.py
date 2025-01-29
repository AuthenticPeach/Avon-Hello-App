from PyQt5.QtCore import Qt
import sqlite3
import os

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QTreeWidget, 
    QTreeWidgetItem, QWidget, QLabel, QLineEdit, QHBoxLayout, 
    QRadioButton, QMessageBox, QDialog, QComboBox, QGroupBox,
    QCheckBox, QTableWidget, QHeaderView, QTableWidgetItem
)

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
        cursor.execute("SELECT first_name, last_name, address, city, state, zip_code, phone, email, status FROM customers WHERE customer_id = ?", (customer_id,))
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
        order_group = QGroupBox("Order Summary (Latest Campaign)")
        order_layout = QVBoxLayout()

        if order_data:
            self.order_year = QLabel(f"Campaign Year: {order_data[0]}")
            self.order_campaign = QLabel(f"Campaign Number: {order_data[1]}")
            self.order_total = QLabel(f"Order Total: ${order_data[2]:.2f}")
            self.previous_balance = QLabel(f"Previous Balance: ${order_data[3]:.2f}")
            self.payment = QLabel(f"Payment: ${order_data[4]:.2f}")
            self.net_due = QLabel(f"Net Due: ${order_data[5]:.2f}")
        else:
            self.order_year = QLabel("Campaign Year: N/A")
            self.order_campaign = QLabel("Campaign Number: N/A")
            self.order_total = QLabel("Order Total: $0.00")
            self.previous_balance = QLabel("Previous Balance: $0.00")
            self.payment = QLabel("Payment: $0.00")
            self.net_due = QLabel("Net Due: $0.00")

        order_layout.addWidget(self.order_year)
        order_layout.addWidget(self.order_campaign)
        order_layout.addWidget(self.order_total)
        order_layout.addWidget(self.previous_balance)
        order_layout.addWidget(self.payment)
        order_layout.addWidget(self.net_due)

        order_group.setLayout(order_layout)
        layout.addWidget(order_group)

        # Order Entry Button
        self.btn_order_entry = QPushButton("Order Entry")
        self.btn_order_entry.clicked.connect(self.open_order_entry)
        layout.addWidget(self.btn_order_entry)

        # Save & Delete Buttons
        btn_save = QPushButton("Save Changes")
        btn_save.clicked.connect(self.save_customer)

        layout.addWidget(btn_save)
        self.setLayout(layout)

    def open_order_entry(self):
        """Open Order Entry Window."""
        self.order_entry_dialog = OrderEntryDialog(self.customer_id, self)
        self.order_entry_dialog.exec_()

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
        """Load past orders for the customer."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_year, campaign_number, order_total, previous_balance, payment, net_due
            FROM orders WHERE customer_id = ?
            ORDER BY campaign_year DESC, campaign_number DESC
        """, (self.customer_id,))
        orders = cursor.fetchall()
        conn.close()

        if orders:
            self.order_history.clear()
            for order in orders:
                self.order_history.addItem(
                    f"Campaign {order[1]} ({order[0]}): Total ${order[2]:.2f}, Due ${order[5]:.2f}"
                )


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
    
    def __init__(self, customer_id, campaign_year, campaign_number, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Order Entry")
        self.setGeometry(300, 200, 1000, 500)
        self.customer_id = customer_id
        self.campaign_year = campaign_year  # Store campaign year
        self.campaign_number = campaign_number  # Store campaign number

        layout = QVBoxLayout()

        # Order Table
        self.order_table = QTableWidget(0, 10)  # Start with 0 rows, 10 columns
        self.order_table.setHorizontalHeaderLabels([
            "Product Number", "Page", "Description", "Shade/Fragrance", "Size", "QTY",
            "Unit Price", "Reg Price", "Tax", "Discount %", "Total Price"
        ])
        self.order_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.order_table)

        # Buttons for Actions
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

        # Total Order Summary
        self.total_label = QLabel("Total: $0.00")
        layout.addWidget(self.total_label)

        self.setLayout(layout)

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

    def update_total(self):
        """Calculate total order price dynamically, ensuring all fields exist."""
        total = 0.0
        for row in range(self.order_table.rowCount()):
            try:
                qty_item = self.order_table.item(row, 5)
                qty = float(qty_item.text()) if qty_item and qty_item.text().strip() else 0

                unit_price_item = self.order_table.item(row, 6)
                unit_price = float(unit_price_item.text().replace("$", "")) if unit_price_item and unit_price_item.text().strip() else 0.0

                discount_item = self.order_table.item(row, 9)
                discount = float(discount_item.text()) if discount_item and discount_item.text().strip() else 0

                # Calculate discounted price
                final_price = (unit_price * qty) * ((100 - discount) / 100)

                # Check if tax is applied
                tax_checkbox = self.order_table.cellWidget(row, 8)
                if tax_checkbox and tax_checkbox.isChecked():
                    final_price *= 1.1  # Assume 10% tax for now

                # Ensure the "Total Price" column exists before setting the value
                total_price_item = self.order_table.item(row, 10)
                if not total_price_item:
                    self.order_table.setItem(row, 10, QTableWidgetItem(f"${final_price:.2f}"))
                else:
                    total_price_item.setText(f"${final_price:.2f}")

                total += final_price
            except ValueError:
                continue  # Ignore invalid inputs

        self.total_label.setText(f"Total: ${total:.2f}")

    def save_order(self):
        """Save order to the database and update order history."""
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
                order_date TEXT DEFAULT (datetime('now', 'localtime')) -- Ensure it has a default value
            )
        """)

        # Ensure order_products table exists
        cursor.execute("""
            INSERT INTO orders (customer_id, campaign_year, campaign_number, order_total, previous_balance, payment, net_due, order_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """, (
            self.customer_id, 2025, 25, 0, 0, 0, 0
        ))

        # Insert new order
        cursor.execute("""
            INSERT INTO orders (customer_id, campaign_year, campaign_number, order_total, previous_balance, payment, net_due)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.customer_id, 2025, 25, 0, 0, 0, 0
        ))
        order_id = cursor.lastrowid  # Get the inserted order ID

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
                total_price_item = self.order_table.item(row, 10)
                total_price = float(total_price_item.text().replace("$", "")) if total_price_item else 0.00

                # Insert product into database
                cursor.execute("""
                    INSERT INTO order_products 
                    (order_id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (order_id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price))

            except ValueError:
                continue  # Ignore invalid rows

        conn.commit()
        conn.close()
        QMessageBox.information(self, "Saved", "Order saved successfully!")
        self.accept()  # Close the order entry dialog

    def open_order_entry(self):
        """Open Order Entry Window and fetch latest campaign details."""

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT campaign_year, campaign_number 
            FROM orders WHERE customer_id = ? 
            ORDER BY campaign_year DESC, campaign_number DESC LIMIT 1
        """, (self.customer_id,))
        latest_order = cursor.fetchone()
        conn.close()

        if latest_order:
            campaign_year, campaign_number = latest_order
        else:
            campaign_year, campaign_number = 2025, 1  # Default values if no order exists

        self.order_entry_dialog = OrderEntryDialog(self.customer_id, campaign_year, campaign_number, self)
        self.order_entry_dialog.exec_()

    def print_order(self):
        """Generate a formatted order printout."""
        print_file = "order_summary.txt"
        with open(print_file, "w") as f:
            f.write(" " * 20 + "AVON BY MONICA\n")
            f.write(" " * 18 + "*** CUSTOMER ORDER ***\n\n")

            f.write(f"Campaign # {self.campaign_number} \n")
            f.write(f"{self.order_date}\n\n")

            # Customer details
            f.write(f"Campaign # {self.campaign_number} - {self.campaign_year}\n")  # Now campaign details exist
            f.write("Tuesday, January 28, 2025\n\n")

            # Representative details
            f.write(f"{self.rep_name}\n")
            f.write(f"{self.rep_address}\n")
            f.write(f"{self.rep_phone}\n")
            f.write(f"Email: {self.rep_email}\n")
            f.write(f"Website: {self.rep_website}\n\n")

            # Column headers
            f.write(f"{'Page':<8}{'Product #':<12}{'Product':<40}{'Qty':>6}{'Price':>10}{'Total':>10}\n")
            f.write("-" * 90 + "\n")

            # Order items
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

            # Subtotal, processing, tax, grand total
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

        os.startfile(print_file, "print")  # Open print dialog
        QMessageBox.information(self, "Print", "Order sent to printer!")

