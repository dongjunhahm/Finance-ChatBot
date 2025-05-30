import { useState } from "react";
import axios from "axios";
import Chatbox from "../components/chatbox";

const Home = () => {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Ask a financial question to get started." },
  ]);

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
    <div>
      <div>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{ textAlign: msg.sender === "user" ? "right" : "left" }}
          >
            <span>{msg.text}</span>
          </div>
        ))}
      </div>

      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyPress}
        placeholder="Enter your question..."
      />
    </div>
  );
};

export default Home;
