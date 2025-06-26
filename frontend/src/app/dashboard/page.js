"use client";
import { useState, useEffect } from 'react';
import { LayoutDashboard, DollarSign, ShoppingCart, Users, RefreshCw, AlertTriangle, XCircle } from "lucide-react";
import { ResponsiveLine } from '@nivo/line';
import { ResponsiveBar } from '@nivo/bar';
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css'; // Core Swiper styles
import 'swiper/css/navigation'; // If you use navigation arrows
import { Navigation } from 'swiper/modules'; // Import modules if you need them (e.g., for arrows/dots)

const formatCurrency = (amount) => {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount || 0);
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (error) {
    return 'Invalid Date';
  }
};

const StatCard = ({ title, value, icon }) => {
  return (
    <div className="bg-white p-3 md:p-4 lg:p-6 rounded-lg shadow-md flex items-center gap-2 md:gap-4">
      <div className="bg-blue-100 p-2 md:p-3 rounded-full">{icon}</div>
      <div className="min-w-0 flex-1">
        <p className="text-xs md:text-sm text-gray-500 truncate">{title}</p>
        <p className="text-lg md:text-xl lg:text-2xl font-bold text-gray-800 truncate">{value}</p>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  const [kpis, setKpis] = useState({});
  const [salesTrends, setSalesTrends] = useState([]);
  const [orderStatusDistribution, setOrderStatusDistribution] = useState({});
  const [inventoryHealth, setInventoryHealth] = useState({});
  const [productPerformance, setProductPerformance] = useState([]);
  const [salesForecast, setSalesForecast] = useState([]);
  const [inventoryNeedsForecast, setInventoryNeedsForecast] = useState([]);
  const [catalogSuggestions, setCatalogSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState("last_30_days");

  // Revised Nivo Data Strategy: connect forecast to last historical point
  const lastHistoricalIndex = salesForecast.map(item => item.type).lastIndexOf('historical');
  const lastHistorical = salesForecast[lastHistoricalIndex];
  const forecastSeries =
    lastHistoricalIndex !== -1
      ? [
          // Start with the last historical point for connection
          { x: lastHistorical.period, y: lastHistorical.revenue },
          ...salesForecast.slice(lastHistoricalIndex + 1).map(item => ({ x: item.period, y: item.revenue })),
        ]
      : [];

  const nivoSalesData = [
    {
      id: 'Historical Revenue',
      data: salesForecast.map(item => ({
        x: item.period,
        y: item.type === 'historical' ? item.revenue : null,
      })),
    },
    {
      id: 'Forecasted Revenue',
      data: forecastSeries,
    },
  ];

  const nivoOrderStatusData = Object.keys(orderStatusDistribution).map(status => ({
    status: status,
    count: orderStatusDistribution[status],
  }));

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Determine granularity based on time filter
      const salesGranularity = (timeFilter === 'last_7_days' || timeFilter === 'last_30_days') ? 'week' : 'month';
      
      // Fetch KPIs, Sales Trends, Order Status, Inventory Health, Product Performance, Sales Forecast, Inventory Needs Forecast, and Catalog Suggestions concurrently using Promise.all
      const [kpisRes, salesTrendsRes, orderStatusRes, inventoryHealthRes, productPerformanceRes, salesForecastRes, inventoryNeedsForecastRes, catalogSuggestionsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/kpis?time_filter=${timeFilter}`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/sales-trends?time_filter=${timeFilter}&granularity=${salesGranularity}`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/order-status?time_filter=${timeFilter}`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/inventory-health`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/product-performance?time_filter=${timeFilter}&top_n=5`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/forecast/sales?time_filter=${timeFilter}&periods=3&granularity=${salesGranularity}`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/forecast/inventory-needs?time_filter=${timeFilter}&top_n=5&periods=3&granularity=month`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/analytics/suggest-catalog-items?time_filter=${timeFilter}&top_n=5`)
      ]);
      
      if (!kpisRes.ok || !salesTrendsRes.ok || !orderStatusRes.ok || !inventoryHealthRes.ok || !productPerformanceRes.ok || !salesForecastRes.ok || !inventoryNeedsForecastRes.ok || !catalogSuggestionsRes.ok) {
        throw new Error('Failed to fetch dashboard data');
      }
      
      const kpisData = await kpisRes.json();
      const salesTrendsData = await salesTrendsRes.json();
      const orderStatusData = await orderStatusRes.json();
      const inventoryHealthData = await inventoryHealthRes.json();
      const productPerformanceData = await productPerformanceRes.json();
      const salesForecastData = await salesForecastRes.json();
      const inventoryNeedsForecastData = await inventoryNeedsForecastRes.json();
      const catalogSuggestionsData = await catalogSuggestionsRes.json();
      
      setKpis(kpisData);
      setSalesTrends(salesTrendsData);
      setOrderStatusDistribution(orderStatusData);
      setInventoryHealth(inventoryHealthData);
      setProductPerformance(productPerformanceData);
      setSalesForecast(salesForecastData);
      setInventoryNeedsForecast(inventoryNeedsForecastData);
      setCatalogSuggestions(catalogSuggestionsData);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [timeFilter]);

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-12 font-sans">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-4">Error: {error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="
    grid grid-cols-7 grid-rows-[auto_0.5fr_1.2fr_1fr_1fr_1fr_0.7fr] gap-4 // Use gap-4 for consistency
    w-full h-full px-4 md:px-8 py-4 md:py-6 // Use h-full to fill its parent's (main's) height
    bg-gray-50 font-sans overflow-hidden
  ">
      {/* Analysis Dashboard Title */}
      <div className="col-start-1 col-end-6 row-start-1 row-end-2 flex items-center gap-3">
        <LayoutDashboard className="h-6 w-6 md:h-8 md:w-8 text-gray-700" />
        <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-gray-800">
          Analysis Dashboard
        </h1>
      </div>

      {/* Time Filter Selection */}
      <div className="col-start-6 col-end-8 row-start-1 row-end-2 flex justify-end items-center">
        <div className="flex space-x-2">
          <button
            value="last_7_days"
            onClick={() => setTimeFilter('last_7_days')}
            className={`
              px-3 py-1 text-sm font-medium rounded-md border
              ${timeFilter === 'last_7_days'
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-100'
              }
              transition-colors
            `}
          >
            Last 7 Days
          </button>
          <button
            value="last_30_days"
            onClick={() => setTimeFilter('last_30_days')}
            className={`
              px-3 py-1 text-sm font-medium rounded-md border
              ${timeFilter === 'last_30_days'
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-100'
              }
              transition-colors
            `}
          >
            Last 30 Days
          </button>
          <button
            value="last_365_days"
            onClick={() => setTimeFilter('last_365_days')}
            className={`
              px-3 py-1 text-sm font-medium rounded-md border
              ${timeFilter === 'last_365_days'
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-100'
              }
              transition-colors
            `}
          >
            Last 365 Days
          </button>
          <button
            value="all_time"
            onClick={() => setTimeFilter('all_time')}
            className={`
              px-3 py-1 text-sm font-medium rounded-md border
              ${timeFilter === 'all_time'
                ? 'bg-blue-600 text-white border-blue-600 hover:bg-blue-700'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-100'
              }
              transition-colors
            `}
          >
            All Time
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="col-start-1 col-end-6 row-start-2 row-end-3 grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          title="Total Revenue"
          value={formatCurrency(kpis.totalRevenue)}
          icon={<DollarSign className="h-4 w-4 md:h-6 md:w-6 text-blue-600" />}
        />
        <StatCard
          title="Total Orders"
          value={kpis.totalOrders || 0}
          icon={<ShoppingCart className="h-4 w-4 md:h-6 md:w-6 text-blue-600" />}
        />
        <StatCard
          title="No. of Customers"
          value={kpis.newCustomers || 0}
          icon={<Users className="h-4 w-4 md:h-6 md:w-6 text-blue-600" />}
        />
        <StatCard
          title="Avg. Order Value"
          value={formatCurrency(kpis.avgOrderValue)}
          icon={<DollarSign className="h-4 w-4 md:h-6 md:w-6 text-blue-600" />}
        />
      </div>

      {/* Sales Trends Chart */}
      <div className="col-start-1 col-end-4 row-start-3 row-end-6 bg-white p-3 md:p-4 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2 md:mb-4">
          Sales Trends & Forecast
        </h2>
        {loading ? (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-md">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:h-6 md:w-6 text-blue-600 animate-spin" />
              <p className="text-sm md:text-base text-gray-600">Loading chart data...</p>
            </div>
          </div>
        ) : salesForecast.length > 0 ? (
          <div className="h-full w-full relative">
            <ResponsiveLine
              data={nivoSalesData}
              margin={{ top: 20, right: 30, bottom: 60, left: 70 }}
              xScale={{ type: 'point' }}
              yScale={{ type: 'linear', min: 'auto', max: 'auto' }}
              axisBottom={{
                tickRotation: -45,
                legend: 'Period',
                legendOffset: 50
              }}
              axisLeft={{
                legend: 'Revenue ($)',
                legendOffset: -60
              }}
              pointSize={6}
              pointBorderWidth={2}
              pointBorderColor={{ from: 'serieColor' }}
              enableGridX={false}
              enableGridY={true}
              colors={['#3B82F6', '#10B981']}
              curve="monotoneX"
              enableSlices="x"
              animate={true}
              motionConfig="stiff"
              lineWidth={3}
              lineStyle={[
                { strokeDasharray: '0' }, // Solid line for historical
                { strokeDasharray: '5,5' } // Dashed line for forecast
              ]}
              tooltip={({ point }) => (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                  <div className="font-semibold text-gray-800">{point.data.x}</div>
                  <div className={`font-medium ${point.serieId === 'Historical Revenue' ? 'text-blue-600' : 'text-green-600'}`}>
                    {point.serieId}: {formatCurrency(point.data.y)}
                  </div>
                  {point.serieId === 'Forecasted Revenue' && (
                    <div className="text-xs text-gray-500 mt-1">(Projected)</div>
                  )}
                </div>
              )}
            />
          </div>
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-md">
            <p className="text-sm md:text-base text-gray-500">No sales data available for this period.</p>
          </div>
        )}
      </div>

      {/* Order Status Distribution Chart */}
      <div className="col-start-4 col-end-6 row-start-3 row-end-6 bg-white p-3 md:p-4 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2 md:mb-4">
          Order Status Distribution
        </h2>
        {loading ? (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-md">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:h-6 md:w-6 text-blue-600 animate-spin" />
              <p className="text-sm md:text-base text-gray-600">Loading chart data...</p>
            </div>
          </div>
        ) : nivoOrderStatusData.length > 0 ? (
          <div className="h-full w-full relative">
            <ResponsiveBar
              data={nivoOrderStatusData}
              keys={['count']}
              indexBy="status"
              margin={{ top: 20, right: 30, bottom: 60, left: 70 }}
              padding={0.3}
              colors={{ scheme: 'nivo' }}
              axisBottom={{
                legend: 'Order Status',
                legendOffset: 50
              }}
              axisLeft={{
                legend: 'Number of Orders',
                legendOffset: -60
              }}
              enableLabel={false}
              labelSkipWidth={12}
              labelSkipHeight={12}
              tooltip={({ data }) => (
                <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                  <div className="font-semibold text-gray-800">{data.status}</div>
                  <div className="text-blue-600">{data.count} orders</div>
                </div>
              )}
              animate={true}
              motionConfig="stiff"
            />
          </div>
        ) : (
          <div className="h-full flex items-center justify-center bg-gray-50 rounded-md">
            <p className="text-sm md:text-base text-gray-500">No order status data available for this period.</p>
          </div>
        )}
      </div>

      {/* Top Selling Products - Sidebar */}
      <div className="col-start-6 col-end-8 row-start-2 row-end-4 bg-white p-3 md:p-4 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2 md:mb-4">
          Top Selling Products
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-4 md:py-8">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:h-6 md:w-6 text-blue-600 animate-spin" />
              <p className="text-xs md:text-sm text-gray-600">Loading...</p>
            </div>
          </div>
        ) : productPerformance.length > 0 ? (
          <div className="flex-1 bg-green-50 border border-green-200 rounded-lg overflow-hidden overflow-y-auto h-full">
            <table className="w-full">
              <thead className="bg-green-100 sticky top-0">
                <tr>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-green-800">ID</th>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-green-800">Name</th>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-green-800">Qty</th>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-green-800">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {productPerformance.map((product, index) => (
                  <tr key={index} className="border-t border-green-200">
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm text-gray-700">{product.p_id}</td>
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm text-gray-700 truncate">{product.p_name}</td>
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm font-semibold text-green-600">{product.total_quantity_sold}</td>
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm font-semibold text-green-600">{formatCurrency(product.total_revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs md:text-sm text-gray-500 italic">No product performance data available for this period.</p>
        )}
      </div>

      {/* Catalog Item Suggestions - Sidebar */}
      <div className="col-start-6 col-end-8 row-start-4 row-end-6 bg-white p-3 md:p-4 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2 md:mb-4">
          Catalog Suggestions
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-4 md:py-8">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:h-6 md:w-6 text-blue-600 animate-spin" />
              <p className="text-xs md:text-sm text-gray-600">Loading...</p>
            </div>
          </div>
        ) : catalogSuggestions.length > 0 ? (
          <div className="flex-1 bg-orange-50 border border-orange-200 rounded-lg overflow-hidden overflow-y-auto h-full">
            <table className="w-full">
              <thead className="bg-orange-100 sticky top-0">
                <tr>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-orange-800">Item</th>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-orange-800">Count</th>
                  <th className="px-2 md:px-4 py-1 md:py-2 text-left text-xs md:text-sm font-medium text-orange-800">Last</th>
                </tr>
              </thead>
              <tbody>
                {catalogSuggestions.map((suggestion, index) => (
                  <tr key={index} className="border-t border-orange-200">
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm text-gray-700 font-medium truncate">{suggestion.item_name}</td>
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm font-semibold text-orange-600">{suggestion.request_count}</td>
                    <td className="px-2 md:px-4 py-1 md:py-2 text-xs md:text-sm text-gray-700">{formatDate(suggestion.last_requested)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-xs md:text-sm text-gray-500 italic">No catalog suggestions available for this period.</p>
        )}
      </div>

      {/* Inventory Insights */}
      <div className="col-start-1 col-end-5 row-start-6 row-end-8 bg-white p-3 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2">
          Inventory Insights
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-4 md:py-8">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:w-6 text-blue-600 animate-spin" />
              <p className="text-sm md:text-base text-gray-600">Loading inventory data...</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-grow">
            {/* Total Inventory Value Card */}
            <div className="bg-blue-50 p-4 md:p-6 rounded-lg shadow-md flex flex-col justify-between">
              <div className="flex items-center gap-3 mb-2">
                <div className="bg-blue-100 p-2 md:p-3 rounded-full">
                  <DollarSign className="h-4 w-4 md:w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-sm md:text-sm font-semibold text-blue-800">Total Inventory Value</h3>
                </div>
              </div>
              <p className="text-lg md:text-xl lg:text-2xl font-bold text-blue-900">
                {formatCurrency(inventoryHealth.totalInventoryValue)}
              </p>
            </div>

            {/* Low Stock Items Card with Swiper */}
            <div className="bg-yellow-50 p-4 md:p-6 rounded-lg shadow-md flex flex-col">
              <div className="flex items-center gap-3 mb-3">
                <div className="bg-yellow-100 p-2 md:p-3 rounded-full">
                  <AlertTriangle className="h-4 w-4 md:w-6 text-yellow-600" />
                </div>
                <div>
                  <h3 className="text-sm md:text-sm font-semibold text-yellow-800">
                    Low Stock Items ({inventoryHealth.lowStockItems ? inventoryHealth.lowStockItems.length : 0})
                  </h3>
                </div>
              </div>
              {inventoryHealth.lowStockItems && inventoryHealth.lowStockItems.length > 0 ? (
                <div className="flex-1">
                  <Swiper
                    modules={[Navigation]}
                    spaceBetween={10}
                    slidesPerView={1}
                    navigation={true}
                    className="w-full h-full"
                  >
                    {inventoryHealth.lowStockItems.map((item, index) => (
                      <SwiperSlide key={index}>
                        <div className="bg-white p-3 rounded-lg shadow-sm h-full flex items-center justify-between">
                          <p className="text-sm md:text-base font-semibold text-gray-800 mb-1">{item.p_name}</p>
                          <p className="text-xs md:text-sm text-gray-600 mb-2">ID: {item.p_id}</p>
                          {/* <p className="text-lg md:text-xl font-bold text-red-600">Stock: {item.p_stock}</p> */}
                        </div>
                      </SwiperSlide>
                    ))}
                  </Swiper>
                </div>
              ) : (
                <p className="text-xs md:text-sm text-gray-500 italic flex-1 flex items-center">
                  No items are currently low in stock.
                </p>
              )}
            </div>

            {/* Out of Stock Items Card with Swiper */}
            <div className="bg-red-50 p-4 md:p-6 rounded-lg shadow-md flex flex-col">
              <div className="flex items-center gap-3 mb-3">
                <div className="bg-red-100 p-2 md:p-3 rounded-full">
                  <XCircle className="h-4 w-4 md:w-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-sm md:text-sm font-semibold text-red-800">
                    Out of Stock Items ({inventoryHealth.outOfStockItems ? inventoryHealth.outOfStockItems.length : 0})
                  </h3>
                </div>
              </div>
              {inventoryHealth.outOfStockItems && inventoryHealth.outOfStockItems.length > 0 ? (
                <div className="flex-1">
                  <Swiper
                    modules={[Navigation]}
                    spaceBetween={10}
                    slidesPerView={1}
                    navigation={true}
                    className="w-full h-full"
                  >
                    {inventoryHealth.outOfStockItems.map((item, index) => (
                      <SwiperSlide key={index}>
                        <div className="bg-white p-3 rounded-lg shadow-sm h-full flex items-center justify-between">
                          <p className="text-sm md:text-base font-semibold text-gray-800 mb-1">{item.p_name}</p>
                          <p className="text-xs md:text-sm text-gray-600 mb-2">ID: {item.p_id}</p>
                          {/* <p className="text-lg md:text-xl font-bold text-red-600">Stock: {item.p_stock}</p> */}
                        </div>
                      </SwiperSlide>
                    ))}
                  </Swiper>
                </div>
              ) : (
                <p className="text-xs md:text-sm text-gray-500 italic flex-1 flex items-center">
                  No items are currently out of stock.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Future Inventory Needs */}
      <div className="col-start-5 col-end-8 row-start-6 row-end-8 bg-white p-3 md:p-4 rounded-lg shadow-md flex flex-col">
        <h2 className="text-lg md:text-xl font-semibold text-gray-700 mb-2">
          Future Inventory Needs
        </h2>
        {loading ? (
          <div className="flex items-center justify-center py-4 md:py-8">
            <div className="flex items-center gap-2 md:gap-3">
              <RefreshCw className="h-4 w-4 md:h-6 md:w-6 text-blue-600 animate-spin" />
              <p className="text-sm md:text-base text-gray-600">Loading inventory forecast data...</p>
            </div>
          </div>
        ) : inventoryNeedsForecast.length > 0 ? (
          <div className="flex-1">
            <Swiper
              modules={[Navigation]}
              spaceBetween={20}
              slidesPerView={1}
              navigation={true}
              className="w-full h-full"
            >
              {inventoryNeedsForecast.map((product, index) => (
                <SwiperSlide key={index}>
                  <div className="h-full flex flex-col justify-center items-center">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      {/* Card 1: Product Name & ID */}
                      <div className="bg-purple-100 p-4 rounded-lg shadow-sm">
                        <h3 className="text-sm md:text-base font-semibold text-purple-800 mb-1">{product.p_name}</h3>
                        <p className="text-xs md:text-sm text-purple-600 font-medium">ID: {product.p_id}</p>
                      </div>

                      {/* Cards 2-4: Period & Forecasted Quantity */}
                      {product.forecasted_demand_periods.map((period, periodIndex) => (
                        <div key={periodIndex} className="p-4 bg-white rounded-lg shadow-sm">
                          <p className="text-xs md:text-sm text-gray-600 mb-1">Period</p>
                          <p className="text-sm md:text-base font-semibold text-gray-800 mb-2">{period.period}</p>
                          <p className="text-xs md:text-sm text-gray-600 mb-1">Forecasted Qty</p>
                          <p className="text-lg md:text-xl font-bold text-purple-600">{period.quantity} units</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </SwiperSlide>
              ))}
            </Swiper>
          </div>
        ) : (
          <p className="text-xs md:text-sm text-gray-500 italic">No inventory forecast data available for this period.</p>
        )}
      </div>
    </div>
  );
}