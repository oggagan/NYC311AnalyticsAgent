import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { ChartConfig } from "../../types";

const DEFAULT_COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#ec4899",
  "#f43f5e",
  "#f97316",
  "#eab308",
  "#22c55e",
  "#14b8a6",
  "#06b6d4",
  "#3b82f6",
];

interface ChartRendererProps {
  config: ChartConfig;
}

function truncateLabel(label: string, maxLen = 20): string {
  if (!label) return "";
  const s = String(label);
  return s.length > maxLen ? s.slice(0, maxLen) + "..." : s;
}

export function ChartRenderer({ config }: ChartRendererProps) {
  const { chart_type, title, data, x_key, y_key, x_label, y_label, colors } =
    config;
  const palette = colors?.length ? colors : DEFAULT_COLORS;
  const yKeys = Array.isArray(y_key) ? y_key : [y_key];

  if (!data || data.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground text-sm">
        No data available for chart
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      {title && (
        <h3 className="text-sm font-semibold text-foreground mb-4 text-center">
          {title}
        </h3>
      )}
      <ResponsiveContainer width="100%" height={350}>
        {chart_type === "bar" ? (
          <BarChart data={data} margin={{ top: 5, right: 20, bottom: 60, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis
              dataKey={x_key}
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => truncateLabel(v, 15)}
              angle={-35}
              textAnchor="end"
              label={x_label ? { value: x_label, position: "bottom", offset: 45, fontSize: 12 } : undefined}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={y_label ? { value: y_label, angle: -90, position: "insideLeft", fontSize: 12 } : undefined}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            {yKeys.length > 1 && <Legend />}
            {yKeys.map((yk, i) => (
              <Bar
                key={yk}
                dataKey={yk}
                fill={palette[i % palette.length]}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        ) : chart_type === "pie" ? (
          <PieChart>
            <Pie
              data={data}
              dataKey={yKeys[0]}
              nameKey={x_key}
              cx="50%"
              cy="50%"
              outerRadius={120}
              innerRadius={50}
              paddingAngle={2}
              label={({ name, percent }) =>
                `${truncateLabel(String(name), 12)} ${(percent * 100).toFixed(1)}%`
              }
              labelLine={{ strokeWidth: 1 }}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={palette[i % palette.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Legend />
          </PieChart>
        ) : chart_type === "line" ? (
          <LineChart data={data} margin={{ top: 5, right: 20, bottom: 60, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis
              dataKey={x_key}
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => truncateLabel(v, 12)}
              angle={-35}
              textAnchor="end"
              label={x_label ? { value: x_label, position: "bottom", offset: 45, fontSize: 12 } : undefined}
            />
            <YAxis
              tick={{ fontSize: 11 }}
              label={y_label ? { value: y_label, angle: -90, position: "insideLeft", fontSize: 12 } : undefined}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            {yKeys.length > 1 && <Legend />}
            {yKeys.map((yk, i) => (
              <Line
                key={yk}
                type="monotone"
                dataKey={yk}
                stroke={palette[i % palette.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            ))}
          </LineChart>
        ) : chart_type === "scatter" ? (
          <ScatterChart margin={{ top: 5, right: 20, bottom: 60, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis
              dataKey={x_key}
              type="number"
              tick={{ fontSize: 11 }}
              label={x_label ? { value: x_label, position: "bottom", offset: 45, fontSize: 12 } : undefined}
            />
            <YAxis
              dataKey={yKeys[0]}
              type="number"
              tick={{ fontSize: 11 }}
              label={y_label ? { value: y_label, angle: -90, position: "insideLeft", fontSize: 12 } : undefined}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Scatter data={data} fill={palette[0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={palette[i % palette.length]} />
              ))}
            </Scatter>
          </ScatterChart>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            Unsupported chart type: {chart_type}
          </div>
        )}
      </ResponsiveContainer>
    </div>
  );
}
