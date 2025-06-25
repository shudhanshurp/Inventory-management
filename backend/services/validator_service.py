from typing import List, Optional
from models import ExtractedOrderInfo, ValidationResult, ValidationErrorItem, OrderProduct
from db import get_customers, get_products

class ValidatorService:
    @staticmethod
    def validate_order(info: ExtractedOrderInfo) -> ValidationResult:
        customers = get_customers()
        products_db = get_products()
        error_items: List[ValidationErrorItem] = []
        successful_items: List[OrderProduct] = []
        suggestions: List[str] = []
        customer_info = {}
        overall_status = "success"
        unknown_customer = False

        # 1. Check customer
        customer_id = info.customer_id
        customer_email = info.customer_email
        customer_found = False
        matched_customer_id = None
        if customer_id and customer_id in customers:
            matched_customer_id = customer_id
            cinfo = customers[customer_id]
            customer_info = {
                "id": matched_customer_id,
                "name": cinfo.get("name"),
                "email": cinfo.get("email"),
                "address": cinfo.get("address"),
            }
            customer_found = True
        elif customer_email:
            # Try to match by email
            for cid, cinfo in customers.items():
                if cinfo.get("email") == customer_email:
                    matched_customer_id = cid
                    customer_info = {
                        "id": matched_customer_id,
                        "name": cinfo.get("name"),
                        "email": cinfo.get("email"),
                        "address": cinfo.get("address"),
                    }
                    customer_found = True
                    break
        if not customer_found:
            overall_status = "unknown_customer"
            error_items.append(ValidationErrorItem(product_id="*", error="Customer not found in database."))
            unknown_customer = True
            customer_info = {
                "id": None,
                "name": None,
                "email": customer_email,
                "address": None,
            }

        # 2. Validate products
        for order_product in info.products:
            prod = products_db.get(order_product.product_id)
            used_product_id = order_product.product_id
            # If not found by product_id, try matching by product_name (case-insensitive)
            if not prod:
                for pid, p in products_db.items():
                    if p["name"].strip().lower() == order_product.product_name.strip().lower():
                        prod = p
                        used_product_id = pid
                        break
            if not prod:
                error_items.append(ValidationErrorItem(
                    product_id=order_product.product_id,
                    error=f"Product '{order_product.product_id}'/'{order_product.product_name}' not found in database."
                ))
                # Suggest similar products (by name)
                similar = [p for p in products_db.values() if order_product.product_name.lower() in p["name"].lower()]
                if similar:
                    suggestions.append(f"Consider: {', '.join([s['name'] for s in similar])}")
                continue
            # Check min quantity
            min_qty = prod.get("min_quantity", 1)  # Default to 1 if not present
            if order_product.quantity < min_qty:
                error_items.append(ValidationErrorItem(
                    product_id=used_product_id,
                    error=f"Ordered quantity for product {prod['name']} is below the minimum order quantity of {min_qty}."
                ))
                continue
            # Check stock
            stock = prod.get("stock", 0)
            if order_product.quantity > stock:
                error_items.append(ValidationErrorItem(
                    product_id=used_product_id,
                    error=f"Ordered quantity for product {prod['name']} exceeds available stock ({stock} units left)."
                ))
                # Suggest alternatives if out of stock
                alternatives = [p for p in products_db.values() if p["stock"] > 0 and p["name"] != prod["name"]]
                if alternatives:
                    suggestions.append(f"Alternatives for {prod['name']}: {', '.join([a['name'] for a in alternatives])}")
                continue
            # If all checks pass, use the matched product_id
            successful_items.append(OrderProduct(
                product_id=used_product_id,
                product_name=prod["name"],
                quantity=order_product.quantity
            ))

        # 3. Set overall status
        if unknown_customer:
            overall_status = "unknown_customer"
        elif len(successful_items) == 0:
            overall_status = "failure"
        elif len(successful_items) < len(info.products):
            overall_status = "partial_success"
        else:
            overall_status = "success"

        return ValidationResult(
            customer_info=customer_info,
            successful_items=successful_items,
            error_items=error_items,
            suggestions=suggestions if suggestions else None,
            overall_status=overall_status,
            total_items=len(info.products),
            successful_count=len(successful_items),
            error_count=len(error_items)
        ) 