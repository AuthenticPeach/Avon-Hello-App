import sqlite3

DB_PATH = "avon_hello.db"

def update_orders_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Updating orders table with new columns if necessary...")

    # Add time_submitted column without a default.
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN time_submitted TEXT")
        print("✅ Added time_submitted column.")
        # Update existing rows with the current local datetime.
        cursor.execute("UPDATE orders SET time_submitted = datetime('now','localtime') WHERE time_submitted IS NULL")
        print("✅ Updated time_submitted values.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e) or "already exists" in str(e):
            print("ℹ️ time_submitted column already exists.")
        else:
            print("⚠️ Error adding time_submitted:", e)

    # Add last_edited column without a default.
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN last_edited TEXT")
        print("✅ Added last_edited column.")
        # Update existing rows with the current local datetime.
        cursor.execute("UPDATE orders SET last_edited = datetime('now','localtime') WHERE last_edited IS NULL")
        print("✅ Updated last_edited values.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e) or "already exists" in str(e):
            print("ℹ️ last_edited column already exists.")
        else:
            print("⚠️ Error adding last_edited:", e)

    conn.commit()
    conn.close()

def force_update_order_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Forcing order_products table update...")

    # Rename the old order_products table.
    cursor.execute("ALTER TABLE order_products RENAME TO old_order_products;")

    # Create a new order_products table with the desired schema.
    cursor.execute("""
        CREATE TABLE order_products (
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
            total_price REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)

    # Copy data from old_order_products to the new order_products table.
    # (If order_id existed in the old table, adjust accordingly.)
    cursor.execute("""
        INSERT INTO order_products (order_id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price)
        SELECT NULL, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price
        FROM old_order_products;
    """)

    # Drop the old table.
    cursor.execute("DROP TABLE old_order_products;")

    conn.commit()
    conn.close()
    print("✅ order_products table successfully updated!")

if __name__ == "__main__":
    update_orders_table()
    force_update_order_products()
