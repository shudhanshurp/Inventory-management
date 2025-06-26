 "use client";

import { useState, useEffect } from 'react';
import { Copy, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

export default function TestCasesPage() {
  const [generatedCases, setGeneratedCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const handleGenerateCases = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/generate-test-cases`);
      
      if (!response.ok) {
        throw new Error(`Failed to generate test cases: ${response.status}`);
      }
      
      const data = await response.json();
      setGeneratedCases(data.test_cases || []);
    } catch (err) {
      setError(err.message || 'Failed to generate test cases');
      console.error('Error generating test cases:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'Valid':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Hold':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Failed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Test Case Generator</h1>
          <p className="text-gray-600">
            Generate test cases for order processing with various scenarios including valid orders, 
            low stock situations, and invalid data.
          </p>
        </div>

        {/* Generate Button */}
        <div className="mb-8">
          <button
            onClick={handleGenerateCases}
            disabled={loading}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? (
              <>
                <RefreshCw className="h-5 w-5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <RefreshCw className="h-5 w-5" />
                Generate Test Cases
              </>
            )}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Error:</span>
              <span>{error}</span>
            </div>
          </div>
        )}

        {/* Test Cases Display */}
        {generatedCases.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">
              Generated Test Cases ({generatedCases.length})
            </h2>
            
            {generatedCases.map((testCase, index) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
              >
                {/* Test Case Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getTypeColor(testCase.type)}`}>
                        {testCase.type}
                      </span>
                      <h3 className="text-lg font-semibold text-gray-800">
                        Test Case {index + 1}
                      </h3>
                    </div>
                  </div>
                  <p className="text-gray-600">{testCase.description}</p>
                </div>

                {/* Email Content */}
                <div className="p-6 space-y-4">
                  {/* Subject */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subject:
                    </label>
                    <div className="p-3 bg-gray-50 rounded-lg border">
                      <p className="text-gray-800 font-medium">{testCase.subject}</p>
                    </div>
                  </div>

                  {/* Email Body */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Email Body:
                      </label>
                      <button
                        onClick={() => copyToClipboard(testCase.body, index)}
                        className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 hover:text-blue-800 transition-colors"
                      >
                        {copiedIndex === index ? (
                          <>
                            <CheckCircle className="h-3 w-3" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                    <textarea
                      value={testCase.body}
                      readOnly
                      className="w-full h-48 p-3 bg-gray-50 border border-gray-200 rounded-lg resize-none text-sm text-gray-800 font-mono"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && generatedCases.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <RefreshCw className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              No test cases generated yet
            </h3>
            <p className="text-gray-500">
              Click the button above to create test scenarios.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}