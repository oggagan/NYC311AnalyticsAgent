import { MessageSquare } from "lucide-react";

const SAMPLES = [
  "What are the top 10 complaint types by number of records?",
  "For the top 5 complaint types, what percent were closed within 3 days?",
  "Which ZIP code has the highest number of complaints?",
  "What proportion of complaints include a valid latitude/longitude?",
  "Show me monthly complaint trends over time",
  "Compare complaint counts across boroughs",
];

interface SampleQuestionsProps {
  onSelect: (question: string) => void;
}

export function SampleQuestions({ onSelect }: SampleQuestionsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
      {SAMPLES.map((q) => (
        <button
          key={q}
          onClick={() => onSelect(q)}
          className="text-left p-4 rounded-xl border border-border bg-card hover:bg-accent
                     transition-colors group flex items-start gap-3"
        >
          <MessageSquare className="h-4 w-4 mt-0.5 text-primary shrink-0 opacity-60 group-hover:opacity-100 transition-opacity" />
          <span className="text-sm text-foreground leading-snug">{q}</span>
        </button>
      ))}
    </div>
  );
}
