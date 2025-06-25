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

### Frontend
- **Email Submission Form**: A simple interface to submit raw email text for processing.
- **Real-time Results**: Displays the generated customer message and a full breakdown of the processing results.
- **Dashboard Views**: (Future enhancement) Tables to display customers, products, and orders from the database.

## Tech Stack

-   **Backend**:
    -   Python 3.12+
    -   Flask
    -   PostgreSQL
    -   `asyncpg` for asynchronous database access
    -   `google-generativeai` for LLM integration
    -   `Pydantic` for data modeling and validation
-   **Frontend**:
    -   Next.js
    -   React
    -   Tailwind CSS

## Project Structure
```
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
```

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
    GEMINI_MODEL=gemini-pro

    # Database Connection
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=your_db_name

    # Flask & CORS Configuration
    CORS_ORIGINS=http://localhost:3000
    FLASK_DEBUG=True
    FLASK_PORT=5001
    ```
5.  **Database Schema**:
    Ensure your PostgreSQL database has the required tables. You can use the following SQL schema as a starting point:
    ```sql
    CREATE TABLE customers (
        c_id VARCHAR(50) PRIMARY KEY,
        c_name VARCHAR(100),
        c_email VARCHAR(100) UNIQUE,
        c_address TEXT
    );

    CREATE TABLE products (
        p_id VARCHAR(50) PRIMARY KEY,
        p_name VARCHAR(100),
        p_price NUMERIC(10, 2),
        p_stock INT,
        p_min_quantity INT DEFAULT 1
    );

    CREATE TABLE orders (
        o_id VARCHAR(50) PRIMARY KEY,
        c_id VARCHAR(50) REFERENCES customers(c_id),
        c_name VARCHAR(100),
        c_address TEXT,
        o_status VARCHAR(50),
        o_placed_time TIMESTAMP,
        o_delivery_date TIMESTAMP
    );

    CREATE TABLE order_items (
        oi_id SERIAL PRIMARY KEY,
        o_id VARCHAR(50) REFERENCES orders(o_id),
        p_id VARCHAR(50) REFERENCES products(p_id),
        p_name VARCHAR(100),
        oi_qty INT,
        oi_price NUMERIC(10, 2),
        oi_total NUMERIC(10, 2),
        oi_is_available BOOLEAN
    );
    ```

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

-   `POST /api/process-order`
    -   **Description**: The main endpoint to process an order from email text.
    -   **Body**: `{ "email_text": "..." }`
    -   **Response**: A JSON object containing the results from the entire processing pipeline.
-   `GET /api/get-orders`
    -   **Description**: Retrieves a list of all orders with basic information.
-   `GET /api/get-order/<order_id>`
    -   **Description**: Fetches the full details for a single order.
-   `GET /api/customers`
    -   **Description**: Returns a list of all customers in the database.
-   `GET /api/products`
    -   **Description**: Returns a list of all products in the database.
-   `GET /api/health`
    -   **Description**: A simple health check endpoint. 