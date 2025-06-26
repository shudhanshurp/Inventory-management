import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from datetime import timezone

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
    from datetime import datetime
    print("[DB] _get_orders_async: Fetching all orders with items.")
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return []
    try:
        print("[DB] _get_orders_async: Executing orders fetch.")
        # asyncpg automatically returns timezone-aware datetime objects for TIMESTAMPTZ columns
        orders = await connection.fetch(
            """
            SELECT o_id, c_id, c_name, o_delivery_date, c_address, o_placed_time, o_status
            FROM orders
            ORDER BY o_placed_time DESC;
            """
        )
        orders_list = []
        for order in orders:
            # print(f"[DB] _get_orders_async: Fetching items for order {order['o_id']}")
            items = await connection.fetch(
                "SELECT p_id, p_name, oi_qty, oi_price, oi_total FROM order_items WHERE o_id = $1;",
                order["o_id"]
            )
            items_list = [
                {
                    "p_id": item["p_id"],
                    "p_name": item["p_name"],
                    "oi_qty": item["oi_qty"],
                    "oi_price": float(item["oi_price"]),
                    "oi_total": float(item["oi_total"])
                }
                for item in items
            ]
            total = float(sum(item["oi_total"] for item in items))
            order_dict = {
                "o_id": order["o_id"],
                "c_id": order["c_id"],
                "c_name": order.get("c_name", ""),
                "c_address": order.get("c_address", ""),
                "o_delivery_date": order.get("o_delivery_date") or datetime(1970, 1, 1),
                "o_placed_time": order["o_placed_time"],
                "total_value": total,
                "o_status": order["o_status"],
                "items": items_list
            }
            # print(f"[DB] _get_orders_async: Order {order_dict['o_id']} customer info: {order_dict.get('c_name')}, {order_dict.get('c_address')}")
            orders_list.append(order_dict)
        print("[DB] _get_orders_async: Closing connection after orders fetch.")
        await connection.close()
        print(f"[DB] _get_orders_async: Returning {len(orders_list)} orders.")
        return orders_list
    except Exception as e:
        print(f"[DB] Error in _get_orders_async: {e}")
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
    order = run_async(_get_order_by_id_async(order_id))
    # Ensure required fields are present and not None
    if order is not None:
        if 'c_name' not in order or order['c_name'] is None:
            order['c_name'] = ''
        if 'c_address' not in order or order['c_address'] is None:
            order['c_address'] = ''
        if 'o_delivery_date' not in order or order['o_delivery_date'] is None:
            from datetime import datetime
            order['o_delivery_date'] = datetime(1970, 1, 1)
    print(f"[DB] get_order_by_id returning: {order}")
    return order

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

# New: async function to fetch all customers as dict with c_created_time
async def _get_all_customers_dict_async():
    from datetime import datetime
    print("[DB] _get_all_customers_dict_async: Fetching all customers.")
    connection = await get_connection()
    if not connection:
        print("Database connection failed.")
        return {}
    try:
        print("[DB] _get_all_customers_dict_async: Executing customers fetch.")
        # asyncpg automatically returns timezone-aware datetime objects for TIMESTAMPTZ columns
        rows = await connection.fetch(
            "SELECT c_id, c_name, c_email, c_address, c_created_time FROM customers;"
        )
        customers = {}
        for row in rows:
            customers[row["c_id"]] = {
                "name": row["c_name"],
                "email": row["c_email"],
                "address": row["c_address"],
                "created_time": row["c_created_time"]  # Already timezone-aware from asyncpg
            }
        print("[DB] _get_all_customers_dict_async: Closing connection after customers fetch.")
        await connection.close()
        print(f"[DB] _get_all_customers_dict_async: Returning {len(customers)} customers.")
        return customers
    except Exception as e:
        print(f"[DB] Error in _get_all_customers_dict_async: {e}")
        await connection.close()
        return {}

# Synchronous wrapper for _get_all_customers_dict_async

def get_all_customers_dict():
    return run_async(_get_all_customers_dict_async())

if __name__ == "__main__":
    customers = get_customers()
    print("Customers:", customers)
    products = get_products()
    print("Products:", products)