from typing import Optional
import google.generativeai as genai
from config import Config
from models import ExtractedOrderInfo, OrderProduct
import json

class InfoExtractorService:
    @staticmethod
    def extract_info(email_text: str) -> ExtractedOrderInfo:
        # Prepare Gemini prompt
        schema = {
            "customer_id": "string or null",
            "customer_email": "string or null",
            "products": [
                {
                    "product_id": "string",
                    "product_name": "string",
                    "quantity": "integer"
                }
            ]
        }
        prompt = (
            "Extract the customer name, customer email, and a list of products (with product name/ID and quantity) "
            "from the following order email. Return the result as a JSON object matching this schema: "
            f"{json.dumps(schema)}\n\nEmail:\n{email_text}"
        )

        # Configure Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        # Try to extract JSON from the response
        try:
            # Gemini may return code block or plain JSON
            content = response.text.strip()
            if content.startswith("```json") and content.endswith("```"):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            elif content.startswith("```") and content.endswith("```"):
                content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
            data = json.loads(content)
        except Exception:
            data = {}

        # Parse fields, handle missing
        customer_id = data.get("customer_id")
        customer_email = data.get("customer_email")
        products_data = data.get("products", [])
        products = []
        for p in products_data:
            try:
                products.append(OrderProduct(
                    product_id=p.get("product_id", ""),
                    product_name=p.get("product_name", ""),
                    quantity=int(p.get("quantity", 0))
                ))
            except Exception:
                continue
        return ExtractedOrderInfo(
            customer_id=customer_id if customer_id else None,
            customer_email=customer_email if customer_email else None,
            products=products
        ) 