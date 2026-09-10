from database.database import get_connection


def get_warehouse_stock(stockNum):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f'''SELECT products.name, {stockNum}.numAvailable
        FROM products 
		INNER JOIN {stockNum} ON products.productId = {stockNum}.productId;'''
    )
    warehouseNumbers = cursor.fetchall()
    conn.commit()
    conn.close()

    return warehouseNumbers


def update_stock(stockNum, quantity, productId):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f'''UPDATE {stockNum}
        SET numAvailable = ?
        WHERE productId = ?''',
        (quantity, productId)
    )
    conn.commit()
    conn.close()


def get_product_weights():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT weight FROM products')
    weights = cursor.fetchall()
    conn.commit()
    conn.close()

    return weights


def get_num_available_weights(stockNum):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''SELECT {stockNum}.numAvailable, products.weight
                    FROM products
                    JOIN {stockNum} ON products.productId = {stockNum}.productId''')
    warehouseNumbers = cursor.fetchall()
    conn.commit()
    conn.close()

    return warehouseNumbers

def get_num_available(stockNum):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f'''SELECT numAvailable FROM {stockNum}''')
    warehouseStock = cursor.fetchall()
    conn.commit()
    conn.close()
    
    return warehouseStock