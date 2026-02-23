export interface ChartConfig {
  chart_type: "bar" | "pie" | "line" | "scatter";
  title: string;
  data: Record<string, unknown>[];
  x_key: string;
  y_key: string | string[];
  x_label?: string;
  y_label?: string;
  colors?: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  chart?: ChartConfig;
  sql_query?: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface StatusEvent {
  step: string;
  message: string;
}

export type SSEEventType = "status" | "token" | "chart" | "sql" | "done" | "error";

export interface SSEEvent {
  event: SSEEventType;
  data: string;
}
