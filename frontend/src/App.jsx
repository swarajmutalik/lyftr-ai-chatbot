
import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  const [sessionId] = useState(
    () => `s-${crypto.randomUUID()}`
  );

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages, loading]);

  async function sendMessage(event) {
    event.preventDefault();

    const message = input.trim();

    if (!message || loading) return;

    setInput("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message
      }
    ]);

    try {
      const payload = {
        session_id: sessionId,
        message
      };

      if (systemPrompt.trim()) {
        payload.system_prompt = systemPrompt.trim();
      }

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        }
      );

      const data = await response.json();

      if (!response.ok) {
        let detail = data.detail;

        if (Array.isArray(detail)) {
          detail = detail
            .map((item) => item.msg)
            .join(", ");
        }

        throw new Error(
          typeof detail === "string"
            ? detail
            : "Unable to process your request."
        );
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.reply,
          metadata: data.metadata
        }
      ]);

    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          role: "error",
          content: error.message
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>LYFTR AI Chatbot</h1>
          <p>Resilient AI conversations</p>
        </div>

        <span className="status">
          AI Assistant
        </span>
      </header>

      <main className="chat-container">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>How can I help you today?</h2>
            <p>
              Ask a question to start a conversation.
            </p>
          </div>
        )}

        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
              data-testid={
                message.role === "assistant"
                  ? "assistant-message"
                  : undefined
              }
            >
              <div className="message-content">
                {message.content}
              </div>

              {message.role === "assistant" &&
                message.metadata && (
                  <div className="metadata">
                    <span data-testid="meta-source">
                      {message.metadata.resolution_source}
                    </span>

                    <span data-testid="meta-model">
                      {message.metadata.model}
                    </span>

                    <span data-testid="meta-latency">
                      {message.metadata.latency_ms} ms
                    </span>

                    <span>
                      Input:
                      {" "}
                      <span data-testid="meta-input-tokens">
                        {message.metadata.input_tokens}
                      </span>
                    </span>

                    <span>
                      Output:
                      {" "}
                      <span data-testid="meta-output-tokens">
                        {message.metadata.output_tokens}
                      </span>
                    </span>
                  </div>
                )}
            </div>
          ))}

          {loading && (
            <div className="message assistant">
              Thinking...
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      <div className="composer">
        <form onSubmit={sendMessage}>
          <textarea
            data-testid="system-prompt-input"
            className="system-prompt"
            placeholder="Optional system prompt"
            value={systemPrompt}
            onChange={(event) =>
              setSystemPrompt(event.target.value)
            }
            rows={2}
          />

          <div className="input-row">
            <textarea
              data-testid="chat-input"
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              placeholder="Type your message..."
              maxLength={4000}
              rows={2}
            />

            <button
              data-testid="send-button"
              type="submit"
              disabled={loading || !input.trim()}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;
