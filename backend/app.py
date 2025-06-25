# backend/app.py
from typing import Dict
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime

from config import Config
# from services.analyst_service import AnalystService
from services.communications_service import CommunicationsService
from db import get_customers, get_products, get_orders, update_product_stock
from services.order_processor import OrderProcessor

# Validate configuration
Config.validate()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Initialize services
# analyst_service = AnalystService()
communications_service = CommunicationsService()

class TwoAgentOrderProcessor:
    """Two-Agent Order Processing System."""
    
    def __init__(self):
        self.customers = get_customers()
        self.products = get_products()
        # self.analyst = analyst_service
        self.communications = communications_service
    
    def process_order(self, email_text: str) -> Dict:
        """Process order using the two-agent system with order record creation."""
        try:
            # Step 1: Create new order record
            order_id = self._generate_order_id()
            order_record = self._create_order_record(order_id, email_text)
            
            # Step 2: Perform validation (existing logic)
            briefing_document = self.analyst.analyze_order(email_text, self.customers, self.products)
            
            # Step 3: Update order status based on validation results
            self._update_order_status(order_record, briefing_document)
            
            # Step 4: Adjust inventory if order is confirmed
            if order_record["status"] == "Confirmed":
                self._adjust_inventory(order_record)
            
            # Step 5: Generate customer response
            customer_response = self.communications.generate_customer_response(briefing_document)
            
            # Step 6: Update order with final details
            self._update_order_details(order_record, briefing_document, customer_response)
            
            # Step 7: Save order to database
            save_order(order_record)
            
            return self._prepare_final_response(briefing_document, customer_response, order_record)
            
        except Exception as e:
            raise Exception(f"Failed to process order: {str(e)}")
    
    def _generate_order_id(self) -> str:
        """Generate a unique order ID."""
        year = datetime.now().year
        # Get existing orders to count
        existing_orders = get_orders()
        count = len([order for order in existing_orders if str(year) in order["order_id"]]) + 1
        return f"ORD-{year}-{count:03d}"
    
    def _create_order_record(self, order_id: str, email_text: str) -> Dict:
        """Create initial order record."""
        return {
            "order_id": order_id,
            "customer_id": None,
            "products": [],
            "total_value": 0,
            "status": "Processing",
            "email_text": email_text,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "customer_response": None,
            "analysis": None
        }
    
    def _update_order_status(self, order_record: Dict, briefing_document: Dict):
        """Update order status based on validation results."""
        customer_status = briefing_document["customer_info"]["status"]
        error_count = briefing_document["error_count"]
        
        if customer_status == "unknown_customer":
            order_record["status"] = "Hold"
        elif error_count > 0:
            order_record["status"] = "Waiting for Confirmation"
        else:
            order_record["status"] = "Confirmed"
        
        order_record["updated_at"] = datetime.now().isoformat()
    
    def _adjust_inventory(self, order_record: Dict):
        """Adjust inventory for confirmed orders."""
        for item in order_record["products"]:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            if product_id in self.products:
                current_stock = self.products[product_id]["stock"]
                new_stock = current_stock - quantity
                # Update in database
                update_product_stock(product_id, new_stock)
                # Update local cache
                self.products[product_id]["stock"] = new_stock
    
    def _update_order_details(self, order_record: Dict, briefing_document: Dict, customer_response: str):
        """Update order with final details from analysis."""
        order_record["customer_id"] = briefing_document["customer_info"]["id"]
        order_record["products"] = briefing_document["successful_items"] + briefing_document["error_items"]
        order_record["total_value"] = sum(item.get("price", 0) * item.get("quantity", 0) for item in briefing_document["successful_items"])
        order_record["customer_response"] = customer_response
        order_record["analysis"] = briefing_document
        order_record["updated_at"] = datetime.now().isoformat()
    
    def _prepare_final_response(self, briefing_document: Dict, customer_response: str, order_record: Dict) -> Dict:
        """Prepare the final API response."""
        status = "success" if briefing_document["overall_status"] == "success" else "error"
        
        return {
            "status": status,
            "message": customer_response,
            "order_id": order_record["order_id"],
            "order_status": order_record["status"],
            "analysis": {
                "customer_info": briefing_document["customer_info"],
                "overall_status": briefing_document["overall_status"],
                "successful_items": briefing_document["successful_items"],
                "error_items": briefing_document["error_items"],
                "suggestions": briefing_document["suggestions"],
                "summary": {
                    "total_items": briefing_document["total_items"],
                    "successful_count": briefing_document["successful_count"],
                    "error_count": briefing_document["error_count"]
                }
            }
        }


# Initialize order processor
order_processor = TwoAgentOrderProcessor()


@app.route("/api/process-order", methods=["POST"])
def process_order():
    """Process order from email text using the new pipeline."""
    try:
        email_text = request.json.get("email_text")
        if not email_text:
            return jsonify({"error": "Email text is required"}), 400
        result = OrderProcessor.process_order(email_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get-orders", methods=["GET"])
def get_orders_endpoint():
    """Get all orders (basic info only)."""
    try:
        orders = get_orders()  # Should return a list of dicts
        # Only keep basic info for each order
        basic_orders = [
            {
                "o_id": o.get("o_id") or o.get("order_id"),
                "c_name": o.get("c_name"),
                "o_placed_time": o.get("o_placed_time") or o.get("created_at"),
                "o_status": o.get("o_status") or o.get("status"),
                "total_value": o.get("total_value"),
            }
            for o in orders
        ]
        return jsonify({"orders": basic_orders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/get-order/<order_id>", methods=["GET"])
def get_order_detail(order_id):
    """Get full details for a specific order."""
    try:
        orders = get_orders()
        order = next((o for o in orders if (o.get("o_id") or o.get("order_id")) == order_id), None)
        if not order:
            return jsonify({"error": "Order not found"}), 404
        return jsonify({"order": order})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Two-Agent Order Processing Service is running"})


@app.route("/api/customers", methods=["GET"])
def get_customers_endpoint():
    """Get available customers from database."""
    try:
        customers = get_customers()
        return jsonify({"customers": customers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["GET"])
def get_products_endpoint():
    """Get available products from database."""
    try:
        products_dict = get_products()
        products = []
        for p_id, prod in products_dict.items():
            products.append({
                "p_id": p_id,
                "p_name": prod.get("name"),
                "p_price": prod.get("price"),
                "p_stock": prod.get("stock"),
            })
        return jsonify({"products": products})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyze-order", methods=["POST"])
def analyze_order_only():
    """Analyze order without generating customer response (for debugging)."""
    try:
        email_text = request.json.get("email_text")
        if not email_text:
            return jsonify({"error": "Email text is required"}), 400
        
        # Get only the analysis
        briefing_document = order_processor.analyst.analyze_order(email_text, order_processor.customers, order_processor.products)
        
        return jsonify({
            "status": "success",
            "analysis": briefing_document
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)