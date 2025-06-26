import json
import random
import google.generativeai as genai
from typing import Callable
from config import Config
from models import ExtractedOrderInfo, OrderProduct
from db import get_customers, get_products

class TestCaseGeneratorService:
    def __init__(self, get_customers_func: Callable, get_products_func: Callable):
        self.get_customers_func = get_customers_func
        self.get_products_func = get_products_func
        
        # Initialize Google Generative AI
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        # Cache customers and products locally
        print("[TestCaseGeneratorService] Initializing and caching data...")
        self.customers = self.get_customers_func()
        self.products = self.get_products_func()
        print(f"[TestCaseGeneratorService] Cached {len(self.customers)} customers and {len(self.products)} products.")

    def _pick_random_product(self, num_products: int, must_exist: bool = True) -> list:
        """Pick num_products random products from cached self.products."""
        if must_exist:
            available_products = list(self.products.keys())
            if len(available_products) < num_products:
                num_products = len(available_products)
            selected_ids = random.sample(available_products, num_products)
            return [
                {
                    "p_id": p_id,
                    "p_name": self.products[p_id]["name"],
                    "quantity": random.randint(1, 5)
                }
                for p_id in selected_ids
            ]
        else:
            # Include non-existent products
            available_products = list(self.products.keys())
            if len(available_products) >= num_products:
                selected_ids = random.sample(available_products, num_products - 1)
                selected_ids.append("p999")  # Non-existent product
            else:
                selected_ids = available_products + ["p999", "p998"][:num_products - len(available_products)]
            
            return [
                {
                    "p_id": p_id,
                    "p_name": self.products[p_id]["name"] if p_id in self.products else f"Unknown Product {p_id}",
                    "quantity": random.randint(1, 5)
                }
                for p_id in selected_ids
            ]

    def _pick_random_customer(self, must_exist: bool = True) -> dict:
        """Pick a random customer from cached self.customers."""
        if must_exist and self.customers:
            customer_id = random.choice(list(self.customers.keys()))
            customer_data = self.customers[customer_id]
            return {
                "id": customer_id,
                "name": customer_data["name"],
                "email": customer_data["email"]
            }
        else:
            return {
                "id": "c999",
                "name": "Unknown User",
                "email": "unknown@example.com"
            }

    async def generate_test_cases(self) -> list[dict]:
        """Generate 5 test cases with different scenarios."""
        try:
            print("[TestCaseGeneratorService] Generating test cases...")
            
            test_cases = []
            
            # Case 1: Valid order with 1-2 random existing products
            customer1 = self._pick_random_customer(must_exist=True)
            products1 = self._pick_random_product(random.randint(1, 2), must_exist=True)
            
            test_cases.append({
                "type": "Valid",
                "description": "Standard order with existing items and customer.",
                "subject": f"Order Request - {customer1['name']}",
                "body": f"""Dear team,

I hope this email finds you well. I would like to place an order for the following items:

{chr(10).join([f"• {product['p_name']} (ID: {product['p_id']}) - Quantity: {product['quantity']}" for product in products1])}

Customer Details:
- Customer ID: {customer1['id']}
- Email: {customer1['email']}

Please process this order at your earliest convenience. I look forward to hearing from you.

Best regards,
{customer1['name']}"""
            })
            
            # Case 2: Valid order with 2-3 random existing products
            customer2 = self._pick_random_customer(must_exist=True)
            products2 = self._pick_random_product(random.randint(2, 3), must_exist=True)
            
            test_cases.append({
                "type": "Valid",
                "description": "Multiple item order with existing products and customer.",
                "subject": f"Bulk Order Request - {customer2['name']}",
                "body": f"""Hi there,

I'm looking to place a larger order for our office supplies. Here are the items we need:

{chr(10).join([f"• {product['p_name']} (ID: {product['p_id']}) - Quantity: {product['quantity']}" for product in products2])}

Customer Information:
- Customer ID: {customer2['id']}
- Email: {customer2['email']}

Could you please confirm availability and provide an estimated delivery time?

Thanks,
{customer2['name']}"""
            })
            
            # Case 3: Hold - Low Stock/Min Qty
            customer3 = self._pick_random_customer(must_exist=True)
            # Find a product with low stock or stock=0
            low_stock_products = [p_id for p_id, product in self.products.items() if product["stock"] <= 1]
            if low_stock_products:
                low_stock_product_id = random.choice(low_stock_products)
                low_stock_product = {
                    "p_id": low_stock_product_id,
                    "p_name": self.products[low_stock_product_id]["name"],
                    "quantity": self.products[low_stock_product_id]["stock"] + 1  # Order more than available
                }
                other_products = self._pick_random_product(1, must_exist=True)
                products3 = [low_stock_product] + other_products
            else:
                # Fallback to regular products but with high quantity
                products3 = self._pick_random_product(2, must_exist=True)
                products3[0]["quantity"] = 10  # High quantity that might exceed stock
            
            test_cases.append({
                "type": "Hold",
                "description": "Order with one item out of stock or below min quantity.",
                "subject": f"Order Query - {customer3['name']}",
                "body": f"""Hello,

I'm interested in placing an order, but I have some concerns about availability:

{chr(10).join([f"• {product['p_name']} (ID: {product['p_id']}) - Quantity: {product['quantity']}" for product in products3])}

Customer Details:
- Customer ID: {customer3['id']}
- Email: {customer3['email']}

I'm particularly concerned about the availability of {products3[0]['p_name']}. Could you please check if you have sufficient stock for this order?

Best regards,
{customer3['name']}"""
            })
            
            # Case 4: Failed - All Wrong Items
            customer4 = self._pick_random_customer(must_exist=True)
            products4 = self._pick_random_product(random.randint(2, 3), must_exist=False)
            
            test_cases.append({
                "type": "Failed",
                "description": "Order with non-existent product IDs.",
                "subject": f"Order Request - {customer4['name']}",
                "body": f"""Dear Sales Team,

I'm trying to order some items but I'm not sure about the exact product codes. Here's what I'm looking for:

{chr(10).join([f"• {product['p_name']} (ID: {product['p_id']}) - Quantity: {product['quantity']}" for product in products4])}

Customer Information:
- Customer ID: {customer4['id']}
- Email: {customer4['email']}

I found these product codes online, but I'm not sure if they're correct. Could you please help me find the right products?

Thanks,
{customer4['name']}"""
            })
            
            # Case 5: Failed - Invalid Customer
            customer5 = self._pick_random_customer(must_exist=False)
            products5 = self._pick_random_product(random.randint(1, 2), must_exist=True)
            
            test_cases.append({
                "type": "Failed",
                "description": "Order with non-existent customer ID and email.",
                "subject": f"New Customer Order - {customer5['name']}",
                "body": f"""Hi,

I'm a new customer and would like to place my first order. Here are the items I need:

{chr(10).join([f"• {product['p_name']} (ID: {product['p_id']}) - Quantity: {product['quantity']}" for product in products5])}

My Details:
- Customer ID: {customer5['id']}
- Email: {customer5['email']}

I'm not sure if I have a customer account yet. Could you please help me set one up and process this order?

Best regards,
{customer5['name']}"""
            })
            
            print(f"[TestCaseGeneratorService] Generated {len(test_cases)} test cases successfully.")
            return test_cases
            
        except Exception as e:
            print(f"[TestCaseGeneratorService] Error generating test cases: {e}")
            return [] 