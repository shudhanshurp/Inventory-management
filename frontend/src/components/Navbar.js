import Link from "next/link";
import { BotMessageSquare } from "lucide-react"; // A nice icon for the logo

const Navbar = () => {
  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <nav className="container mx-auto flex items-center justify-between p-4">
        {/* Logo / App Name */}
        <Link
          href="/"
          className="flex items-center gap-2 text-xl font-bold text-gray-800"
        >
          <BotMessageSquare className="h-7 w-7 text-blue-600" />
          <span>AI Processor</span>
        </Link>

        {/* Navigation Links */}
        <ul className="flex items-center gap-6 text-sm font-medium text-gray-600">
          <li>
            <Link
              href="/email-processor"
              className="transition hover:text-blue-600"
            >
              Email Processor
            </Link>
          </li>
          <li>
            <Link
              href="/orders"
              className="transition hover:text-blue-600"
            >
              Orders
            </Link>
          </li>
          <li>
            <Link
              href="/inventory"
              className="transition hover:text-blue-600"
            >
              Inventory
            </Link>
          </li>
          <li>
            <Link
              href="/dashboard"
              className="transition hover:text-blue-600"
            >
              Analysis Dashboard
            </Link>
          </li>
          <li>
            <Link
              href="/test-cases"
              className="transition hover:text-blue-600"
            >
              Test Cases
            </Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Navbar;