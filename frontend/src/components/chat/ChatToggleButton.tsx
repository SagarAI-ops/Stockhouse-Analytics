import { MessageSquare, X } from "lucide-react";

import { useChatStore } from "../../store/useChatStore";

export default function ChatToggleButton() {
  const isOpen = useChatStore((s) => s.isOpen);
  const toggle = useChatStore((s) => s.toggle);

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={isOpen ? "Close AI assistant" : "Open AI assistant"}
      className={`fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full shadow-lg transition-colors ${
        isOpen
          ? "bg-slate-700 text-white hover:bg-slate-600"
          : "bg-[var(--color-ai-accent)] text-slate-950 hover:brightness-110"
      }`}
    >
      {isOpen ? (
        <X className="h-6 w-6" />
      ) : (
        <MessageSquare className="h-6 w-6" />
      )}
    </button>
  );
}
