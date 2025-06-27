import Link from "next/link";
import { Zap, FileText, ShieldCheck, LayoutDashboard } from "lucide-react";

const FeatureCard = ({ icon, title, children }) => {
  return (
    <div className="flex flex-col items-center p-6 text-center bg-white rounded-lg shadow-md transition hover:shadow-xl">
      <div className="mb-4 bg-blue-100 p-4 rounded-full">{icon}</div>
      <h3 className="mb-2 text-xl font-bold text-gray-800">{title}</h3>
      <p className="text-gray-600">{children}</p>
    </div>
  );
};

export default function LandingPage() {
  return (
    <>
      {/* Hero Section */}
      <section className="text-center py-24 bg-white">
        <div className="container mx-auto px-6">
          <Zap className="mx-auto h-16 w-16 text-blue-600" />
          <h1 className="mt-4 text-4xl font-extrabold text-gray-900 md:text-6xl">
            Transform Email Orders into Actionable Data
          </h1>
          <p className="mt-4 max-w-3xl mx-auto text-lg text-gray-600">
            Our AI-powered platform intelligently extracts, validates, and
            processes customer orders from any email format, saving you time and
            eliminating errors.
          </p>
          <Link
            href="/email-processor"
            className="mt-8 inline-block bg-blue-600 text-white font-bold py-3 px-8 rounded-lg text-lg transition hover:bg-blue-700"
          >
            Go to Processor
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800">
              Why Use Our AI Processor?
            </h2>
            <p className="mt-2 text-gray-600">
              Streamline your workflow with powerful, intelligent features.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<FileText className="h-8 w-8 text-blue-600" />}
              title="Automated Data Extraction"
            >
              No more manual copy-pasting. Our AI reads emails and pulls out
              customer and order details automatically.
            </FeatureCard>
            <FeatureCard
              icon={<ShieldCheck className="h-8 w-8 text-blue-600" />}
              title="Instant Validation"
            >
              Cross-reference orders against your inventory and customer lists
              in real-time to prevent mistakes before they happen.
            </FeatureCard>
            <FeatureCard
              icon={<LayoutDashboard className="h-8 w-8 text-blue-600" />}
              title="Centralized Dashboard"
            >
              Manage orders, view inventory, and analyze sales trends all from
              one convenient and intuitive interface.
            </FeatureCard>
          </div>
        </div>
      </section>
    </>
  );
}