import sqlite3

DB_PATH = "avon_hello.db"

def add_processing_column_to_order_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🔧 Ensuring 'processing' column exists in order_products...")

    try:
        cursor.execute("ALTER TABLE order_products ADD COLUMN processing INTEGER DEFAULT 0")
        print("✅ Added 'processing' column to order_products.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ 'processing' column already exists.")
        else:
            print("⚠️ Error adding 'processing' column:", e)

    conn.commit()
    conn.close()

    print("✅ 'customers' table updated successfully!")

if __name__ == "__main__":
    add_processing_column_to_order_products()
