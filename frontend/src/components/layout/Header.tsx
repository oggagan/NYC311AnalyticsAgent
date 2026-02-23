import { BarChart3, Moon, Sun } from "lucide-react";

interface HeaderProps {
  darkMode: boolean;
  onToggleDark: () => void;
}

export function Header({ darkMode, onToggleDark }: HeaderProps) {
  return (
    <header className="border-b border-border bg-card px-4 py-3 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <div className="bg-primary rounded-lg p-2">
          <BarChart3 className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground leading-tight">
            NYC 311 Analytics
          </h1>
          <p className="text-xs text-muted-foreground">
            AI-Powered Data Analysis
          </p>
        </div>
      </div>
      <button
        onClick={onToggleDark}
        className="p-2 rounded-lg hover:bg-accent transition-colors"
        aria-label="Toggle dark mode"
      >
        {darkMode ? (
          <Sun className="h-5 w-5 text-muted-foreground" />
        ) : (
          <Moon className="h-5 w-5 text-muted-foreground" />
        )}
      </button>
    </header>
  );
}
