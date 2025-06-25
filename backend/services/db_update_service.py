import asyncio
from typing import Optional
from models import ValidationResult, OrderUpdateResult, OrderProduct
from db import get_connection
import asyncpg
from datetime import datetime, timedelta

class DBUpdateService:
    @staticmethod
    def update_order(validation: ValidationResult) -> OrderUpdateResult:
        try:
            result = asyncio.get_event_loop().run_until_complete(DBUpdateService._update_order_async(validation))
            return result
        except Exception as e:
            return OrderUpdateResult(success=False, order_id=None, details=f"Error: {str(e)}")

    @staticmethod
    async def _generate_order_id(conn: asyncpg.Connection) -> str:
        now = datetime.now()
        year = now.year
        prefix = f"ORD-{year}-"
        last_order_row = await conn.fetchrow(
            "SELECT o_id FROM orders WHERE o_id LIKE $1 ORDER BY o_id DESC LIMIT 1",
            f"{prefix}%"
        )
        
        if last_order_row and last_order_row['o_id']:
            try:
                last_seq = int(last_order_row['o_id'].split('-')[-1])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1
        
        order_id = f"{prefix}{new_seq:03d}"
        return order_id

    @staticmethod
    async def _update_order_async(validation: ValidationResult) -> OrderUpdateResult:
        conn: Optional[asyncpg.Connection] = None
        order_id = None
        details = []
        try:
            conn = await get_connection()
            if not conn:
                return OrderUpdateResult(success=False, details="Database connection failed.")
            async with conn.transaction():
                if validation.overall_status.lower() in ["success", "confirmed"]:
                    for item in validation.successful_items:
                        stock_row = await conn.fetchrow("SELECT p_stock FROM products WHERE p_id = $1 FOR UPDATE;", item.product_id)
                        if not stock_row:
                            raise Exception(f"Product {item.product_id} not found.")
                        current_stock = stock_row["p_stock"]
                        if item.quantity > current_stock:
                            raise Exception(f"Insufficient stock for product {item.product_id} during update.")
                        await conn.execute(
                            "UPDATE products SET p_stock = p_stock - $1 WHERE p_id = $2;",
                            item.quantity, item.product_id
                        )
                        details.append(f"Updated stock for {item.product_id} (-{item.quantity})")
                    
                    customer_id = validation.customer_info.get("id")
                    if not customer_id:
                        return OrderUpdateResult(success=False, order_id=None, details="Customer ID is missing in validation result. Cannot create order record.")
                    customer_name = validation.customer_info.get("name")
                    customer_address = validation.customer_info.get("address")
                    status = "Confirmed"
                    now = datetime.now()
                    o_placed_time = now
                    o_delivery_date = now + timedelta(days=3)

                    order_id = await DBUpdateService._generate_order_id(conn)

                    await conn.execute(
                        """
                        INSERT INTO orders (o_id, c_id, c_name, c_address, o_status, o_placed_time, o_delivery_date)
                        VALUES ($1, $2, $3, $4, $5, $6, $7);
                        """,
                        order_id, customer_id, customer_name, customer_address, status, o_placed_time, o_delivery_date
                    )

                    for item in validation.successful_items:
                        prod_row = await conn.fetchrow("SELECT p_name, p_price FROM products WHERE p_id = $1;", item.product_id)
                        p_name = prod_row["p_name"]
                        p_price = prod_row["p_price"]
                        oi_total = p_price * item.quantity
                        await conn.execute(
                            """
                            INSERT INTO order_items (o_id, p_id, p_name, oi_qty, oi_price, oi_total, oi_is_available)
                            VALUES ($1, $2, $3, $4, $5, $6, $7);
                            """,
                            order_id, item.product_id, p_name, item.quantity, p_price, oi_total, True
                        )
                        details.append(f"Created order item for {item.product_id} (qty {item.quantity})")
                    return OrderUpdateResult(success=True, order_id=str(order_id), details="; ".join(details))
                else:
                    status = "Hold" if validation.overall_status.lower() in ["partial_success", "unknown_customer"] else "Failed"
                    customer_id = validation.customer_info.get("id")
                    if not customer_id:
                        return OrderUpdateResult(success=False, order_id=None, details="Customer ID is missing in validation result. Cannot create order record.")
                    customer_name = validation.customer_info.get("name")
                    customer_address = validation.customer_info.get("address")
                    now = datetime.now()
                    o_placed_time = now
                    o_delivery_date = now + timedelta(days=3)

                    order_id = await DBUpdateService._generate_order_id(conn)

                    await conn.execute(
                        """
                        INSERT INTO orders (o_id, c_id, c_name, c_address, o_status, o_placed_time, o_delivery_date)
                        VALUES ($1, $2, $3, $4, $5, $6, $7);
                        """,
                        order_id, customer_id, customer_name, customer_address, status, o_placed_time, o_delivery_date
                    )
                    
                    details.append(f"Order created with status {status}")
                    return OrderUpdateResult(success=False, order_id=str(order_id), details="; ".join(details))
        except Exception as e:
            if conn:
                await conn.rollback()
            return OrderUpdateResult(success=False, order_id=str(order_id) if order_id else None, details=f"Error: {str(e)}")
        finally:
            if conn:
                await conn.close() 