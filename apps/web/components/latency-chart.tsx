"use client";

import { useMemo } from "react";
import { Card, CardBody, CardHeader } from "@/components/ui/card";
import { METHOD_COLORS, METHOD_LABELS } from "@/lib/utils";
import type { QueryResponse } from "@/lib/types";

interface Props {
  history: QueryResponse[];
}

type Point = { q: number; values: Record<string, number> };

const W = 1100;
const H = 240;
const PAD_X = 56;
const PAD_Y = 28;

export function LatencyChart({ history }: Props) {
  const { points, methods, max } = useMemo(() => {
    const methodSet = new Set<string>();
    for (const h of history) for (const r of h.results) methodSet.add(r.method);
    const methodList = Array.from(methodSet);

    const pointList: Point[] = history.map((entry, i) => {
      const values: Record<string, number> = {};
      for (const r of entry.results) values[r.method] = Number(r.latency_ms.toFixed(3));
      return { q: i + 1, values };
    });

    let maxV = 1;
    for (const p of pointList) for (const v of Object.values(p.values)) maxV = Math.max(maxV, v);
    return { points: pointList, methods: methodList, max: maxV };
  }, [history]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-baseline gap-2">
          <span className="font-mono text-[10px] tracking-[0.2em] text-mint">03</span>
          <h3 className="text-[15px] font-semibold text-ink-100">Latency over time</h3>
        </div>
        <span className="font-mono text-[10px] tracking-[0.16em] uppercase text-ink-600">
          {points.length} {points.length === 1 ? "query" : "queries"}
        </span>
      </CardHeader>
      <CardBody>
        {points.length === 0 ? (
          <div className="h-60 flex flex-col items-center justify-center gap-2 text-center text-sm">
            <div className="font-mono text-[10px] tracking-[0.2em] text-ink-600 uppercase">
              awaiting input
            </div>
            <div className="text-ink-500 italic">run a query to start the chart</div>
          </div>
        ) : (
          <Oscilloscope points={points} methods={methods} max={max} />
        )}
      </CardBody>
    </Card>
  );
}

function Oscilloscope({
  points,
  methods,
  max,
}: {
  points: Point[];
  methods: string[];
  max: number;
}) {
  const xStep = points.length > 1 ? (W - PAD_X * 2) / (points.length - 1) : 0;
  const x = (i: number) => PAD_X + i * xStep;
  const y = (v: number) => H - PAD_Y - (v / max) * (H - PAD_Y * 2);

  return (
    <div className="overflow-x-auto -mx-2">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full block" style={{ height: H }}>
        <defs>
          {methods.map((m) => {
            const hue = METHOD_COLORS[m] ?? "#A3B0C7";
            return (
              <linearGradient key={m} id={`lc-${m}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={hue} stopOpacity={0.4} />
                <stop offset="100%" stopColor={hue} stopOpacity={0} />
              </linearGradient>
            );
          })}
        </defs>

        {[0, 0.25, 0.5, 0.75, 1].map((t) => (
          <line
            key={t}
            x1={PAD_X}
            x2={W - PAD_X}
            y1={PAD_Y + (H - PAD_Y * 2) * t}
            y2={PAD_Y + (H - PAD_Y * 2) * t}
            stroke="rgba(255,255,255,0.05)"
          />
        ))}

        {[0, 0.5, 1].map((t) => {
          const yy = PAD_Y + (H - PAD_Y * 2) * t;
          const v = max - max * t;
          return (
            <text
              key={t}
              x={PAD_X - 8}
              y={yy + 3}
              textAnchor="end"
              fill="#5A6378"
              fontFamily="var(--font-jetbrains), ui-monospace"
              fontSize={10}
            >
              {v.toFixed(0)}ms
            </text>
          );
        })}

        {methods.map((m) => {
          const hue = METHOD_COLORS[m] ?? "#A3B0C7";
          const seriesPoints = points.filter((p) => m in p.values);
          if (seriesPoints.length === 0) return null;
          const path = seriesPoints
            .map((p) => `${p === seriesPoints[0] ? "M" : "L"} ${x(points.indexOf(p))} ${y(p.values[m])}`)
            .join(" ");
          const last = seriesPoints[seriesPoints.length - 1];
          const first = seriesPoints[0];
          const area = `${path} L ${x(points.indexOf(last))} ${H - PAD_Y} L ${x(points.indexOf(first))} ${H - PAD_Y} Z`;
          return (
            <g key={m}>
              <path d={area} fill={`url(#lc-${m})`} />
              <path d={path} fill="none" stroke={hue} strokeWidth={1.6} />
              {seriesPoints.map((p) => (
                <circle
                  key={p.q}
                  cx={x(points.indexOf(p))}
                  cy={y(p.values[m])}
                  r={2.5}
                  fill={hue}
                />
              ))}
            </g>
          );
        })}

        {points.map((p, i) => (
          <text
            key={p.q}
            x={x(i)}
            y={H - 6}
            textAnchor="middle"
            fill="#5A6378"
            fontFamily="var(--font-jetbrains), ui-monospace"
            fontSize={10}
          >
            Q{p.q}
          </text>
        ))}
      </svg>

      <div className="mx-2 mt-2 flex flex-wrap gap-x-5 gap-y-1.5 font-mono text-[11px]">
        {methods.map((m) => {
          const hue = METHOD_COLORS[m] ?? "#A3B0C7";
          return (
            <span key={m} className="flex items-center gap-2 text-ink-400">
              <span
                className="inline-block w-3 h-[2px]"
                style={{ background: hue, boxShadow: `0 0 8px ${hue}` }}
              />
              {METHOD_LABELS[m] ?? m}
            </span>
          );
        })}
      </div>
    </div>
  );
}
