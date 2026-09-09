from database.database import get_connection


def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute()


def get_warehouse_stock(stockNum):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f'''SELECT products.name, {stockNum}.numAvailable
        FROM products 
		INNER JOIN {stockNum} ON products.productId = {stockNum}.productId;'''
        )
    warehouseNumbers = cursor.fetchall()
    return warehouseNumbers


def get_total_stock():
    ...


def update_stock(warehouse, product_id, quantity):
    ...


def reset_stock(stock1, stock2):
    ...


def get_product_weights():
    ...