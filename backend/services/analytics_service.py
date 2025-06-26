from datetime import datetime, timedelta, timezone
from typing import Tuple, Callable
from collections import defaultdict
import pandas as pd
from prophet import Prophet

class AnalyticsService:
    def __init__(self, get_all_orders_func: Callable, get_all_customers_dict_func: Callable, get_products_func: Callable):
        self.get_all_orders_func = get_all_orders_func
        print("[AnalyticsService] Initialized with orders func.")
        self.get_all_customers_dict_func = get_all_customers_dict_func
        print("[AnalyticsService] Initialized with customers func.")
        self.get_products_func = get_products_func
        print("[AnalyticsService] Initialized with products func.")
        self.all_cached_orders = []
        self.all_cached_customers_dict = {}
        self.all_cached_products = {}

    async def load_cached_data(self):
        """Load and cache all orders and customers data."""
        print("[AnalyticsService] Loading cached data...")
        self.all_cached_orders = await self.get_all_orders_func()
        print(f"[AnalyticsService] Cached {len(self.all_cached_orders)} orders.")
        self.all_cached_customers_dict = await self.get_all_customers_dict_func()
        print(f"[AnalyticsService] Cached {len(self.all_cached_customers_dict)} customers.")
        self.all_cached_products = await self.get_products_func()
        print(f"[AnalyticsService] Cached {len(self.all_cached_products)} products.")
        print("[AnalyticsService] Cached data loaded successfully.")

    def _get_date_range(self, time_filter: str) -> Tuple[datetime, datetime]:
        print(f"[AnalyticsService] _get_date_range called for filter: {time_filter}")
        now = datetime.now(timezone.utc)
        print(f"DEBUG: Current UTC time (now): {now}")
        
        if time_filter == "last_7_days":
            # Last 7 days from current time
            end_date = now
            start_date = end_date - timedelta(days=7)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"DEBUG: Filter '{time_filter}': Start={start_date}, End={end_date}")
            
        elif time_filter == "last_30_days":
            # Last 30 days from current time
            end_date = now
            start_date = end_date - timedelta(days=30)
            print(f"DEBUG: Filter '{time_filter}': Start={start_date}, End={end_date}")
            
        elif time_filter == "last_365_days":
            # Rolling 365 days from current time
            end_date = now
            start_date = end_date - timedelta(days=365)
            print(f"DEBUG: Filter '{time_filter}': Start={start_date}, End={end_date}")
            
        elif time_filter == "all_time":
            start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
            end_date = now
            print(f"DEBUG: Filter '{time_filter}': Start={start_date}, End={end_date}")
            
        else:
            raise ValueError(f"Unknown time_filter: {time_filter}")
            
        print(f"[AnalyticsService] Date range: {start_date} to {end_date}")
        return (start_date, end_date)

    async def get_kpis(self, time_filter: str = "all_time") -> dict:
        try:
            print(f"[AnalyticsService] get_kpis called for filter: {time_filter}")
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] KPIs: Date range calculated.")
            print(f"[AnalyticsService] KPIs: Using {len(self.all_cached_orders)} cached orders.")
            filtered_orders = [
                order for order in self.all_cached_orders
                if order.get("o_placed_time") and start_date <= order["o_placed_time"] <= end_date
            ]
            print(f"[AnalyticsService] KPIs: Filtered down to {len(filtered_orders)} orders.")
            total_revenue = 0.0
            total_orders = 0
            unique_customer_ids = set()
            new_customers_count = 0
            for order in filtered_orders:
                total_revenue += float(order.get("total_value", 0))
                total_orders += 1
                c_id = order.get("c_id")
                if c_id:
                    unique_customer_ids.add(c_id)
            print(f"[AnalyticsService] KPIs: Using {len(self.all_cached_customers_dict)} cached customers for new customer count.")
            for customer in self.all_cached_customers_dict.values():
                created_time = customer.get("created_time")
                if created_time and start_date <= created_time <= end_date:
                    new_customers_count += 1
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
            kpis_result = {
                "totalRevenue": total_revenue,
                "totalOrders": total_orders,
                "avgOrderValue": avg_order_value,
                "newCustomers": new_customers_count
            }
            print(f"[AnalyticsService] KPIs: Returning KPIs: {kpis_result}")
            return kpis_result
        except Exception as e:
            print(f"[AnalyticsService] Error in get_kpis: {e}")
            raise

    async def get_sales_trends(self, time_filter: str = "all_time", granularity: str = "month") -> list:
        try:
            print(f"[AnalyticsService] get_sales_trends called for filter: {time_filter}, granularity: {granularity}")
            from collections import defaultdict
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] Sales Trends: Date range calculated.")
            print(f"[AnalyticsService] Sales Trends: Using {len(self.all_cached_orders)} cached orders.")
            filtered_orders = [
                order for order in self.all_cached_orders
                if order.get("o_placed_time") and start_date <= order["o_placed_time"] <= end_date
            ]
            print(f"[AnalyticsService] Sales Trends: Filtered down to {len(filtered_orders)} orders for trends.")
            revenue_by_period = defaultdict(float)
            for order in filtered_orders:
                o_placed_time = order.get("o_placed_time")
                if not o_placed_time:
                    continue
                if granularity == "month":
                    period_str = o_placed_time.strftime("%Y-%m")
                elif granularity == "week":
                    period_str = o_placed_time.strftime("%Y-%W")
                elif granularity == "year":
                    period_str = o_placed_time.strftime("%Y")
                else:
                    raise ValueError(f"Unknown granularity: {granularity}")
                for item in order.get("items", []):
                    revenue_by_period[period_str] += float(item.get("oi_total", 0))
            # Fill in missing periods
            periods = []
            current = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            if granularity == "month":
                while current <= end_date:
                    periods.append(current.strftime("%Y-%m"))
                    # Move to next month
                    if current.month == 12:
                        current = current.replace(year=current.year + 1, month=1)
                    else:
                        current = current.replace(month=current.month + 1)
            elif granularity == "week":
                while current <= end_date:
                    periods.append(current.strftime("%Y-%W"))
                    current += timedelta(weeks=1)
            elif granularity == "year":
                while current <= end_date:
                    periods.append(current.strftime("%Y"))
                    current = current.replace(year=current.year + 1)
            # Build final sorted list
            result = []
            for period in sorted(periods):
                result.append({"period": period, "revenue": revenue_by_period.get(period, 0.0)})
            print(f"[AnalyticsService] Sales Trends: Returning {len(result)} trend periods.")
            return result
        except Exception as e:
            print(f"[AnalyticsService] Error in get_sales_trends: {e}")
            raise

    async def get_order_status_distribution(self, time_filter: str = "all_time") -> dict:
        try:
            print(f"[AnalyticsService] get_order_status_distribution called for filter: {time_filter}")
            from collections import defaultdict
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] Order Status Distribution: Date range calculated.")
            print(f"[AnalyticsService] Order Status Distribution: Using {len(self.all_cached_orders)} cached orders.")
            
            filtered_orders = [
                order for order in self.all_cached_orders
                if order.get("o_placed_time") and start_date <= order["o_placed_time"] <= end_date
            ]
            print(f"[AnalyticsService] Order Status Distribution: Filtered down to {len(filtered_orders)} orders.")
            
            status_counts = defaultdict(int)
            for order in filtered_orders:
                # Normalize status name to ensure consistency
                status = order.get('o_status', 'Unknown')
                normalized_status = status.title() if status else 'Unknown'
                status_counts[normalized_status] += 1
            
            # Filter out statuses with zero counts and return only non-zero statuses
            final_status_distribution = {
                status: count
                for status, count in status_counts.items()
                if count > 0
            }
            
            print(f"[AnalyticsService] Order Status Distribution: Returning {len(final_status_distribution)} status types with non-zero counts.")
            return final_status_distribution
        except Exception as e:
            print(f"[AnalyticsService] Error in get_order_status_distribution: {e}")
            raise

    async def get_inventory_health(self) -> dict:
        try:
            print(f"[AnalyticsService] get_inventory_health called")
            
            # Use cached products data
            products_dict = self.all_cached_products
            print(f"[AnalyticsService] Inventory Health: Using {len(products_dict)} cached products.")
            
            total_inventory_value = 0.0
            low_stock_items = []
            out_of_stock_items = []
            LOW_STOCK_THRESHOLD = 5
            
            for p_id, product in products_dict.items():
                price = float(product.get('price', 0))
                stock = int(product.get('stock', 0))
                
                # Calculate total inventory value
                total_inventory_value += price * stock
                
                # Check for low stock items (stock > 0 but <= threshold)
                if stock <= LOW_STOCK_THRESHOLD and stock > 0:
                    low_stock_items.append({
                        'p_id': p_id,
                        'p_name': product.get('name', 'Unknown Product'),
                        'p_stock': stock
                    })
                
                # Check for out of stock items
                elif stock == 0:
                    out_of_stock_items.append({
                        'p_id': p_id,
                        'p_name': product.get('name', 'Unknown Product'),
                        'p_stock': stock
                    })
            
            result = {
                "totalInventoryValue": total_inventory_value,
                "lowStockItems": low_stock_items,
                "outOfStockItems": out_of_stock_items
            }
            
            print(f"[AnalyticsService] Inventory Health: Total value: ${total_inventory_value:.2f}, Low stock: {len(low_stock_items)}, Out of stock: {len(out_of_stock_items)}")
            return result
        except Exception as e:
            print(f"[AnalyticsService] Error in get_inventory_health: {e}")
            raise

    async def get_product_performance(self, time_filter: str = "all_time", top_n: int = 10) -> list:
        try:
            print(f"[AnalyticsService] get_product_performance called for filter: {time_filter}, top_n: {top_n}")
            from collections import defaultdict
            
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] Product Performance: Date range calculated.")
            
            all_orders = self.all_cached_orders
            print(f"[AnalyticsService] Product Performance: Using {len(all_orders)} cached orders.")
            
            filtered_orders = [
                order for order in all_orders
                if order.get("o_placed_time") and start_date <= order["o_placed_time"] <= end_date
            ]
            print(f"[AnalyticsService] Product Performance: Filtered down to {len(filtered_orders)} orders.")
            
            # Create defaultdict to store aggregated data per product
            product_data = defaultdict(lambda: {'total_quantity_sold': 0, 'total_revenue': 0.0, 'p_name': ''})
            
            # Loop through filtered orders and their items
            for order in filtered_orders:
                for item in order.get("items", []):
                    p_id = item.get("p_id")
                    p_name = item.get("p_name", "")
                    oi_qty = int(item.get("oi_qty", 0))
                    oi_total = float(item.get("oi_total", 0))
                    
                    if p_id:
                        product_data[p_id]['total_quantity_sold'] += oi_qty
                        product_data[p_id]['total_revenue'] += oi_total
                        # Store p_name (since p_name might not be in products cache and is present in order_items)
                        if not product_data[p_id]['p_name'] and p_name:
                            product_data[p_id]['p_name'] = p_name
            
            # Convert defaultdict into a list of dictionaries
            product_list = []
            for p_id, data in product_data.items():
                product_list.append({
                    "p_id": p_id,
                    "p_name": data['p_name'],
                    "total_quantity_sold": data['total_quantity_sold'],
                    "total_revenue": data['total_revenue']
                })
            
            # Sort by total_quantity_sold in descending order
            product_list.sort(key=lambda x: x['total_quantity_sold'], reverse=True)
            
            # Return only the top_n products
            result = product_list[:top_n]
            
            print(f"[AnalyticsService] Product Performance: Returning top {len(result)} products by quantity sold.")
            return result
            
        except Exception as e:
            print(f"[AnalyticsService] Error in get_product_performance: {e}")
            raise

    async def get_sales_forecast(self, time_filter: str = "last_365_days", periods_to_forecast: int = 3, granularity: str = "month") -> list:
        try:
            print(f"[AnalyticsService] get_sales_forecast called for filter: {time_filter}, periods_to_forecast: {periods_to_forecast}, granularity: {granularity}")
            
            # Get historical sales data
            historical_sales_trends_raw = await self.get_sales_trends(time_filter=time_filter, granularity=granularity)
            print(f"[AnalyticsService] Sales Forecast: Retrieved {len(historical_sales_trends_raw)} historical periods.")
            
            # Prepare data for Prophet
            df = pd.DataFrame(historical_sales_trends_raw).rename(columns={'period': 'ds', 'revenue': 'y'})
            if granularity == 'month':
                df['ds'] = pd.to_datetime(df['ds'], format='%Y-%m')
            elif granularity == 'week':
                df['ds'] = pd.to_datetime(df['ds'] + '-1', format='%Y-%W-%w')
            elif granularity == 'year':
                df['ds'] = pd.to_datetime(df['ds'], format='%Y')
            else:
                raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
            
            if len(df) < 2:
                print(f"[AnalyticsService] Sales Forecast: Insufficient historical data for forecasting. Returning historical data only.")
                for item in historical_sales_trends_raw:
                    item["type"] = "historical"
                return historical_sales_trends_raw
            
            model = Prophet(seasonality_mode='multiplicative', daily_seasonality=False)
            model.fit(df)
            if granularity == 'month':
                future = model.make_future_dataframe(periods=periods_to_forecast, freq='MS')
            elif granularity == 'week':
                future = model.make_future_dataframe(periods=periods_to_forecast, freq='W-MON')
            elif granularity == 'year':
                future = model.make_future_dataframe(periods=periods_to_forecast, freq='AS')
            else:
                raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
            forecast_df = model.predict(future)

            # Build a lookup for actual historical revenue by period
            historical_lookup = {item['ds']: item['y'] for item in df.to_dict('records')}
            if granularity == 'month':
                period_format = "%Y-%m"
            elif granularity == 'week':
                period_format = "%Y-%W"
            elif granularity == 'year':
                period_format = "%Y"
            else:
                period_format = "%Y-%m"
            # Find the last historical ds for type assignment
            last_hist_ds = df['ds'].max()

            result = []
            for _, row in forecast_df.iterrows():
                ds = row['ds']
                yhat = row['yhat']
                period_str = ds.strftime(period_format)
                if ds <= last_hist_ds and ds in historical_lookup:
                    # Use actual revenue for historical periods
                    result.append({
                        "period": period_str,
                        "revenue": float(historical_lookup[ds]),
                        "type": "historical"
                    })
                else:
                    # Use forecast for future periods
                    result.append({
                        "period": period_str,
                        "revenue": round(float(yhat), 2),
                        "type": "forecast"
                    })
            print(f"[AnalyticsService] Sales Forecast: Returning {len(result)} total periods (historical + forecast).")
            return result
        except Exception as e:
            print(f"[AnalyticsService] Error in get_sales_forecast: {e}")
            raise

    async def get_inventory_needs_forecast(self, time_filter: str = "last_365_days", top_n_products: int = 5, periods_to_forecast: int = 3, granularity: str = "month") -> list:
        try:
            print(f"[AnalyticsService] get_inventory_needs_forecast called for filter: {time_filter}, top_n_products: {top_n_products}, periods_to_forecast: {periods_to_forecast}, granularity: {granularity}")
            from collections import defaultdict
            
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] Inventory Needs Forecast: Date range calculated.")
            
            all_orders = self.all_cached_orders
            print(f"[AnalyticsService] Inventory Needs Forecast: Using {len(all_orders)} cached orders.")
            
            filtered_orders = [
                order for order in all_orders
                if order.get("o_placed_time") and start_date <= order["o_placed_time"] <= end_date
            ]
            print(f"[AnalyticsService] Inventory Needs Forecast: Filtered down to {len(filtered_orders)} orders.")
            
            # Get historical sales data per product by period
            product_period_data = defaultdict(lambda: defaultdict(int))  # p_id -> period -> quantity
            product_names = {}  # p_id -> p_name
            product_total_quantity = defaultdict(int)  # p_id -> total_quantity_sold
            
            # Aggregate sales data by product and period
            for order in filtered_orders:
                o_placed_time = order.get("o_placed_time")
                if not o_placed_time:
                    continue
                
                # Determine period based on granularity
                if granularity == "month":
                    period_str = o_placed_time.strftime("%Y-%m")
                elif granularity == "week":
                    period_str = o_placed_time.strftime("%Y-%W")
                else:
                    raise ValueError(f"Unsupported granularity: {granularity}")
                
                # Process each item in the order
                for item in order.get("items", []):
                    p_id = item.get("p_id")
                    p_name = item.get("p_name", "")
                    oi_qty = int(item.get("oi_qty", 0))
                    
                    if p_id and oi_qty > 0:
                        product_period_data[p_id][period_str] += oi_qty
                        product_total_quantity[p_id] += oi_qty
                        if p_id not in product_names and p_name:
                            product_names[p_id] = p_name
            
            # Identify top N products by total quantity sold
            top_products = sorted(product_total_quantity.items(), key=lambda x: x[1], reverse=True)[:top_n_products]
            print(f"[AnalyticsService] Inventory Needs Forecast: Identified top {len(top_products)} products.")
            
            # Get the last period from historical data for forecasting
            all_periods = set()
            for p_id in product_period_data:
                all_periods.update(product_period_data[p_id].keys())
            
            if not all_periods:
                print(f"[AnalyticsService] Inventory Needs Forecast: No historical data available.")
                return []
            
            last_period = sorted(all_periods)[-1]
            print(f"[AnalyticsService] Inventory Needs Forecast: Last historical period: {last_period}")
            
            # Forecast for each top product using Prophet
            result = []
            for p_id, total_quantity in top_products:
                p_name = product_names.get(p_id, f"Product {p_id}")
                historical_periods = product_period_data[p_id]
                
                print(f"[AnalyticsService] Inventory Needs Forecast: Forecasting for product {p_id} ({p_name})")
                
                # Extract historical quantities sold per period for this product
                historical_data = []
                for period in sorted(historical_periods.keys()):
                    historical_data.append({
                        "period": period,
                        "quantity": historical_periods[period]
                    })
                
                # Convert to Prophet's pd.DataFrame(ds, y) format
                if len(historical_data) < 2:
                    print(f"[AnalyticsService] Inventory Needs Forecast: Insufficient data for product {p_id}. Using average calculation.")
                    # Fallback to average calculation for insufficient data
                    avg_quantity_per_period = sum(historical_periods.values()) / len(historical_periods) if historical_periods else 0
                    forecasted_demand_periods = []
                    current_period = last_period
                    
                    for i in range(1, periods_to_forecast + 1):
                        # Calculate next period
                        if granularity == "month":
                            year, month = map(int, current_period.split("-"))
                            if month == 12:
                                year += 1
                                month = 1
                            else:
                                month += 1
                            next_period = f"{year:04d}-{month:02d}"
                        elif granularity == "week":
                            year, week = map(int, current_period.split("-W"))
                            week += 1
                            if week > 52:
                                year += 1
                                week = 1
                            next_period = f"{year:04d}-W{week:02d}"
                        else:
                            raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
                        
                        forecasted_demand_periods.append({
                            "period": next_period,
                            "quantity": int(avg_quantity_per_period)
                        })
                        current_period = next_period
                else:
                    # Use Prophet for forecasting
                    df = pd.DataFrame(historical_data).rename(columns={'period': 'ds', 'quantity': 'y'})
                    
                    # Explicitly specify datetime format based on granularity
                    if granularity == 'month':
                        df['ds'] = pd.to_datetime(df['ds'], format='%Y-%m')
                    elif granularity == 'week':
                        # Append '-1' to assume weeks start on Monday (day 1 of the week)
                        df['ds'] = pd.to_datetime(df['ds'] + '-1', format='%Y-%W-%w')
                    else:
                        raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
                    
                    # Initialize, fit, and predict using Prophet model for this specific product's quantity
                    model = Prophet(growth='linear', daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
                    model.fit(df)
                    
                    # Make future dataframe for prediction with correct frequency
                    if granularity == 'month':
                        future = model.make_future_dataframe(periods=periods_to_forecast, freq='MS')
                    elif granularity == 'week':
                        # Use 'W-MON' for weeks starting on Monday
                        future = model.make_future_dataframe(periods=periods_to_forecast, freq='W-MON')
                    else:
                        raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
                    
                    # Generate prediction
                    forecast_df = model.predict(future)
                    
                    # Extract ds and yhat from forecast_df
                    forecasted_demand_periods = []
                    for _, row in forecast_df.iterrows():
                        ds = row['ds']
                        yhat = row['yhat']
                        
                        # Map back to desired period format based on granularity
                        if granularity == "month":
                            period_str = ds.strftime("%Y-%m")
                        elif granularity == "week":
                            period_str = ds.strftime("%Y-%W")
                        else:
                            raise ValueError(f"Unsupported granularity for forecasting: {granularity}")
                        
                        # Only add forecasted periods (not historical ones)
                        if period_str > last_period:
                            forecasted_demand_periods.append({
                                "period": period_str,
                                "quantity": max(0, int(round(float(yhat))))
                            })
                
                result.append({
                    "p_id": p_id,
                    "p_name": p_name,
                    "forecasted_demand_periods": forecasted_demand_periods
                })
            
            print(f"[AnalyticsService] Inventory Needs Forecast: Generated forecasts for {len(result)} products.")
            return result
            
        except Exception as e:
            print(f"[AnalyticsService] Error in get_inventory_needs_forecast: {e}")
            raise

    async def get_catalog_suggestions(self, time_filter: str = "all_time", top_n: int = 5) -> list:
        try:
            print(f"[AnalyticsService] get_catalog_suggestions called for filter: {time_filter}, top_n: {top_n}")
            from collections import defaultdict
            
            start_date, end_date = self._get_date_range(time_filter)
            print(f"[AnalyticsService] Catalog Suggestions: Date range calculated.")
            
            all_orders = self.all_cached_orders
            print(f"[AnalyticsService] Catalog Suggestions: Using {len(all_orders)} cached orders.")
            
            # Create defaultdict to store counts and last request date for problematic items
            item_requests = defaultdict(lambda: {'request_count': 0, 'last_requested': None})
            
            # Loop through all orders
            for order in all_orders:
                # Check if order is within the time filter
                o_placed_time = order.get('o_placed_time')
                if not o_placed_time or not (start_date <= o_placed_time <= end_date):
                    continue
                
                # Check if order has analysis field with error_items
                analysis = order.get('analysis')
                if not analysis or 'error_items' not in analysis:
                    continue
                
                error_items = analysis['error_items']
                if not error_items:
                    continue
                
                # Process each error item
                for error_item in error_items:
                    # Check if this is a product-related error (not found or out of stock)
                    error_message = error_item.get('error_message', '').lower()
                    
                    # Look for indicators of product not found or out of stock
                    is_product_error = any(keyword in error_message for keyword in [
                        'not found', 'out of stock', 'insufficient stock', 'unavailable'
                    ])
                    
                    if is_product_error:
                        # Get product identifier (prefer product_name, fallback to product_id)
                        item_name = error_item.get('product_name')
                        if not item_name:
                            item_name = error_item.get('product_id', 'Unknown Product')
                        
                        # Increment request count
                        item_requests[item_name]['request_count'] += 1
                        
                        # Update last requested date (keep the most recent)
                        if item_requests[item_name]['last_requested'] is None or o_placed_time > item_requests[item_name]['last_requested']:
                            item_requests[item_name]['last_requested'] = o_placed_time
            
            print(f"[AnalyticsService] Catalog Suggestions: Found {len(item_requests)} items with errors.")
            
            # Convert defaultdict into a list of dictionaries
            suggestions_list = []
            for item_name, data in item_requests.items():
                # Format the date as YYYY-MM-DD
                last_requested_str = None
                if data['last_requested']:
                    last_requested_str = data['last_requested'].strftime("%Y-%m-%d")
                
                suggestions_list.append({
                    "item_name": item_name,
                    "request_count": data['request_count'],
                    "last_requested": last_requested_str
                })
            
            # Sort by request_count in descending order
            suggestions_list.sort(key=lambda x: x['request_count'], reverse=True)
            
            # Return only the top_n suggestions
            result = suggestions_list[:top_n]
            
            print(f"[AnalyticsService] Catalog Suggestions: Returning top {len(result)} suggestions.")
            return result
            
        except Exception as e:
            print(f"[AnalyticsService] Error in get_catalog_suggestions: {e}")
            raise 