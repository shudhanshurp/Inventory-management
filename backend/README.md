# Two-Agent Order Processing Backend

This backend service processes customer orders using a two-agent system with Supabase database integration using asyncpg for better Windows compatibility.

## Features

- **Two-Agent System**: Analyst Agent analyzes emails and Communications Agent generates responses
- **Supabase Integration**: Persistent data storage for customers, products, and orders
- **Async Database Operations**: Uses asyncpg for efficient PostgreSQL connections
- **Order Management**: Complete order lifecycle with status tracking
- **Inventory Management**: Automatic stock updates for confirmed orders
- **Analytics & Forecasting**: Sales trends, product performance, inventory health, sales and inventory forecasting using Prophet
- **Catalog Suggestions**: Suggests catalog items based on order errors
- **Windows Compatible**: Uses asyncpg instead of psycopg2 for better Windows support

## Setup

### 1. Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Flask Configuration
DEBUG=True
PORT=5001
CORS_ORIGINS=["http://localhost:3000"]

# Supabase Database Configuration
SUPABASE_USER=your_supabase_user
SUPABASE_PASSWORD=your_supabase_password
SUPABASE_HOST=your_supabase_host
SUPABASE_PORT=5432
SUPABASE_DBNAME=your_supabase_database_name
```

### 2. Supabase Setup

1. Create a new Supabase project
2. Get your database connection details from the Supabase dashboard
3. The application will automatically create the required tables:
   - `customers` - Customer information
   - `products` - Product catalog with stock levels
   - `orders` - Order records (must include c_name, c_address, o_delivery_date)
   - `order_items` - Individual items in each order

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

## API Endpoints

### Order & Data Endpoints
- `POST /api/process-order` - Process customer email and create order
- `GET /api/get-orders` - Retrieve all orders
- `GET /api/get-order/<order_id>` - Retrieve full details for a specific order
- `GET /api/customers` - Get customer list
- `GET /api/products` - Get product catalog
- `GET /api/health` - Health check
- `POST /api/analyze-order` - Analyze order without generating response
- `GET /api/generate-sales-order-pdf/<order_id>` - Generate a PDF for a specific order

### Analytics & Forecasting Endpoints
- `GET /api/analytics/kpis` - Get key performance indicators (KPIs)
- `GET /api/analytics/sales-trends` - Get sales trends (supports granularity)
- `GET /api/analytics/order-status` - Get order status distribution
- `GET /api/analytics/inventory-health` - Get inventory health summary
- `GET /api/analytics/product-performance` - Get top product performance
- `GET /api/analytics/forecast/sales` - Get sales forecast (uses Prophet)
- `GET /api/analytics/forecast/inventory-needs` - Get inventory needs forecast (uses Prophet)
- `GET /api/analytics/suggest-catalog-items` - Get catalog suggestions based on order errors

## Database Schema

### Customers Table
- `c_id` (VARCHAR) - Customer ID
- `c_name` (VARCHAR) - Customer name
- `c_email` (VARCHAR) - Customer email
- `c_address` (TEXT) - Customer address
- `created_time` (TIMESTAMP) - Creation timestamp

### Products Table
- `p_id` (VARCHAR) - Product ID
- `p_name` (VARCHAR) - Product name
- `p_price` (DECIMAL) - Product price
- `p_stock` (INTEGER) - Available stock
- `created_at` (TIMESTAMP) - Creation timestamp
- `updated_at` (TIMESTAMP) - Last update timestamp

### Orders Table
- `o_id` (VARCHAR) - Unique order ID
- `c_id` (VARCHAR) - Customer reference
- `c_name` (VARCHAR) - Customer name (required)
- `c_address` (TEXT) - Customer address (required)
- `o_delivery_date` (TIMESTAMP) - Delivery date (required, not null)
- `o_status` (VARCHAR) - Order status
- `o_placed_time` (TIMESTAMP) - Order placed timestamp
- `o_remarks` (TEXT) - Remarks

### Order Items Table
- `oi_id` (SERIAL) - Auto-increment ID
- `o_id` (VARCHAR) - Order reference
- `p_id` (VARCHAR) - Product reference
- `p_name` (VARCHAR) - Product name
- `oi_qty` (INTEGER) - Quantity ordered
- `oi_price` (DECIMAL) - Price at time of order
- `oi_total` (DECIMAL) - Total for item
- `oi_is_available` (BOOLEAN) - Availability

## Order Statuses

- **Processing** - Initial state when order is being analyzed
- **Hold** - Unknown customer, requires registration
- **Waiting for Confirmation** - Issues found, needs customer input
- **Confirmed** - Order validated and confirmed

## Technical Implementation

### Async Database Operations
The application uses `asyncpg` for all database operations, providing:
- Better performance with async I/O
- Improved Windows compatibility
- Automatic connection pooling
- Native JSON support

### Forecasting
- Uses Facebook Prophet for sales and inventory forecasting
- Forecast endpoints return both historical and forecasted data in a frontend-friendly format

### Error Handling
The application includes fallback mechanisms:
- If database connection fails, it falls back to mock data
- Comprehensive error handling for all API endpoints
- Graceful degradation when services are unavailable
- Automatic table creation if they don't exist

### Data Flow
1. **Initialization**: Load customers and products from database
2. **Order Processing**: Analyze email → Create order → Save to database
3. **Inventory Updates**: Update product stock in real-time
4. **Data Retrieval**: Fetch orders with related items using JSON aggregation

## System Overview

This system implements a **Two-Agent Response Generation System** with persistent order management and analytics:

1. **Analyst Agent** - Analyzes emails and produces structured briefing documents
2. **Communications Agent** - Generates professional customer responses
3. **Order Management** - Maintains persistent order records with status tracking
4. **Analytics & Forecasting** - Provides business insights and predictions

## Architecture

```
Email Input → Analyst Agent → Briefing Document → Communications Agent → Customer Response
     ↓
Order Record Creation → Status Management → Inventory Adjustment → Persistent Storage
     ↓
Analytics & Forecasting → Dashboard
```

## File Structure

```
backend/
├── app.py                          # Main Flask application with order management
├── config.py                       # Configuration management
├── db.py                           # Database (asyncpg)
├── requirements.txt                # Python dependencies
├── services/
│   ├── __init__.py
│   ├── analytics_service.py        # Analytics and forecasting
│   ├── communications_service.py   # Communications Agent
│   ├── db_update_service.py        # DB update logic
│   ├── info_extractor_service.py   # Info extraction (Gemini)
│   ├── order_processor.py          # Order processing pipeline
│   ├── pdf_service.py              # PDF generation
│   └── validator_service.py        # Validation logic
├── models.py                       # Pydantic models
```

## 🎯 System Overview

This system implements a **Two-Agent Response Generation System** with persistent order management:

1. **Analyst Agent** - Analyzes emails and produces structured briefing documents
2. **Communications Agent** - Generates professional customer responses
3. **Order Management** - Maintains persistent order records with status tracking

## 🏗️ Architecture

```
Email Input → Analyst Agent → Briefing Document → Communications Agent → Customer Response
     ↓
Order Record Creation → Status Management → Inventory Adjustment → Persistent Storage
```

### Agent 1: Analyst Agent
- **Role**: Logical analysis and data extraction
- **Input**: Raw customer email text
- **Output**: Structured briefing document
- **Responsibilities**: Extract customer info, identify products, validate data, check inventory, generate suggestions

### Agent 2: Communications Agent
- **Role**: Professional customer communication
- **Input**: Structured briefing document from Analyst
- **Output**: Professional customer email response
- **Persona**: Alex, senior customer service representative

### Order Management System
- **Role**: Persistent order tracking and status management
- **Features**: Unique order IDs, status tracking, inventory management, timestamp tracking

## 📁 File Structure

```
backend/
├── app.py                          # Main Flask application with order management
├── config.py                       # Configuration management
├── db.py                          # Mock database (customers & products)
├── requirements.txt               # Python dependencies
└── services/
    ├── __init__.py
    ├── analyst_service.py         # Analyst Agent implementation
    └── communications_service.py  # Communications Agent implementation
```

## 🚀 API Endpoints

### Main Endpoints

#### `POST /api/process-order`
Process a complete order using both agents and create persistent order record.

**Request:**
```json
{
  "email_text": "Hi, I'm Alice and I need 2 laptops and a wireless mouse"
}
```

#### `GET /api/get-orders`
Get all orders from the backend with their current statuses.

**Response:**
```json
{
  "orders": [
    {
      "order_id": "ORD-2025-001",
      "customer_id": "CUST101",
      "products": [...],
      "total_value": 1200,
      "status": "Confirmed",
      "email_text": "Hi, I'm Alice and I need a laptop",
      "created_at": "2025-01-15T10:30:00",
      "updated_at": "2025-01-15T10:30:00",
      "customer_response": "Dear Alice Johnson...",
      "analysis": {...}
    }
  ]
}
```

#### `POST /api/analyze-order`
Get only the analysis without generating customer response (for debugging).

#### `GET /api/health`
Health check endpoint.

#### `GET /api/customers`
Get available customers.

#### `GET /api/products`
Get available products.

## 📊 Order Status System

The system automatically manages order statuses based on validation results:

### Status Types:
- **Processing**: Initial status when order is created
- **Hold**: Customer not found in database (requires registration)
- **Waiting for Confirmation**: Customer found but items have issues (out of stock, insufficient quantity)
- **Confirmed**: Customer found and all items available (inventory automatically adjusted)

### Status Logic:
1. **Unknown Customer** → Status: "Hold"
2. **Known Customer + Item Issues** → Status: "Waiting for Confirmation"
3. **Known Customer + All Items Available** → Status: "Confirmed" (inventory adjusted)

## 📋 Order Record Structure

Each order record contains comprehensive information:

```json
{
  "order_id": "ORD-2025-001",
  "customer_id": "CUST101",
  "products": [
    {
      "product_id": "PROD001",
      "product_name": "Laptop Pro",
      "quantity": 1,
      "price": 1200
    }
  ],
  "total_value": 1200,
  "status": "Confirmed",
  "email_text": "Original email text",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00",
  "customer_response": "Generated response email",
  "analysis": {
    "customer_info": {...},
    "overall_status": "success",
    "successful_items": [...],
    "error_items": [...],
    "suggestions": [...],
    "total_items": 1,
    "successful_count": 1,
    "error_count": 0
  }
}
```

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

## 📦 Installation

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables (see Configuration section)

3. Run the application:
```bash
python app.py
```

## 🎭 Agent Personas

### Analyst Agent
- **Role**: Internal order analyst
- **Focus**: Factual analysis and data validation
- **Output**: Structured JSON briefing documents

### Communications Agent
- **Name**: Alex
- **Role**: Senior customer service representative
- **Tone**: Professional, polite, and helpful

## 🎯 Benefits

1. **Separation of Concerns**: Analysis and communication are handled by specialized agents
2. **Persistent Order Tracking**: All orders are stored with complete history and status
3. **Real-time Status Updates**: Orders automatically update status based on validation results
4. **Inventory Management**: Automatic inventory adjustment for confirmed orders
5. **Professional Output**: Human-like, empathetic customer responses
6. **Complete Audit Trail**: Full order history with timestamps and analysis

## 🔍 Example Workflow

1. **Customer Email**: "Hi, I'm Alice and I need 2 laptops and a wireless mouse"
2. **Order Creation**: System creates ORD-2025-003 with "Processing" status
3. **Analyst Agent**: Analyzes and produces briefing document
4. **Status Update**: Updates order status based on validation results
5. **Inventory Adjustment**: If confirmed, adjusts product inventory
6. **Communications Agent**: Generates professional response
7. **Order Completion**: Order record contains full transaction history

## 🛠️ Frontend Integration

The frontend can now:
- Fetch live order data from `/api/get-orders`
- Display real-time order statuses
- Show complete order history
- Track inventory changes
- Display customer responses

## 📈 Order ID Format

Orders use a sequential ID format: `ORD-YYYY-NNN`
- **ORD**: Order prefix
- **YYYY**: Current year
- **NNN**: Sequential number (001, 002, 003, etc.)

Example: `ORD-2025-001`, `ORD-2025-002`, `ORD-2025-003` 