import axios from "axios";
import { create } from "zustand";

import { sendChatMessage } from "../api/client";
import type { Message } from "../types";

interface ChatState {
  messages: Message[];
  isOpen: boolean;
  isLoading: boolean;
  error: string | null;
  toggle: () => void;
  setOpen: (open: boolean) => void;
  sendMessage: (content: string) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isOpen: false,
  isLoading: false,
  error: null,
  toggle: () => set((s) => ({ isOpen: !s.isOpen })),
  setOpen: (open) => set({ isOpen: open }),
  sendMessage: async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed || get().isLoading) return;

    const history = get().messages;
    const userMessage: Message = { role: "user", content: trimmed };

    set({
      messages: [...history, userMessage],
      isLoading: true,
      error: null,
      isOpen: true,
    });

    try {
      const reply = await sendChatMessage(trimmed, history);
      set((s) => ({
        messages: [
          ...s.messages,
          { role: "assistant", content: reply.content },
        ],
        isLoading: false,
      }));
    } catch (err: unknown) {
      let detail = "Failed to send message. Is the backend running?";
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const apiDetail = err.response?.data?.detail;
        if (status === 503) {
          detail = "LLM not configured. Set GEMINI_API_KEY in backend/.env.";
        } else if (typeof apiDetail === "string" && apiDetail.trim()) {
          detail = apiDetail;
        } else if (status === 502) {
          detail = "LLM request failed. Check Gemini model/API key.";
        }
      }
      set((s) => ({
        isLoading: false,
        error: detail,
        messages: [
          ...s.messages,
          {
            role: "assistant",
            content: detail,
          },
        ],
      }));
    }
  },
}));
