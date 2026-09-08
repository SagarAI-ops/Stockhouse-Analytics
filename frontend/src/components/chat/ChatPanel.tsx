import { useEffect, useRef, useState, type FormEvent } from "react";
import { Bot, Loader2, Send } from "lucide-react";

import { useChatStore } from "../../store/useChatStore";
import ChatBubble from "./ChatBubble";

export default function ChatPanel() {
  const { isOpen, messages, isLoading, error, sendMessage, setOpen } =
    useChatStore();
  const [draft, setDraft] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, isLoading, isOpen]);

  if (!isOpen) return null;

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text || isLoading) return;
    setDraft("");
    void sendMessage(text);
  };

  return (
    <>
      <button
        type="button"
        aria-label="Close chat overlay"
        className="fixed inset-0 z-40 bg-black/40 md:bg-transparent"
        onClick={() => setOpen(false)}
      />
      <aside
        role="dialog"
        aria-label="AI assistant"
        className="fixed right-0 top-0 z-40 flex h-full w-full max-w-md flex-col border-l border-slate-700 bg-slate-900 shadow-2xl"
      >
        <header className="flex items-center gap-2 border-b border-slate-700 px-4 py-3">
          <Bot className="h-5 w-5 text-[var(--color-ai-accent)]" />
          <div>
            <h2 className="text-sm font-semibold text-white">AI Assistant</h2>
            <p className="text-xs text-slate-400">Ask about stockhouse analytics</p>
          </div>
        </header>

        <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.length === 0 && !isLoading && (
            <p className="rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-sm text-slate-400">
              Try asking about total tonnage, hopper cycle times, or filling
              precision.
            </p>
          )}
          {messages.map((message, index) => (
            <ChatBubble key={`${message.role}-${index}`} message={message} />
          ))}
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin text-[var(--color-ai-accent)]" />
              <div className="flex-1 space-y-2">
                <div className="h-3 w-3/4 animate-pulse rounded bg-slate-700" />
                <div className="h-3 w-1/2 animate-pulse rounded bg-slate-700" />
              </div>
            </div>
          )}
        </div>

        {error && (
          <p className="px-4 pb-2 text-xs text-red-300">{error}</p>
        )}

        <form
          onSubmit={onSubmit}
          className="border-t border-slate-700 p-3 pb-24"
        >
          <div className="flex items-end gap-2">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  onSubmit(e);
                }
              }}
              rows={2}
              placeholder="Ask a question…"
              className="flex-1 resize-none rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none"
            />
            <button
              type="submit"
              disabled={isLoading || !draft.trim()}
              aria-label="Send message"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--color-ai-accent)] text-slate-950 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      </aside>
    </>
  );
}
