import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import showdown from "showdown";
import MarketChart from "../components/marketChart";

const Home = () => {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Ask a financial question to get started!" },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);
  const loadingSteps = [
    ["⢿", "⣻", "⣽"],
    ["⣾", "⣷", "⣯"],
    ["⣟", "⡿", "⣿"],
  ];
  const [loadingIndex, setLoadingIndex] = useState(0);

  const intervalRef = useRef(null);

  useEffect(() => {
    if (isLoading) {
      intervalRef.current = setInterval(() => {
        setLoadingIndex((prevIndex) => (prevIndex + 1) % loadingSteps.length);
      }, 100); //time between each iteration, in milliseconds
    }
    return () => {
      clearInterval(intervalRef.current);
      setLoadingIndex(0);
    };
  }, [isLoading]);

  useEffect(() => {
    const el = chatContainerRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages]);

  function normalizeMarkdown(md) {
    return md
      .replace(/(\* .+)/g, "\n$1") // ensure bullet points are separated
      .replace(/(#+ .+)/g, "\n\n$1\n\n") // ensure headings are separated
      .replace(/\n{2,}/g, "\n\n"); // normalize multiple newlines
  }

  const ask = async () => {
    if (!inputValue.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: inputValue }]);
    const userInput = inputValue;
    setInputValue("");
    setIsLoading(true);

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
      setIsLoading(false);
    } catch (error) {
      console.error("API error:", error);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Something went wrong. Please try again." },
      ]);
      setIsLoading(false);
    }
  };

  const convertToMarkdown = (str) => {
    const converter = new showdown.Converter({
      ghCompatibleHeaderId: true,
      headerLevelStart: 1,
      simplifiedAutoLink: true,
      strikethrough: true,
      tables: true,
      tasklists: true,
    });
    const text = normalizeMarkdown(str);
    const html = converter.makeHtml(text);
    return html; //just in order to make sure that no malicious scripts are present
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
              <div
                className="prose prose-base inline-block bg-gray-100 text-sm p-2 rounded-lg max-w-full"
                dangerouslySetInnerHTML={{
                  __html: convertToMarkdown(msg.text),
                }}
              />
            </div>
          ))}

          {isLoading && (
            <div style={{ textAlign: "left" }} className="pt-3">
              {loadingSteps[loadingIndex]}
            </div>
          )}
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
