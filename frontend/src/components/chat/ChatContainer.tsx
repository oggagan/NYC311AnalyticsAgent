import { useEffect, useRef } from "react";
import type { Message, StatusEvent } from "../../types";
import { MessageBubble } from "./MessageBubble";
import { ThinkingIndicator } from "./ThinkingIndicator";

interface ChatContainerProps {
  messages: Message[];
  isLoading: boolean;
  currentStatus: StatusEvent | null;
}

export function ChatContainer({
  messages,
  isLoading,
  currentStatus,
}: ChatContainerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStatus]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isLoading && currentStatus && (
        <ThinkingIndicator status={currentStatus} />
      )}
      <div ref={bottomRef} />
    </div>
  );
}
