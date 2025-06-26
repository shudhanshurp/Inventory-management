"use client";

import { Warehouse } from "lucide-react";
import { useState, useEffect } from "react";

const StockStatus = ({ stock }) => {
  if (stock === 0) {
    return (
      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
        Out of Stock
      </span>
    );
  }
  if (stock <= 5) {
    return (
      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">
        Low Stock
      </span>
    );
  }
  return (
    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
      In Stock
    </span>
  );
};

const formatCurrency = (amount) => {
  if (typeof amount !== "number") amount = Number(amount) || 0;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
};

export default function InventoryPage() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [productsPerPage] = useState(10);
  const [paginatedProducts, setPaginatedProducts] = useState([]);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchInventory();
  }, []);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:5001/api/products");
      if (!response.ok) throw new Error("Failed to fetch inventory");
      const data = await response.json();
      // Defensive: ensure inventory is always an array
      let products = [];
      if (Array.isArray(data.products)) {
        products = data.products;
      } else if (data.products && typeof data.products === "object") {
        products = Object.values(data.products);
      }
      setInventory(products);
      const total = products.length;
      const pages = Math.ceil(total / productsPerPage);
      setTotalPages(pages);
      setError(null);
    } catch (err) {
      setError("Failed to load inventory. Please try again later.");
      setInventory([]);
    } finally {
      setLoading(false);
    }
  };

  // Update paginatedProducts whenever inventory, currentPage, or productsPerPage changes
  useEffect(() => {
    const startIndex = (currentPage - 1) * productsPerPage;
    const endIndex = startIndex + productsPerPage;
    setPaginatedProducts(inventory.slice(startIndex, endIndex));
  }, [inventory, currentPage, productsPerPage]);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-12 font-sans">
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-lg text-gray-600">Loading inventory...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-12 font-sans">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">{error}</div>
          <button
            onClick={fetchInventory}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center bg-gray-50 p-12 font-sans">
      <div className="flex items-center gap-3 mb-8">
        <Warehouse className="h-8 w-8 text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-800">Product Inventory</h1>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-100 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 font-medium text-gray-600">
                Product ID
              </th>
              <th className="px-6 py-3 font-medium text-gray-600">
                Product Name
              </th>
              <th className="px-6 py-3 font-medium text-gray-600">Price</th>
              <th className="px-6 py-3 font-medium text-gray-600 text-center">
                Stock Level
              </th>
              <th className="px-6 py-3 font-medium text-gray-600 text-center">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedProducts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  No products found.
                </td>
              </tr>
            ) : (
              paginatedProducts.map((item) => (
                <tr key={item.p_id} className="border-b border-gray-200">
                  <td className="px-6 py-4 font-mono text-blue-600">
                    {item.p_id}
                  </td>
                  <td className="px-6 py-4 text-gray-800">
                    {item.p_name}
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {formatCurrency(item.p_price)}
                  </td>
                  <td className="px-6 py-4 text-gray-800 font-medium text-center">
                    {item.p_stock}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <StockStatus stock={item.p_stock} />
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
    </div>
  );
}