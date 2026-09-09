# make database
import sqlite3

conn = sqlite3.connect("data/my_database.db")
cursor = conn.cursor()

# array has productid, name, weight, amount in warehouse 1, amount in warehouse 2
productInfo = [(1, "Milk (500ml)", 0.515), (2, "Water bottle (500ml)", 0.51), (3, "Pasta", 0.42), (4, "Canned tuna", 0.5), (5, "Cereal", 0.425), (6, "Bread loaf", 0.565), (7, "Canned Soup", 0.450), (8, "First Aid Kit", 1.36)]

warehouse1Products = [(1, 10), (2, 5), (3, 15), (4, 15), (5, 10), (6, 3), (7, 1), (8, 4)]
warehouse2Products = [(1, 9), (2, 8), (3, 4), (4, 18), (5, 13), (6, 12), (7, 0), (8, 8)]

cursor.execute("CREATE TABLE IF NOT EXISTS stock1 (productId INTEGER PRIMARY KEY, numAvailable INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS stock2 (productId INTEGER PRIMARY KEY, numAvailable INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS products (productId INTEGER PRIMARY KEY, name STRING, weight FLOAT)")
cursor.execute("CREATE TABLE IF NOT EXISTS orders (orderId INTEGER PRIMARY KEY, deliveryLat FLOAT, deliveryLong FLOAT, orderWeight FLOAT, timeOrderPlaced INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS orderLine (productId INTEGER, orderId INTEGER, quantity INTEGER, PRIMARY KEY (productId, orderId))")

'''
cursor.executemany("INSERT INTO products (productId, name, weight) VALUES (?, ?, ?)", productInfo )
cursor.executemany("INSERT INTO stock1 (productId, numAvailable) VALUES (?, ?)", warehouse1Products)
cursor.executemany("INSERT INTO stock2 (productId, numAvailable) VALUES (?, ?)", warehouse2Products)
'''

cursor.execute("""
    SELECT
        p.productId,
        p.name,
        p.weight,
        s1.numAvailable AS warehouse1,
        s2.numAvailable AS warehouse2
    FROM products p
    JOIN stock1 s1 ON p.productId = s1.productId
    JOIN stock2 s2 ON p.productId = s2.productId
""")

for row in cursor.fetchall():
    print(row)


conn.commit()
conn.close()

