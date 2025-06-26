# backend/app.py
from typing import Dict
from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import uuid
from datetime import datetime

from config import Config
# from services.analyst_service import AnalystService
from services.communications_service import CommunicationsService
from db import get_customers, get_products, get_orders, update_product_stock, get_order_by_id, get_all_customers_dict, _get_orders_async, _get_all_customers_dict_async, _get_products_async, run_async
from services.order_processor import OrderProcessor
from services.pdf_service import PdfService
from services.analytics_service import AnalyticsService
from services.info_extractor_service import InfoExtractorService
from services.validator_service import ValidatorService
from services.db_update_service import DBUpdateService
from services.test_case_generator_service import TestCaseGeneratorService

# Validate configuration
Config.validate()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Initialize services
# analyst_service = AnalystService()
info_extractor_service = InfoExtractorService()
validator_service = ValidatorService()
db_update_service = DBUpdateService()
communications_service = CommunicationsService()
pdf_service = PdfService()

# Instantiate AnalyticsService
analytics_service = AnalyticsService(_get_orders_async, _get_all_customers_dict_async, _get_products_async)

# Asynchronously load data into the analytics_service once at startup
run_async(analytics_service.load_cached_data())

# Instantiate TestCaseGeneratorService
test_case_generator_service = TestCaseGeneratorService(get_customers, get_products)

# Initialize order processor
order_processor_instance = OrderProcessor(
    info_extractor_service_instance=info_extractor_service,
    validator_service_instance=validator_service,
    communications_service_instance=communications_service,
    db_update_service_instance=db_update_service
)

@app.route("/api/process-order", methods=["POST"])
def process_order():
    """Process order from email text using the new pipeline."""
    try:
        email_text = request.json.get("email_text")
        if not email_text:
            return jsonify({"error": "Email text is required"}), 400
        # print(f"[APP-PROCESS] Received email_text (first 100 chars): {email_text[:100]}...")
        # print("[APP-PROCESS] Calling OrderProcessor.process_order...")
        result = order_processor_instance.process_order(email_text)
        # print(f"[APP-PROCESS] OrderProcessor.process_order returned: {result.get('order_id')}, Status: {result.get('order_status')}")
        return jsonify(result)
    except Exception as e:
        print(f"[APP-PROCESS] Error processing order in endpoint: {e}")
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
    """Get full details for a specific order, including items."""
    try:
        order = get_order_by_id(order_id)
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
    # TODO: This endpoint needs to be implemented properly
    # Currently has issues with missing analyst service
    return jsonify({"error": "Analyze order endpoint not yet implemented"}), 501
    
    # try:
    #     email_text = request.json.get("email_text")
    #     if not email_text:
    #         return jsonify({"error": "Email text is required"}), 400
    #     
    #     # Get only the analysis
    #     briefing_document = order_processor.analyst.analyze_order(email_text, order_processor.customers, order_processor.products)
    #     
    #     return jsonify({
    #         "status": "success",
    #         "analysis": briefing_document
    #     })
    #     
    # except Exception as e:
    #     return jsonify({"error": str(e)}), 500


@app.route("/api/generate-sales-order-pdf/<order_id>", methods=["GET"])
def generate_sales_order_pdf_endpoint(order_id):
    """Generate and return a sales order PDF for a specific order."""
    try:
        orders = get_orders()
        order = next((o for o in orders if (o.get("o_id") or o.get("order_id")) == order_id), None)
        print(f"[APP-PDF] Order data fetched for PDF: {order}")
        if not order:
            return jsonify({"error": "Order not found"}), 404
        pdf_bytes = pdf_service.generate_sales_order_pdf(order)
        response = make_response(pdf_bytes)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', f'attachment; filename=sales_order_{order_id}.pdf')
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/kpis", methods=["GET"])
def analytics_kpis_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'last_30_days')
        import asyncio
        result = asyncio.run(analytics_service.get_kpis(time_filter=time_filter))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/sales-trends", methods=["GET"])
def analytics_sales_trends_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'last_30_days')
        granularity = request.args.get('granularity', 'month')
        import asyncio
        result = asyncio.run(analytics_service.get_sales_trends(time_filter=time_filter, granularity=granularity))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/order-status", methods=["GET"])
def analytics_order_status_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'last_30_days')
        import asyncio
        result = asyncio.run(analytics_service.get_order_status_distribution(time_filter=time_filter))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/inventory-health", methods=["GET"])
def analytics_inventory_health_endpoint():
    try:
        print(f"[APP] Inventory Health endpoint hit")
        import asyncio
        result = asyncio.run(analytics_service.get_inventory_health())
        print(f"[APP] Inventory Health endpoint returning result.")
        return jsonify(result)
    except Exception as e:
        print(f"[APP] Error in Inventory Health endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/product-performance", methods=["GET"])
def analytics_product_performance_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'all_time')
        top_n = int(request.args.get('top_n', 10))
        import asyncio
        result = asyncio.run(analytics_service.get_product_performance(time_filter=time_filter, top_n=top_n))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/forecast/sales", methods=["GET"])
def analytics_sales_forecast_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'last_365_days')
        periods = int(request.args.get('periods', 3))
        granularity = request.args.get('granularity', 'month')
        import asyncio
        result = asyncio.run(analytics_service.get_sales_forecast(time_filter=time_filter, periods_to_forecast=periods, granularity=granularity))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/forecast/inventory-needs", methods=["GET"])
def analytics_inventory_needs_forecast_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'last_365_days')
        top_n = int(request.args.get('top_n', 5))
        periods = int(request.args.get('periods', 3))
        granularity = request.args.get('granularity', 'month')
        import asyncio
        result = asyncio.run(analytics_service.get_inventory_needs_forecast(time_filter=time_filter, top_n_products=top_n, periods_to_forecast=periods, granularity=granularity))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/analytics/suggest-catalog-items", methods=["GET"])
def analytics_catalog_suggestions_endpoint():
    try:
        time_filter = request.args.get('time_filter', 'all_time')
        top_n = int(request.args.get('top_n', 5))
        import asyncio
        result = asyncio.run(analytics_service.get_catalog_suggestions(time_filter=time_filter, top_n=top_n))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-test-cases", methods=["GET"])
def generate_test_cases_endpoint():
    """Generate test cases for order processing."""
    try:
        import asyncio
        result = asyncio.run(test_case_generator_service.generate_test_cases())
        return jsonify({"test_cases": result})
    except Exception as e:
        print(f"[APP] Error generating test cases: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=Config.PORT)