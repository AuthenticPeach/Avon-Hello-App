import sqlite3

DB_PATH = "avon_hello.db"

def force_update_order_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Forcing order_products table update...")

    # Rename old order_products table
    cursor.execute("ALTER TABLE order_products RENAME TO old_order_products;")

    # Create a new order_products table with the correct schema
    cursor.execute("""
        CREATE TABLE order_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,  -- This was missing!
            product_number TEXT,
            page INTEGER,
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

    # Copy data from old_order_products to new order_products table
    cursor.execute("""
        INSERT INTO order_products (id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price)
        SELECT id, product_number, page, description, shade, size, qty, unit_price, reg_price, tax, discount, total_price FROM old_order_products;
    """)

    # Drop the old table
    cursor.execute("DROP TABLE old_order_products;")

    conn.commit()
    conn.close()
    print("✅ order_products table successfully updated!")

if __name__ == "__main__":
    force_update_order_products()
