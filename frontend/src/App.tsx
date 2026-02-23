import { useState, useEffect } from "react";
import { Header } from "./components/layout/Header";
import { SampleQuestions } from "./components/layout/SampleQuestions";
import { ChatContainer } from "./components/chat/ChatContainer";
import { ChatInput } from "./components/chat/ChatInput";
import { useChat } from "./hooks/useChat";

export default function App() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== "undefined") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches;
    }
    return false;
  });
  const { messages, isLoading, currentStatus, sendMessage } = useChat();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const showWelcome = messages.length === 0 && !isLoading;

  return (
    <div className="flex flex-col h-screen bg-background">
      <Header darkMode={darkMode} onToggleDark={() => setDarkMode((d) => !d)} />
      <main className="flex-1 overflow-hidden flex flex-col max-w-4xl w-full mx-auto">
        {showWelcome ? (
          <div className="flex-1 flex flex-col items-center justify-center px-4 pb-8">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold mb-3 text-foreground">
                NYC 311 Analytics Agent
              </h2>
              <p className="text-muted-foreground text-lg max-w-lg">
                Ask questions about NYC 311 service requests data. I can generate
                statistics, insights, and visualizations.
              </p>
            </div>
            <SampleQuestions onSelect={sendMessage} />
          </div>
        ) : (
          <ChatContainer
            messages={messages}
            isLoading={isLoading}
            currentStatus={currentStatus}
          />
        )}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />
      </main>
    </div>
  );
}
