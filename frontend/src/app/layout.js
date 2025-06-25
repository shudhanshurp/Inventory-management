import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar"; // 1. Import the Navbar

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "AI Order Processor", // Updated title
  description: "Empowering Businesses with AI Solutions", // Updated description
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50`}
      >
        <div className="flex min-h-screen flex-col">
          <Navbar /> {/* 2. Add the Navbar component here */}
          <main className="flex-grow">{children}</main>
        </div>
      </body>
    </html>
  );
}