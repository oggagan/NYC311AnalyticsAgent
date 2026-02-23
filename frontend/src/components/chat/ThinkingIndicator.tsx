import { Loader2 } from "lucide-react";
import type { StatusEvent } from "../../types";

interface ThinkingIndicatorProps {
  status: StatusEvent;
}

const STEP_LABELS: Record<string, string> = {
  connecting: "Connecting...",
  starting: "Processing your question...",
  routing: "Classifying query...",
  schema: "Inspecting data schema...",
  sql_generated: "Generating SQL query...",
  executed: "Executing query...",
  analyzed: "Analyzing results...",
  chart: "Generating visualization...",
};

export function ThinkingIndicator({ status }: ThinkingIndicatorProps) {
  const label = STEP_LABELS[status.step] || status.message;

  return (
    <div className="flex gap-3">
      <div className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-accent">
        <Loader2 className="h-4 w-4 text-primary animate-spin" />
      </div>
      <div className="bg-card border border-border rounded-2xl rounded-tl-md px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">{label}</span>
          <span className="flex gap-1">
            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0ms]" />
            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:150ms]" />
            <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:300ms]" />
          </span>
        </div>
      </div>
    </div>
  );
}
