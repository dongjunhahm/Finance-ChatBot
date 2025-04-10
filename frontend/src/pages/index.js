"use client";
import axios from "axios";
import { useState, useEffect } from "react";

const Home = () => {
  const [inputValue, setInputValue] = useState("");

  const handleInput = (e) => {
    setInputValue(e.target.value);
  };

  const handleSubmit = () => {};

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
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
