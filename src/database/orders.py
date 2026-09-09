from database.database import get_connection


def create_order(latitude, longitude, weight, time_placed):
    ...


def add_order_line(order_id, product_id, quantity):
    ...


def get_order(order_id):
    ...


def get_order_by_location(latitude, longitude):
    ...


def get_order_items(order_id):
    ...


def get_pending_orders():
    ...
