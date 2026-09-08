import { Bot, User } from "lucide-react";

import type { Message } from "../../types";

export default function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-300">
          <Bot className="h-4 w-4" />
        </div>
      )}
      <div
        className={`max-w-[82%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm leading-relaxed ${
          isUser
            ? "rounded-br-md bg-[var(--color-ai-accent)] text-slate-950"
            : "rounded-bl-md bg-slate-800 text-slate-100 border border-slate-700"
        }`}
      >
        {message.content}
      </div>
      {isUser && (
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-700 text-slate-200">
          <User className="h-4 w-4" />
        </div>
      )}
    </div>
  );
}
