import asyncpg
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

USER = os.getenv("SUPABASE_USER")
PASSWORD = os.getenv("SUPABASE_PASSWORD")
HOST = os.getenv("SUPABASE_HOST")
PORT = os.getenv("SUPABASE_PORT", "5432")
DBNAME = os.getenv("SUPABASE_DBNAME")

async def get_connection():
    try:
        return await asyncpg.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DBNAME
        )
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        return None

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def get_customers():
    return run_async(_get_customers_async())

async def _get_customers_async():
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return {}
    try:
        rows = await connection.fetch(
            "SELECT c_id, c_name, c_email, c_address FROM customers;"
        )
        customers = {}
        for row in rows:
            customers[row["c_id"]] = {
                "name": row["c_name"],
                "email": row["c_email"],
                "address": row["c_address"]
            }
        await connection.close()
        return customers
    except Exception as e:
        print(f"Error fetching customers: {e}")
        await connection.close()
        return {}

def get_products():
    return run_async(_get_products_async())

async def _get_products_async():
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return {}
    try:
        rows = await connection.fetch(
            "SELECT p_id, p_name, p_price, p_stock FROM products;"
        )
        products = {}
        for row in rows:
            products[row["p_id"]] = {
                "name": row["p_name"],
                "price": float(row["p_price"]),
                "stock": row["p_stock"]
            }
        await connection.close()
        return products
    except Exception as e:
        print(f"Error fetching products: {e}")
        await connection.close()
        return {}


def get_orders():
    return run_async(_get_orders_async())

async def _get_orders_async():
    import json
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return []
    try:
        # Fetch all orders (no total_value column)
        orders = await connection.fetch(
            """
            SELECT o_id, c_id, c_name, o_delivery_date, c_address, o_remarks, o_placed_time, o_status
            FROM orders
            ORDER BY o_placed_time DESC;
            """
        )
        orders_list = []
        for order in orders:
            # Fetch order items for this order
            items = await connection.fetch(
                "SELECT oi_id, p_id, p_name, oi_qty, oi_price, oi_total, oi_is_available "
                "FROM order_items WHERE o_id = $1;",
                order["o_id"]
            )
            items_list = [dict(item) for item in items]
            # Calculate total from oi_total
            total = float(sum(item["oi_total"] for item in items))
            order_dict = dict(order)
            order_dict["items"] = items_list
            order_dict["total_value"] = total
            orders_list.append(order_dict)
        await connection.close()
        return orders_list
    except Exception as e:
        print(f"Error fetching orders: {e}")
        await connection.close()
        return []

def update_product_stock(product_id, new_stock):
    return run_async(_update_product_stock_async(product_id, new_stock))

async def _update_product_stock_async(product_id, new_stock):
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return False
    try:
        await connection.execute(
            "UPDATE products SET p_stock = $1 WHERE p_id = $2;",
            new_stock, product_id
        )
        await connection.close()
        return True
    except Exception as e:
        print(f"Error updating product stock: {e}")
        await connection.close()
        return False

def get_order_by_id(order_id):
    return run_async(_get_order_by_id_async(order_id))

async def _get_order_by_id_async(order_id):
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return None
    try:
        order_row = await connection.fetchrow(
            """
            SELECT o_id, c_id, c_name, o_delivery_date, c_address, o_remarks, o_placed_time, o_status
            FROM orders WHERE o_id = $1;
            """,
            order_id
        )
        if not order_row:
            await connection.close()
            return None
        items = await connection.fetch(
            "SELECT oi_id, p_id, p_name, oi_qty, oi_price, oi_total, oi_is_available FROM order_items WHERE o_id = $1;",
            order_id
        )
        items_list = [dict(item) for item in items]
        total = float(sum(item["oi_total"] for item in items))
        order_dict = dict(order_row)
        order_dict["items"] = items_list
        order_dict["total_value"] = total
        await connection.close()
        return order_dict
    except Exception as e:
        print(f"Error fetching order by id: {e}")
        await connection.close()
        return None

if __name__ == "__main__":
    customers = get_customers()
    print("Customers:", customers)
    products = get_products()
    print("Products:", products)