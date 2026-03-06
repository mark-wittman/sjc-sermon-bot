"use client";

import { useState, useRef, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import { getPreacherColor } from "@/lib/preachers";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import type { ChatMessage, SermonSource } from "@/lib/types";

const SUGGESTED_QUESTIONS = [
  "What does Dean Lawson say about doubt?",
  "How does Broderick Greer approach justice in his preaching?",
  "What role does mystery play in Katie Pearson's sermons?",
  "What does the cathedral's preaching say about suffering?",
];

function SourceCard({ source }: { source: SermonSource }) {
  return (
    <Link
      href={`/sermons/${source.slug}`}
      className="block p-3 bg-cream rounded border border-border hover:border-cathedral-red/30 transition-colors text-sm"
    >
      <p className="font-medium text-ink">{source.title}</p>
      <div className="flex items-center gap-2 mt-1">
        <span
          className="inline-block w-2 h-2 rounded-full"
          style={{ backgroundColor: getPreacherColor(source.preacher) }}
        />
        <span className="text-xs text-ink-muted">
          {source.preacher} &middot; {source.date}
        </span>
      </div>
      {source.excerpt && (
        <p className="mt-2 text-xs text-ink-light line-clamp-2">
          &ldquo;{source.excerpt}&rdquo;
        </p>
      )}
    </Link>
  );
}

function MessageBubble({
  message,
  isStreaming,
}: {
  message: ChatMessage;
  isStreaming: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] sm:max-w-[75%] ${
          isUser
            ? "bg-cathedral-red text-white rounded-2xl rounded-br-sm px-4 py-3"
            : "bg-white border border-border rounded-2xl rounded-bl-sm px-4 py-3"
        }`}
      >
        <div
          className={`text-sm leading-relaxed ${
            isUser ? "whitespace-pre-wrap" : "text-ink-light"
          }`}
        >
          {isUser ? (
            message.content
          ) : message.content ? (
            <ReactMarkdown
              components={{
                h1: ({ children }) => (
                  <h4 className="font-serif text-base font-semibold mt-3 mb-1">
                    {children}
                  </h4>
                ),
                h2: ({ children }) => (
                  <h4 className="font-serif text-sm font-semibold mt-3 mb-1">
                    {children}
                  </h4>
                ),
                h3: ({ children }) => (
                  <h5 className="text-sm font-semibold mt-2 mb-1">
                    {children}
                  </h5>
                ),
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => (
                  <strong className="font-semibold text-ink">{children}</strong>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc pl-4 space-y-1 mb-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-4 space-y-1 mb-2">{children}</ol>
                ),
                li: ({ children }) => (
                  <li className="leading-relaxed">{children}</li>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-cathedral-red/30 pl-3 italic my-2">
                    {children}
                  </blockquote>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : null}
          {isStreaming && message.role === "assistant" && !message.content && (
            <span className="inline-block animate-pulse">Thinking...</span>
          )}
        </div>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="text-xs font-medium text-ink-muted">Sources:</p>
            {message.sources.map((source, i) => (
              <SourceCard key={i} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function ChatInterface() {
  const { messages, isStreaming, sendMessage, clearMessages } = useChat();
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
        <div className="mx-auto max-w-3xl space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <h2 className="font-serif text-2xl font-semibold mb-2">
                Ask about the sermons
              </h2>
              <p className="text-sm text-ink-muted mb-8 max-w-md mx-auto">
                I can answer questions about the preaching of Saint John&apos;s
                Cathedral, grounded in actual sermon transcripts.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg mx-auto">
                {SUGGESTED_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="text-left text-sm px-4 py-3 bg-white rounded-lg border border-border hover:border-cathedral-red/30 hover:shadow-sm transition-all text-ink-light"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble
              key={i}
              message={msg}
              isStreaming={isStreaming && i === messages.length - 1}
            />
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border bg-cream/80 backdrop-blur-sm px-4 sm:px-6 py-4">
        <form
          onSubmit={handleSubmit}
          className="mx-auto max-w-3xl flex items-end gap-2"
        >
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the sermons..."
              disabled={isStreaming}
              className="w-full px-4 py-3 rounded-xl border border-border bg-white text-sm focus:outline-none focus:ring-2 focus:ring-cathedral-red/20 focus:border-cathedral-red disabled:opacity-50 transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={isStreaming || !input.trim()}
            className="px-4 py-3 bg-cathedral-red text-white rounded-xl text-sm font-medium hover:bg-cathedral-red-light disabled:opacity-50 transition-colors shrink-0"
          >
            Send
          </button>
          {messages.length > 0 && (
            <button
              type="button"
              onClick={clearMessages}
              className="px-3 py-3 text-ink-muted hover:text-ink text-sm transition-colors shrink-0"
              title="Clear chat"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </form>
      </div>
    </div>
  );
}
