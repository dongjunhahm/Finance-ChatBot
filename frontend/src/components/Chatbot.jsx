import { useState } from "react";
import { useImmer } from "use-immer";
import api from "../pages/api/api";
import ChatMessages from "../components/ChatMessages";
import ChatInput from "../components/ChatInput";

function Chatbot() {
  const [messages, setMessages] = useImmer([]);
  const [newMessage, setNewMessage] = useState("");

  const isLoading = messages.length && messages[messages.length - 1].loading;

  async function submitNewMessage() {
    const trimmedMessage = newMessage.trim();
    if (!trimmedMessage || isLoading) return;

    setMessages((draft) => [
      ...draft,
      { role: "user", content: trimmedMessage },
      { role: "assistant", content: "", loading: true },
    ]);
    setNewMessage("");

    try {
      const { answer } = await api.askQuestion(trimmedMessage);
      setMessages((draft) => {
        draft[draft.length - 1].content = answer;
        draft[draft.length - 1].loading = false;
      });
    } catch (err) {
      console.error(err);
      setMessages((draft) => {
        draft[draft.length - 1].loading = false;
        draft[draft.length - 1].error = true;
      });
    }
  }

  return (
    <div>
      {messages.length === 0 && <div>{/* Welcome message */}</div>}
      <ChatMessages messages={messages} isLoading={isLoading} />
      <ChatInput
        newMessage={newMessage}
        isLoading={isLoading}
        setNewMessage={setNewMessage}
        submitNewMessage={submitNewMessage}
      />
    </div>
  );
}

export default Chatbot;
