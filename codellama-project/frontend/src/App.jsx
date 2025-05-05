import { useState, useEffect } from 'react';

function App() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  // Fetch chat history on mount
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch('http://codellama-service.codellama.svc.cluster.local/history');
        const data = await res.json();
        setChatHistory(data.history);
      } catch (err) {
        console.error('Failed to fetch history:', err);
      }
    };
    fetchHistory();
  }, []);

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const res = await fetch('http://codellama-service.codellama.svc.cluster.local/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      setResponse(data.code);
      // Refresh history
      const historyRes = await fetch('http://codellama-service.codellama.svc.cluster.local/history');
      const historyData = await historyRes.json();
      setChatHistory(historyData.history);
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
            <pre className="bg-gray-800 text-white p-4 rounded-md overflow-auto">{response}</pre>
          </div>
        )}
      </div>
      <div className="w-full max-w-2xl mt-8">
        <h2 className="text-2xl font-semibold mb-4">Chat History</h2>
        {chatHistory.length === 0 ? (
          <p className="text-gray-500">No chat history yet.</p>
        ) : (
          <div className="space-y-4">
            {chatHistory.map((chat, index) => (
              <div key={index} className="bg-white p-4 rounded-lg shadow-md">
                <p className="text-sm text-gray-500">{chat.timestamp}</p>
                <p className="font-semibold">Prompt:</p>
                <p className="mb-2">{chat.prompt}</p>
                <p className="font-semibold">Response:</p>
                <pre className="bg-gray-800 text-white p-2 rounded-md overflow-auto">{chat.response}</pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;