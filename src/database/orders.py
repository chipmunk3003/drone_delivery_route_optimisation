from database.database import get_connection


def clear_orderInfo():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders')
    cursor.execute('DELETE FROM orderLine')
    conn.commit()
    conn.close()


def create_order(latitude, longitude, weight, time_placed):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO orders (deliveryLat, deliveryLong, orderWeight, timeOrderPlaced)
        VALUES (?,?,?,?)''', (latitude, longitude, weight, time_placed)
    )
    conn.commit()
    conn.close()


def add_order_line(orderId, productId, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO orderLine(orderId, productId, quantity)
        VALUES (?,?,?)''', (orderId, productId, quantity)
    )
    conn.commit()
    conn.close()



def get_order(orderId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT orderWeight, orderId, timeOrderPlaced FROM orders WHERE orderId = ?",(orderId,))
    orderWeight, orderId, timeOrderPlaced = cursor.fetchone()
    print(orderWeight)
    conn.commit()
    conn.close()

    return orderWeight, orderId, timeOrderPlaced


def get_order_by_location(latitude, longitude):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT orderId FROM orders WHERE deliveryLat = ? AND deliveryLong = ?",(latitude,longitude))
    orderId = cursor.fetchone()
    conn.commit()
    conn.close()

    return orderId


def get_order_items(orderId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, orderLine.quantity
        FROM orderLine
        JOIN products ON orderLine.productId = products.productId
        WHERE orderLine.orderId = ?;
    """, (orderId,))
    items = cursor.fetchall()
    conn.commit()
    conn.close()

    return items


def get_order_location(orderId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT deliveryLat, deliveryLong FROM orders WHERE orderId = ?", (orderId,))
    coords = cursor.fetchone()
    conn.commit()
    conn.close()

    return coords


def get_product_quantity_in_order(orderId, productId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM orderLine WHERE orderId = ? AND productId = ?", (orderId, productId))
    quant = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return quant


