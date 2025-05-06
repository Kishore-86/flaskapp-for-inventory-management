from flask import Flask, render_template, request, redirect, url_for
import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from utils import generate_id

app = Flask(__name__)

db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        product_id = generate_id('pd')
        name = request.form['name']
        quantity = request.form['quantity']
        price = request.form['price']
        cursor.execute("INSERT INTO product VALUES (%s, %s, %s, %s)", (product_id, name, quantity, price))
        db.commit()
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    return render_template('product.html', products=products)

@app.route('/location', methods=['GET', 'POST'])
def location():
    if request.method == 'POST':
        location_id = generate_id('lc')
        name = request.form['name']
        cursor.execute("INSERT INTO location VALUES (%s, %s)", (location_id, name))
        db.commit()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    return render_template('location.html', locations=locations)

@app.route('/movement', methods=['GET', 'POST'])
def movement():
    cursor.execute("SELECT * FROM product")
    products = cursor.fetchall()
    cursor.execute("SELECT * FROM location")
    locations = cursor.fetchall()
    message = None

    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location'] or None
        to_location = request.form['to_location'] or None
        qty = int(request.form['qty'])

        cursor.execute("SELECT quantity FROM product WHERE product_id = %s", (product_id,))
        result = cursor.fetchone()
        available_qty = result[0] if result else 0

        if from_location and qty > available_qty:
            message = f"Error: Only {available_qty} units available. Cannot move {qty} units."
        else:
            cursor.execute("""
                INSERT INTO productmovement (product_id, from_location, to_location, qty)
                VALUES (%s, %s, %s, %s)
            """, (product_id, from_location, to_location, qty))

            if from_location:
                cursor.execute("UPDATE product SET quantity = quantity - %s WHERE product_id = %s", (qty, product_id))
            if to_location and not from_location:
                cursor.execute("UPDATE product SET quantity = quantity + %s WHERE product_id = %s", (qty, product_id))

            db.commit()
            message = "Movement recorded successfully."

    cursor.execute("""
        SELECT 
            m.movement_id, 
            m.timestamp, 
            p.name, 
            lf.name AS from_location, 
            lt.name AS to_location, 
            m.qty
        FROM productmovement m
        JOIN product p ON m.product_id = p.product_id
        LEFT JOIN location lf ON m.from_location = lf.location_id
        LEFT JOIN location lt ON m.to_location = lt.location_id
        ORDER BY m.timestamp DESC
    """)
    movements = cursor.fetchall()
    return render_template('movement.html', products=products, locations=locations, movements=movements, message=message)

@app.route('/report')
def report():
    query = """
        SELECT
            p.product_id,
            p.name AS product_name,
            l.name AS location_name,
            SUM(
                CASE
                    WHEN m.to_location = l.location_id THEN m.qty
                    WHEN m.from_location = l.location_id THEN -m.qty
                    ELSE 0
                END
            ) AS qty
        FROM product p
        JOIN productmovement m ON p.product_id = m.product_id
        JOIN location l ON l.location_id = m.to_location OR l.location_id = m.from_location
        GROUP BY p.product_id, p.name, l.location_id, l.name
        HAVING qty >= 0
        ORDER BY p.product_id, l.name
    """
    cursor.execute(query)
    report_data = cursor.fetchall()
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
