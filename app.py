from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample menu items
menu_items = [
    {"id": 1, "name": "Burger", "price": 150},
    {"id": 2, "name": "Pizza", "price": 300},
    {"id": 3, "name": "Pasta", "price": 250},
    {"id": 4, "name": "Coke", "price": 50},
]

# Store orders
orders = {}
invoice_id = 1

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Zaid@017",
        database="invoices",
        auth_plugin='mysql_native_password'
    )

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
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def generate_upi_qr(amount, upi_id, name="ChaiPatti", note="Food Payment"):
    """Generate UPI QR code with payment details"""
    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&tn={note}&cu=INR"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_str

@app.route("/")
def index():
    table = request.args.get('table')
    return render_template("index.html", menu=menu_items, table=table)

@app.route("/billing", methods=["POST"])
def billing_page():
    global invoice_id
    order = request.json
    total_price = sum(item["price"] * item["quantity"] for item in order["items"])
    
    orders[invoice_id] = {
        "items": order["items"],
        "total": total_price,
        "status": "pending",
        "tableNo": order.get("tableNo", "Unknown")
    }

    print(f"Processing order: {orders[invoice_id]}")
    insert_invoice(invoice_id, orders[invoice_id]["tableNo"], total_price)
    response = {"invoice_id": invoice_id, "total": total_price}
    invoice_id += 1
    return jsonify(response)

@app.route("/order-status/<int:order_id>")
def order_status(order_id):
    tableNo = orders.get(order_id, {}).get("tableNo", "Unknown")
    return render_template("order_status.html", table=tableNo)

@app.route("/get-order-status/<int:order_id>")
def get_order_status(order_id):
    if order_id in orders:
        return jsonify(orders[order_id])
    return jsonify({"status": "error", "message": "Order not found"}), 404

@app.route("/complete-order/<int:order_id>", methods=["POST"])
def complete_order(order_id):
    if order_id in orders:
        orders[order_id]["status"] = "Ready"
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Order not found"}), 404

@app.route("/invoice/<int:order_id>")
def invoice(order_id):
    if order_id not in orders:
        return "Order not found", 404
        
    order = orders[order_id]
    return render_template(
        "invoice.html", 
        order=order, 
        order_id=order_id,
        table=order.get("tableNo", "Unknown")
    )

@app.route("/verify-payment/<int:order_id>", methods=["POST"])
def verify_payment(order_id):
    """Verify payment status (this would typically integrate with a payment gateway API)"""
    payment_status = request.form.get('status', 'failed')
    
    if payment_status == 'success':
        # Update order status in database
        orders[order_id]['status'] = 'completed'
        insert_invoice(order_id, orders[order_id]['tableNo'], orders[order_id]['total'])
        return jsonify({"status": "success", "message": "Payment successful"})
    else:
        return jsonify({"status": "failed", "message": "Payment failed"})

@app.route("/kitchen")
def kitchen():
    return render_template("kitchen_order.html")

@app.route("/waiter-orders")
def waiter_orders():
    return jsonify({"status": "success", "orders": orders})

@app.route("/waiter-order-status")
def waiter_order_status():
    return render_template("waiter_order_status.html", orders=orders)

@app.route("/waiter-view")
def waiter_view():
    return render_template("waiter_view.html", orders=orders)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
