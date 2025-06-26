# Email-Based Order Processing System

This is a full-stack application designed to automate the processing of customer orders received via email. It uses a Python Flask backend with a multi-agent architecture to extract, validate, and process orders, and a Next.js frontend to provide a user interface for monitoring and managing the system.

## Overview

The system works as follows:
1.  An email containing a customer's order is pasted into the frontend application.
2.  The frontend sends the email text to the backend API.
3.  The backend's **OrderProcessor** pipeline kicks off:
    - **InfoExtractorService**: Uses the Google Gemini LLM to extract structured order information (customer details, products, quantities) from the unstructured email text.
    - **ValidatorService**: Validates the extracted information against the PostgreSQL database. It checks for customer existence, product availability, stock levels, and minimum order quantities.
    - **CommunicationsService**: Generates a professional, context-aware email response for the customer based on the validation results.
    - **DBUpdateService**: If the order is valid, it atomically updates product stock, creates a new order record, and creates the associated order items in the database. If the order has issues, it creates a record with a "Hold" or "Failed" status.
4.  The backend returns a complete JSON object to the frontend, containing the results from each step.
5.  The frontend displays the generated customer message and other processing details.

## Features

### Backend
- **Automated Order Extraction**: Uses an LLM to parse unstructured email text into structured JSON.
- **Robust Validation**: Validates customers and products against the database, including stock and quantity checks.
- **Dynamic Customer Communication**: Generates tailored email responses for successful orders, orders with errors, and unknown customers.
- **Transactional Database Updates**: Ensures data integrity by using database transactions for order creation and stock updates.
- **RESTful API**: Provides clear and documented endpoints for processing orders and retrieving data.
- **Analytics & Forecasting**: Sales trends, product performance, inventory health, sales and inventory forecasting using Prophet, catalog suggestions.

### Frontend
- **Analysis Dashboard**: Visualizes sales trends, forecasts, product performance, inventory health, and catalog suggestions.
- **Order Management**: Paginated order history with detailed modal views and PDF export.
- **Inventory Management**: Paginated inventory table with stock status indicators.
- **Responsive UI**: Built with Tailwind CSS for a clean, adaptive experience.
- **Swiper Carousels**: Used for low/out-of-stock and inventory forecast carousels.
- **Nivo Charts**: Interactive line and bar charts for analytics.

## Tech Stack

-   **Backend**:
    -   Python 3.12+
    -   Flask
    -   PostgreSQL
    -   `asyncpg` for asynchronous database access
    -   `google-generativeai` for LLM integration
    -   `pydantic` for data modeling and validation
    -   `prophet` for forecasting
-   **Frontend**:
    -   Next.js
    -   React
    -   Tailwind CSS
    -   Swiper (for carousels)
    -   Nivo (for charts)

## Project Structure

/practice
|-- /backend
|   |-- /services         # Business logic for each agent/service
|   |-- app.py            # Flask application entrypoint and API routes
|   |-- config.py         # Configuration management
|   |-- db.py             # Database connection and query helpers
|   |-- models.py         # Pydantic models for data structures
|   |-- requirements.txt  # Python dependencies
|   |-- .gitignore        # Git ignore for backend
|   |-- .env              # Environment variables (not committed)
|
|-- /frontend
|   |-- /src
|   |   |-- /app          # Next.js app router pages and layouts
|   |   |-- /components   # Reusable React components
|   |-- next.config.mjs   # Next.js configuration
|   |-- tailwind.config.js
|   |-- package.json

## Setup and Installation

### Prerequisites
- Python 3.12+
- Node.js and npm/yarn
- PostgreSQL server

### Backend Setup
1.  **Navigate to the backend directory**:
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables**:
    Create a file named `.env` in the `backend` directory and add the following, replacing the placeholder values:
    ```ini
    # Google Gemini API
    GOOGLE_API_KEY=your_google_api_key
    GEMINI_MODEL=gemini-1.5-flash

    # Database Connection
    SUPABASE_USER=your_db_user
    SUPABASE_PASSWORD=your_db_password
    SUPABASE_HOST=localhost
    SUPABASE_PORT=5432
    SUPABASE_DBNAME=your_db_name

    # Flask & CORS Configuration
    CORS_ORIGINS=["http://localhost:3000"]
    DEBUG=True
    PORT=5001
    ```
5.  **Database Schema**:
    Ensure your PostgreSQL database has the required tables. See backend/README.md for schema details. Orders table must include `c_name`, `c_address`, and `o_delivery_date` fields.

### Frontend Setup
1.  **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```

## Running the Application

1.  **Run the Backend Server**:
    From the `backend` directory:
    ```bash
    python app.py
    ```
    The server will start on the port specified in your `.env` file (default: 5001).

2.  **Run the Frontend Development Server**:
    From the `frontend` directory:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:3000`.

## API Endpoints

-   `POST /api/process-order` — Process an order from email text
-   `GET /api/get-orders` — List all orders
-   `GET /api/get-order/<order_id>` — Get full order details
-   `GET /api/customers` — List all customers
-   `GET /api/products` — List all products
-   `GET /api/health` — Health check
-   `GET /api/generate-sales-order-pdf/<order_id>` — Generate PDF for an order
-   `GET /api/analytics/kpis` — KPIs
-   `GET /api/analytics/sales-trends` — Sales trends
-   `GET /api/analytics/order-status` — Order status distribution
-   `GET /api/analytics/inventory-health` — Inventory health
-   `GET /api/analytics/product-performance` — Product performance
-   `GET /api/analytics/forecast/sales` — Sales forecast
-   `GET /api/analytics/forecast/inventory-needs` — Inventory needs forecast
-   `GET /api/analytics/suggest-catalog-items` — Catalog suggestions

## License

MIT 