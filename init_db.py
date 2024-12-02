import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Zaid@017",
        database="invoices",
        auth_plugin='mysql_native_password'
    )

def create_table():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                slot VARCHAR(50),
                total DECIMAL(10, 2),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("Table created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def process_order(order_id, slot, total):
    # Logic to process the order
    # ...

    # Automatically store invoice details in the database
    insert_invoice(order_id, slot, total)

def insert_invoice(order_id, slot, total):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO invoices (order_id, slot, total)
            VALUES (%s, %s, %s)
        """, (order_id, slot, total))
        connection.commit()
        print(f"Invoice for order {order_id} inserted successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Example usage: Process an order and automatically store the invoice
process_order("order_id", 'slot', "total")