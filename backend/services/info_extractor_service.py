from typing import Optional
import google.generativeai as genai
from config import Config
from models import ExtractedOrderInfo, OrderProduct
import json

class InfoExtractorService:
    def extract_info(self, email_text: str) -> ExtractedOrderInfo:
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
            f"Extract the customer ID, customer email, and a list of products (with product name/ID and quantity) "
            f"from the following order email. The products may be listed as bullet points, numbered lists, or inline in the text. "
            f"For each product, extract the product name and quantity. Return the result as a JSON object matching this schema: {json.dumps(schema)}\n"
            f"\nRules: Strictly follow the schema. If a field is missing, set it to null. "
            f"The 'products' field must be a list of objects, each with 'product_id' (if available), 'product_name', and 'quantity'. "
            f"Do not include any explanation or extra text, only the JSON object.\n"
            f"\nEmail:\n{email_text}"
        )

        # Configure Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        response = model.generate_content(prompt)
        # print("[InfoExtractorService] Gemini raw response:", response.text)
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
                    product_id=p.get("product_id") or "",
                    product_name=p.get("product_name") or "",
                    quantity=int(p.get("quantity") or 0)
                ))
            except Exception as e:
                # print(f"[InfoExtractorService] Skipping product due to error: {e} | Data: {p}")
                continue
        return ExtractedOrderInfo(
            customer_id=customer_id if customer_id else None,
            customer_email=customer_email if customer_email else None,
            products=products
        ) 