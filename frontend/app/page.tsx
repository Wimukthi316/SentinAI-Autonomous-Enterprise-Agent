"use client";

import { useState, useEffect } from "react";

const API_BASE_URL = "http://localhost:8000";

interface AgentStatus {
  agent_id: string;
  status: string;
  capabilities: string[];
}

interface ChatResponse {
  response: string;
  agent_id: string;
  status: string;
}

export default function Home() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      if (response.ok) {
        setBackendConnected(true);
        fetchAgentStatus();
      }
    } catch (error) {
      console.error("Backend not connected:", error);
      setBackendConnected(false);
    }
  };

  const fetchAgentStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agents/status`);
      const data: AgentStatus = await response.json();
      setAgentStatus(data);
    } catch (error) {
      console.error("Failed to fetch agent status:", error);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = message.trim();
    setMessage("");
    setChatHistory((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/agents/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data: ChatResponse = await response.json();
      setChatHistory((prev) => [...prev, { role: "assistant", content: data.response }]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Failed to connect to the backend. Make sure the server is running." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      {/* Header */}
      <div className="w-full max-w-4xl mb-8">
        <h1 className="text-4xl font-bold text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          SentinAI
        </h1>
        <p className="text-center text-gray-400 mt-2">
          Autonomous AI Agent powered by LangChain & Google Gemini
        </p>

        {/* Connection Status */}
        <div className="flex justify-center mt-4 gap-4">
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                backendConnected ? "bg-green-500" : "bg-red-500"
              }`}
            />
            <span className="text-sm text-gray-400">
              Backend: {backendConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
          {agentStatus && (
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-sm text-gray-400">
                Agent: {agentStatus.status}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Chat Container */}
      <div className="w-full max-w-4xl flex-1 bg-slate-800/50 rounded-lg border border-slate-700 flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 min-h-[400px]">
          {chatHistory.length === 0 ? (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg">Welcome to SentinAI!</p>
              <p className="text-sm mt-2">Send a message to start chatting with the AI agent.</p>
              {agentStatus && (
                <div className="mt-4 text-xs">
                  <p>Capabilities: {agentStatus.capabilities.join(", ")}</p>
                </div>
              )}
            </div>
          ) : (
            chatHistory.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-gray-100"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-700 p-3 rounded-lg">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={sendMessage} className="p-4 border-t border-slate-700">
          <div className="flex gap-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-medium transition-colors"
            >
              Send
            </button>
          </div>
        </form>
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-gray-500 text-sm">
        <p>Tools: LangChain • Google Gemini API • Whisper AI</p>
      </footer>
    </main>
  );
}
