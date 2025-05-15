"use client";
import axios from "axios";
import { useState, useEffect } from "react";

const Home = () => {
  const [inputValue, setInputValue] = useState("");
  const [answer, setAnswer] = useState("");

  const handleInput = (e) => {
    setInputValue(e.target.value);
  };

  const ask = async () => {
    axios
      .post(
        "http://localhost:8000/api/ask",
        { question: inputValue },
        {
          headers: { "Content-Type": "application/json" },
        }
      )
      .then((response) => {
        console.log(response.data);
        setAnswer(response.data.answer);
      });
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      ask();
    }
  };

  return (
    <div>
      <button>hi world</button>
      <input
        type="text"
        value={inputValue}
        onChange={handleInput}
        onKeyDown={handleKeyPress}
        placeholder="Enter Question to Get Started!"
      ></input>

      <p>{answer}</p>
    </div>
  );
};

export default Home;
