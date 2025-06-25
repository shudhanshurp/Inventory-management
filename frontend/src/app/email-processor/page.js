// frontend/src/app/page.jsx
"use client";

import { useState } from "react";

export default function HomePage() {
  const [emailText, setEmailText] = useState("");
  const [response, setResponse] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResponse(null);
    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:5001/api/process-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email_text: emailText }),
      });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else if (data.customer_message && data.customer_message.body) {
        let display = "";
        if (data.customer_message.subject) {
          display += `Subject: ${data.customer_message.subject}\n`;
        }
        if (data.customer_message.status) {
          display += `Status: ${data.customer_message.status}\n`;
        }
        display += `\n${data.customer_message.body}`;
        setResponse(display);
      } else {
        setResponse(JSON.stringify(data, null, 2)); // fallback: show full JSON
      }
    } catch (err) {
      setError("Failed to process order: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center bg-gray-50 p-12 font-sans">
      <div className="w-full max-w-3xl">
        <h1 className="mb-2 text-4xl font-bold text-gray-800">
          AI Email Order Processor
        </h1>
        <p className="mb-8 text-black">
          Paste the customer's email below to automatically extract and validate
          the order.
        </p>

        <form onSubmit={handleSubmit}>
          <textarea
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
            // placeholder="Hi team,&#10;&#10;Please place an order for me. My customer ID is CUST101.&#10;&#10;I need:&#10;- 2x PROD001&#10;- 1x PROD003&#10;&#10;Thanks,&#10;Alice"
            placeholder="Enter your email here"
            className="h-48 w-full text-black rounded-lg border border-gray-300 p-4 shadow-sm transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
            required
          />
          <button
            type="submit"
            disabled={isLoading}
            className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-3 font-bold text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? "Processing..." : "Process Order"}
          </button>
        </form>

        {(response || error) && (
          <div className="mt-8 w-full">
            <h2 className="mb-4 text-2xl font-semibold text-gray-700">
              Generated Response
            </h2>
            <div
              className={`whitespace-pre-wrap rounded-lg p-6 ${
                error
                  ? "border border-red-300 bg-red-100 text-red-800"
                  : "border border-green-300 bg-green-100 text-green-800"
              }`}
            >
              {error || response}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}