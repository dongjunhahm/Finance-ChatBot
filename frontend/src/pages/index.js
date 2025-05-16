"use client";
import Chatbot from "../components/Chatbot";

export default function Home() {
  return (
    <main className="min-h-screen p-4 bg-gray-100">
      <h1 className="text-2xl font-bold mb-6 text-center">Finance Chatbot</h1>
      <Chatbot />
    </main>
  );
}
