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
      .post("http://localhost:8000/api/ask", {
        headers: { "Content-Type": "application/json" },
        request: JSON.stringify({ inputValue }),
      })
      .then((response) => {
        console.log(response.data);
        setAnswer(response);
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
        placeHolder="Enter Question to Get Started!"
      ></input>
    </div>
  );
};

export default Home;
