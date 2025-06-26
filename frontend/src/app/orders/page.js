"use client";

import { History, X, Package, User, Calendar, DollarSign, RefreshCw } from "lucide-react";
import { useState, useEffect, useCallback } from "react";

// Move these helpers OUTSIDE the component
const getStatusColor = (status) => {
  switch ((status || "").toLowerCase()) {
    case "confirmed":
      return "bg-green-100 text-green-800";
    case "processing":
      return "bg-blue-100 text-blue-800";
    case "waiting for confirmation":
      return "bg-yellow-100 text-yellow-800";
    case "hold":
      return "bg-red-100 text-red-800";
    default:
      return "bg-gray-100 text-gray-800";
  }
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatCurrency = (amount) => {
  if (typeof amount !== "number") amount = Number(amount) || 0;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

export default function OrdersPage() {
  // 1. ALL useState DECLARATIONS FIRST
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [ordersPerPage] = useState(10);
  const [paginatedOrders, setPaginatedOrders] = useState([]);
  const [totalPages, setTotalPages] = useState(1);

  // 2. ALL useCallback WRAPPED FUNCTION DECLARATIONS NEXT
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/get-orders`);
      if (!response.ok) throw new Error("Failed to fetch orders");
      const data = await response.json();
      setOrders(data.orders || []);
      const total = (data.orders || []).length;
      const pages = Math.ceil(total / ordersPerPage);
      setTotalPages(pages);
      setError(null);
    } catch (err) {
      setError("Failed to load orders. Please try again later.");
    } finally {
      setLoading(false);
    }
  }, [ordersPerPage, setLoading, setOrders, setTotalPages, setError]);

  const fetchOrderDetail = useCallback(async (orderId) => {
    setDetailLoading(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/get-order/${orderId}`);
      if (!response.ok) throw new Error("Failed to fetch order details");
      const data = await response.json();
      setSelectedOrder(data.order);
    } catch (err) {
      setSelectedOrder({ error: "Failed to load order details." });
    } finally {
      setDetailLoading(false);
    }
  }, [setSelectedOrder, setDetailLoading]);

  // 3. ALL useEffect HOOKS LAST
  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  useEffect(() => {
    const startIndex = (currentPage - 1) * ordersPerPage;
    const endIndex = startIndex + ordersPerPage;
    setPaginatedOrders(orders.slice(startIndex, endIndex));
  }, [orders, currentPage, ordersPerPage]);

  // All other functions after useEffect
  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  return (
    <div className="flex min-h-screen flex-col items-center bg-gray-50 p-12 font-sans">
      <div className="flex items-center gap-3 mb-8">
        <History className="h-8 w-8 text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-800">Order History</h1>
      </div>
      {loading ? (
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-lg text-gray-600">Loading orders...</span>
        </div>
      ) : error ? (
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">{error}</div>
          <button
            onClick={fetchOrders}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      ) : (
        <>
        <div className="bg-white rounded-lg shadow-md overflow-hidden w-full max-w-6xl">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-gray-100 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 font-medium text-gray-600">Order ID</th>
                <th className="px-6 py-3 font-medium text-gray-600">Customer</th>
                <th className="px-6 py-3 font-medium text-gray-600">Date</th>
                <th className="px-6 py-3 font-medium text-gray-600">Status</th>
                <th className="px-6 py-3 font-medium text-gray-600 text-right">
                  Total
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedOrders.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No orders found.
                  </td>
                </tr>
              ) : (
                paginatedOrders.map((order) => (
                  <tr
                    key={order.o_id}
                    className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => fetchOrderDetail(order.o_id)}
                  >
                    <td className="px-6 py-4 font-mono text-blue-600">
                      {order.o_id}
                    </td>
                    <td className="px-6 py-4 text-gray-800">
                      {order.c_name}
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {formatDate(order.o_placed_time)}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.o_status)}`}
                      >
                        {order.o_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-800 font-medium text-right">
                      {formatCurrency(order.total_value)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {/* Pagination Controls */}
        <div className="flex items-center justify-center mt-6 space-x-2">
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={`px-3 py-1 rounded border text-sm font-medium transition-colors ${currentPage === 1 ? 'bg-gray-200 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
          >
            Previous
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
            <button
              key={page}
              onClick={() => handlePageChange(page)}
              className={`px-3 py-1 rounded border text-sm font-medium transition-colors ${currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
            >
              {page}
            </button>
          ))}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className={`px-3 py-1 rounded border text-sm font-medium transition-colors ${currentPage === totalPages ? 'bg-gray-200 text-gray-400 border-gray-200 cursor-not-allowed' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100'}`}
          >
            Next
          </button>
          <span className="ml-4 text-gray-500 text-sm">
            Page {currentPage} of {totalPages}
          </span>
        </div>
        </>
      )}

      {/* Order Detail Modal */}
      {selectedOrder && (
        <OrderDetailModal
          order={selectedOrder}
          loading={detailLoading}
          onClose={() => setSelectedOrder(null)}
        />
      )}
    </div>
  );
}

// OrderDetailModal: shows full order details
function OrderDetailModal({ order, loading, onClose }) {
  const [isPrinting, setIsPrinting] = useState(false);

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto flex items-center justify-center">
          <div className="flex items-center gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="text-lg text-gray-600">Loading order details...</span>
          </div>
        </div>
      </div>
    );
  }
  if (!order) return null;
  if (order.error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto flex items-center justify-center">
          <div className="text-red-600 text-lg">{order.error}</div>
          <button onClick={onClose} className="ml-4 px-4 py-2 bg-blue-600 text-white rounded">Close</button>
        </div>
      </div>
    );
  }
  const items = order.items || order.products || [];

  // Print handler
  const handlePrintOrder = async (orderId) => {
    setIsPrinting(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/generate-sales-order-pdf/${orderId}`);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate PDF: ${response.status} - ${errorText}`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (err) {
      console.error("Error generating PDF:", err);
      alert(err.message || "Could not generate PDF. Please try again.");
    } finally {
      setIsPrinting(false);
    }
  };

  return (
    <div className="fixed inset-0 backdrop-blur-xs bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-800">Order Details</h2>
            <div className="flex gap-2">
              <button
                onClick={() => handlePrintOrder(order.o_id || order.order_id)}
                disabled={isPrinting}
                className="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isPrinting && <RefreshCw className="h-4 w-4 animate-spin" />}
                {isPrinting ? "Generating PDF..." : "Print"}
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="h-6 w-6 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
        <div className="p-6 text-gray-800 space-y-6">
          {/* Order Header */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
              <Package className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Order ID</p>
                <p className="font-mono text-lg font-semibold text-blue-600">{order.o_id || order.order_id}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <User className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Customer</p>
                <p className="font-semibold">{order.c_name}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">Placed</p>
                <p className="font-semibold">{order.o_placed_time || order.created_at}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="font-semibold">{formatCurrency(order.total_value)}</p>
              </div>
            </div>
          </div>
          {/* Status */}
          <div>
            <p className="text-sm text-gray-600 mb-2">Status</p>
            <span className={`px-3 py-2 text-sm font-semibold rounded-full`}>
              {order.o_status || order.status}
            </span>
          </div>
          {/* Products/Items */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Products</h3>
            <div className="space-y-2">
              {items.length === 0 && <p className="text-gray-500">No items found.</p>}
              {items.map((product, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold">{product.p_name || product.product_name}</p>
                    <p className="text-sm text-gray-600">Qty: {product.oi_qty || product.quantity}</p>
                  </div>
                  <p className="font-semibold">
                    {formatCurrency((product.oi_price || product.price) * (product.oi_qty || product.quantity))}
                  </p>
                </div>
              ))}
            </div>
          </div>
          {/* Original Email */}
          {order.email_text && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Original Email</h3>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-700 whitespace-pre-wrap">{order.email_text}</p>
              </div>
            </div>
          )}
          {/* Customer Response */}
          {order.customer_response && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Customer Response</h3>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-gray-700 whitespace-pre-wrap">{order.customer_response}</p>
              </div>
            </div>
          )}
          {/* Analysis Summary */}
          {order.analysis && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Analysis Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600">Successful Items</p>
                  <p className="text-lg font-semibold text-green-600">{order.analysis.successful_count}</p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <p className="text-sm text-gray-600">Error Items</p>
                  <p className="text-lg font-semibold text-red-600">{order.analysis.error_count}</p>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Items</p>
                  <p className="text-lg font-semibold text-blue-600">{order.analysis.total_items}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}