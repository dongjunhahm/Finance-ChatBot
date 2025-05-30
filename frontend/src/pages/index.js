import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import MarketChart from "../components/marketChart";
import Chatbox from "../components/chatbox";

const Home = () => {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Ask a financial question to get started." },
  ]);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    const el = chatContainerRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages]);

  const ask = async () => {
    if (!inputValue.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: inputValue }]);
    const userInput = inputValue;
    setInputValue("");

    try {
      const response = await axios.post(
        "http://localhost:8000/api/ask",
        { question: userInput },
        { headers: { "Content-Type": "application/json" } }
      );
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: response.data.answer },
      ]);
    } catch (error) {
      console.error("API error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Something went wrong. Please try again." },
      ]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      ask();
    }
  };

  return (
    <>
      {/* Navbar header */}
      <div className="navbar bg-base-100 shadow-sm">
        <a className="btn btn-ghost text-xl">MarketBuddy</a>
      </div>

      {/* Main layout */}
      <main className="h-[calc(100vh-4rem)] grid grid-cols-[2fr_1fr] grid-rows-[1fr_auto] gap-4 px-4 py-6 max-w-7xl mx-auto">
        {/* Chat History on the left */}
        <div
          ref={chatContainerRef}
          style={{ maxHeight: "100%", paddingRight: "0.5rem" }}
          className="overflow-y-auto max-h-full"
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{ textAlign: msg.sender === "user" ? "right" : "left" }}
              className="pt-3"
            >
              <span className="prose inline-block bg-gray-100 text-sm p-2 rounded-lg max-w-full break-words">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.text}
                </ReactMarkdown>
              </span>
            </div>
          ))}
        </div>

        {/* Market Chart on the right */}
        <div className="border-l border-gray-300 flex justify-center items-center pl-4">
          <MarketChart />
        </div>

        {/* Input bar spans both columns */}
        <div className="col-span-2 w-full bg-white border-t border-gray-200 px-4 py-3 max-w-7xl mx-auto">
          <div className="flex gap-2 max-w-3xl mx-auto">
            <input
              className="flex-1 border border-gray-300 rounded-md p-2 text-sm"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Enter your question..."
            />
          </div>
        </div>
      </main>
    </>
  );
};

export default Home;
