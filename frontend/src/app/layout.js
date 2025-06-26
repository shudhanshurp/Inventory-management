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
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white-100`}
      >
        <div className="flex flex-col min-h-screen bg-white-100">
          <Navbar /> {/* 2. Add the Navbar component here */}
          <main className="flex-grow overflow-hidden">{children}</main>
        </div>
      </body>
    </html>
  );
}