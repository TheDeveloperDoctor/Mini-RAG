"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { METHOD_COLORS, METHOD_LABELS } from "@/lib/utils";
import type { QueryResponse } from "@/lib/types";

interface Props {
  history: QueryResponse[];
}

type Point = { query: number; [method: string]: number };

export function LatencyChart({ history }: Props) {
  const data = useMemo<Point[]>(() => {
    return history.map((entry, i) => {
      const point: Point = { query: i + 1 };
      for (const r of entry.results) point[r.method] = Number(r.latency_ms.toFixed(3));
      return point;
    });
  }, [history]);

  const methods = useMemo(() => {
    const set = new Set<string>();
    for (const h of history) for (const r of h.results) set.add(r.method);
    return Array.from(set);
  }, [history]);

  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-medium text-ink-100">Latency (ms) per query</h3>
        <p className="text-xs text-ink-400 mt-0.5">
          Each query adds a point. The crossover where naive collapses gets visible around ~10k+ chunks.
        </p>
      </CardHeader>
      <CardBody className="h-72">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-xs text-ink-500 italic">
            run a query to start the chart
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -12 }}>
              <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
              <XAxis
                dataKey="query"
                stroke="#64748b"
                tick={{ fontSize: 11, fontFamily: "ui-monospace" }}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11, fontFamily: "ui-monospace" }} />
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid #1e293b",
                  borderRadius: 8,
                  fontSize: 12,
                }}
                labelStyle={{ color: "#cbd5e1" }}
              />
              <Legend
                wrapperStyle={{ fontSize: 12 }}
                formatter={(value: string) => METHOD_LABELS[value] ?? value}
              />
              {methods.map((m) => (
                <Line
                  key={m}
                  type="monotone"
                  dataKey={m}
                  stroke={METHOD_COLORS[m] ?? "#94a3b8"}
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  isAnimationActive={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardBody>
    </Card>
  );
}
