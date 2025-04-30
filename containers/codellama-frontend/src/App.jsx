import { useState } from 'react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const res = await fetch('http://codellama-service.default.svc.cluster.local/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setResponse(data.code);
    } catch (err) {
      setError('Failed to fetch response. Is the CodeLlama service running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <h1 className="text-3xl font-bold mb-6">CodeLlama Assistant</h1>
      <div className="w-full max-w-2xl bg-white p-6 rounded-lg shadow-md">
        <textarea
          className="w-full p-2 border rounded-md mb-4"
          rows="4"
          placeholder="Enter your prompt (e.g., 'Write a Python function to list Kubernetes pods')"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Code'}
        </button>
        {error && <p className="text-red-500 mt-4">{error}</p>}
        {response && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">Generated Code:</h2>
            <pre className="bg-gray-800 text-white p-4 rounded-md overflow-auto">
              {response}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;