import { create } from "zustand";
import type { Message, ChartConfig, StatusEvent } from "../types";
import { generateId } from "../lib/utils";

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentStatus: StatusEvent | null;
  sessionId: string;

  addUserMessage: (content: string) => string;
  startAssistantMessage: () => string;
  appendToAssistant: (id: string, content: string) => void;
  setAssistantChart: (id: string, chart: ChartConfig) => void;
  setAssistantSql: (id: string, sql: string) => void;
  finalizeAssistant: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setStatus: (status: StatusEvent | null) => void;
  setError: (id: string, error: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  currentStatus: null,
  sessionId: generateId(),

  addUserMessage: (content: string) => {
    const id = generateId();
    set((state) => ({
      messages: [
        ...state.messages,
        { id, role: "user", content, timestamp: new Date() },
      ],
    }));
    return id;
  },

  startAssistantMessage: () => {
    const id = generateId();
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id,
          role: "assistant",
          content: "",
          timestamp: new Date(),
          isStreaming: true,
        },
      ],
    }));
    return id;
  },

  appendToAssistant: (id: string, content: string) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + content } : m
      ),
    }));
  },

  setAssistantChart: (id: string, chart: ChartConfig) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, chart } : m
      ),
    }));
  },

  setAssistantSql: (id: string, sql: string) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, sql_query: sql } : m
      ),
    }));
  },

  finalizeAssistant: (id: string) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, isStreaming: false } : m
      ),
    }));
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setStatus: (status: StatusEvent | null) => {
    set({ currentStatus: status });
  },

  setError: (id: string, error: string) => {
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id
          ? { ...m, content: m.content || `Error: ${error}`, isStreaming: false }
          : m
      ),
    }));
  },
}));
