import sqlite3

DB_PATH = "avon_hello.db"

def update_customers_phone_fields():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔄 Updating 'customers' table to include 'cell_phone' and 'office_phone'...")

    # Step 1: Check if the columns already exist
    cursor.execute("PRAGMA table_info(customers)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    if "cell_phone" in existing_columns and "office_phone" in existing_columns:
        print("ℹ️ 'cell_phone' and 'office_phone' already exist. No changes needed.")
        conn.close()
        return

    # Step 2: Rename original table
    cursor.execute("ALTER TABLE customers RENAME TO old_customers")

    # Step 3: Create new table with updated schema
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            cell_phone TEXT,
            office_phone TEXT,
            email TEXT,
            status TEXT
        )
    """)

    # Step 4: Copy data from old table to new one
    if "cell_phone" in existing_columns and "office_phone" in existing_columns:
        cursor.execute("""
            INSERT INTO customers (customer_id, first_name, last_name, address, city, state, zip_code, cell_phone, office_phone, email, status)
            SELECT customer_id, first_name, last_name, address, city, state, zip_code, cell_phone, office_phone, email, status
            FROM old_customers
        """)
    else:
        cursor.execute("""
            INSERT INTO customers (customer_id, first_name, last_name, address, city, state, zip_code, cell_phone, office_phone, email, status)
            SELECT customer_id, first_name, last_name, address, city, state, zip_code, phone, '', email, status
            FROM old_customers
        """)

    # Step 5: Drop old table
    cursor.execute("DROP TABLE old_customers")

    conn.commit()
    conn.close()
    print("✅ 'customers' table updated successfully!")

if __name__ == "__main__":
    update_customers_phone_fields()
