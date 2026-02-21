"use client";

import { MessageSquare, Send, Sparkles, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { apiClient } from "../../lib/api-client";
import { AuthStore } from "../../lib/auth-store";
import { useRouter } from "next/navigation";
import { listDatabases, type DatabaseResponse } from "../../lib/api/databases";

type Message = { role: "user" | "assistant"; text: string };

const suggestedQuestions = [
  "List all tables in the public schema",
  "What is the relationship between orders and order_items?",
  "Generate SQL for total revenue by month",
];

export default function ChatPage() {
  const router = useRouter();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [databases, setDatabases] = useState<DatabaseResponse[]>([]);
  const [databaseId, setDatabaseId] = useState<number | "">("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listDatabases()
      .then((res) => {
        setDatabases(res.data);
        if (res.data.length > 0 && databaseId === "") {
          setDatabaseId(res.data[0].id);
        }
      })
      .catch(() => setDatabases([]));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const token = AuthStore.getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);

    try {
      const response = await apiClient.post<{
        conversation_id: string;
        message_id: string;
        response: string;
        intent: string;
        processing_time_ms: number;
        created_at: string;
      }>(
        "/ai/chat",
        {
          message: text,
          database_id: databaseId === "" ? undefined : databaseId,
        },
        token
      );
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: response.response },
      ]);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to get a reply.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Error: ${message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-4xl flex-col">
      <h2 className="mb-6 text-2xl font-semibold text-[var(--color-text)]">
        Chat
      </h2>

      <div className="flex min-h-[480px] flex-col rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] shadow-sm">
        {databases.length > 0 && (
          <div className="flex items-center gap-2 border-b border-[var(--color-border)] px-4 py-2">
            <label className="text-sm font-medium text-[var(--color-text-secondary)]">
              Database:
            </label>
            <select
              value={databaseId}
              onChange={(e) =>
                setDatabaseId(e.target.value === "" ? "" : Number(e.target.value))
              }
              className="rounded border border-[var(--color-border)] bg-[var(--color-bg)] px-2 py-1 text-sm text-[var(--color-text)]"
            >
              <option value="">Select...</option>
              {databases.map((db) => (
                <option key={db.id} value={db.id}>
                  {db.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="flex-1 overflow-auto p-6">
          <div className="flex items-center gap-2 rounded-lg bg-secondary/10 p-3 text-sm text-[var(--color-text-secondary)]">
            <Sparkles className="h-4 w-4 text-secondary" />
            <span>
              Ask about tables, columns, lineage, or request SQL. Replies use your
              synced schema and Gemini.
            </span>
          </div>
          <ul className="mt-4 space-y-6">
            {messages.map((msg, i) => (
              <li
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    msg.role === "user"
                      ? "bg-primary text-white"
                      : "bg-[var(--color-bg-secondary)] text-[var(--color-text)]"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <div className="whitespace-pre-wrap">{msg.text}</div>
                  ) : (
                    msg.text
                  )}
                </div>
              </li>
            ))}
            {loading && (
              <li className="flex justify-start">
                <div className="flex items-center gap-2 rounded-2xl bg-[var(--color-bg-secondary)] px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Thinking…</span>
                </div>
              </li>
            )}
          </ul>
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-[var(--color-border)] px-6 py-3">
          <p className="mb-2 text-xs font-medium text-[var(--color-text-secondary)]">
            Suggested
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setInput(q)}
                className="rounded-full border border-[var(--color-border)] bg-[var(--color-bg)] px-3 py-1.5 text-xs text-[var(--color-text)] hover:bg-[var(--color-bg-secondary)]"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-[var(--color-border)] p-4">
          <div className="flex gap-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-2 focus-within:ring-1 focus-within:ring-primary">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder="Ask about your data..."
              className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-[var(--color-text-secondary)]"
              aria-label="Chat message"
              disabled={loading}
            />
            <button
              type="button"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary text-white hover:opacity-90 disabled:opacity-50"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
