import { LayoutDashboard, DollarSign, ShoppingCart, Users } from "lucide-react";

const StatCard = ({ title, value, icon }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md flex items-center gap-4">
      <div className="bg-blue-100 p-3 rounded-full">{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  );
};

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col items-center bg-gray-50 p-12 font-sans">
      <div className="flex items-center gap-3 mb-8">
        <LayoutDashboard className="h-8 w-8 text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-800">
          Analysis Dashboard
        </h1>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Revenue"
          value="$12,450"
          icon={<DollarSign className="h-6 w-6 text-blue-600" />}
        />
        <StatCard
          title="Orders This Month"
          value="132"
          icon={<ShoppingCart className="h-6 w-6 text-blue-600" />}
        />
        <StatCard
          title="New Customers"
          value="12"
          icon={<Users className="h-6 w-6 text-blue-600" />}
        />
        <StatCard
          title="Avg. Order Value"
          value="$94.32"
          icon={<DollarSign className="h-6 w-6 text-blue-600" />}
        />
      </div>

      {/* Placeholder for a chart */}
      <div className="mt-12 w-full max-w-3xl bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">
          Sales Trends
        </h2>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded-md">
          <p className="text-gray-500">Chart component will be rendered here.</p>
        </div>
      </div>
    </div>
  );
}