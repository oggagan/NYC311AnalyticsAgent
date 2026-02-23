import { useCallback } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useChatStore } from "../store/chatStore";
import type { Message, StatusEvent } from "../types";

export function useChat() {
  const store = useChatStore();

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || store.isLoading) return;

      store.addUserMessage(content);
      store.setLoading(true);
      store.setStatus({ step: "connecting", message: "Connecting..." });

      const assistantId = store.startAssistantMessage();

      try {
        await fetchEventSource("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: content,
            session_id: store.sessionId,
          }),
          onmessage(ev) {
            if (!ev.data) return;

            try {
              const data = JSON.parse(ev.data);

              switch (ev.event) {
                case "status":
                  store.setStatus(data as StatusEvent);
                  break;
                case "token":
                  store.appendToAssistant(assistantId, data.content);
                  break;
                case "chart":
                  store.setAssistantChart(assistantId, data);
                  break;
                case "sql":
                  store.setAssistantSql(assistantId, data.query);
                  break;
                case "error":
                  store.setError(assistantId, data.message);
                  break;
                case "done":
                  store.finalizeAssistant(assistantId);
                  store.setLoading(false);
                  store.setStatus(null);
                  break;
              }
            } catch {
              // ignore malformed events
            }
          },
          onerror(err) {
            store.setError(assistantId, "Connection lost. Please try again.");
            store.setLoading(false);
            store.setStatus(null);
            throw err;
          },
          onclose() {
            store.finalizeAssistant(assistantId);
            store.setLoading(false);
            store.setStatus(null);
          },
          openWhenHidden: true,
        });
      } catch {
        store.finalizeAssistant(assistantId);
        store.setLoading(false);
        store.setStatus(null);
      }
    },
    [store]
  );

  return {
    messages: store.messages as Message[],
    isLoading: store.isLoading,
    currentStatus: store.currentStatus,
    sendMessage,
  };
}
