import { Layers } from "lucide-react";
import type { SimilarIncident } from "@/types/incident";
import { IncidentCard } from "./IncidentCard";

export interface IncidentsPanelProps {
  incidents: SimilarIncident[];
}

export function IncidentsPanel({ incidents }: IncidentsPanelProps) {
  if (!incidents || incidents.length === 0) return null;

  const avgScore = (
    incidents.reduce((sum, inc) => sum + inc.similarity_score, 0) / incidents.length
  ).toFixed(2);

  return (
    <div
      className="mt-4 overflow-hidden rounded-2xl"
      style={{
        background:  "hsl(var(--rl-ink-950))",
        border:      "1px solid hsl(var(--rl-ink-800))",
      }}
    >
      {/* Panel header */}
      <div
        className="flex items-center justify-between px-4 py-3"
        style={{
          background:   "hsl(var(--rl-purple-950) / 0.4)",
          borderBottom: "1px solid hsl(var(--rl-ink-800))",
        }}
      >
        <div className="flex items-center gap-2.5">
          <div
            className="flex h-6 w-6 items-center justify-center rounded-md"
            style={{ background: "hsl(var(--rl-gold-400) / 0.12)" }}
          >
            <Layers size={12} strokeWidth={2} style={{ color: "hsl(var(--rl-gold-400))" }} />
          </div>
          <p
            className="text-[11px] font-semibold uppercase tracking-[0.1em]"
            style={{ color: "hsl(var(--rl-ink-400))" }}
          >
            Similar Incidents
          </p>
          <span
            className="rounded-md px-2 py-0.5 text-[10px] font-semibold"
            style={{
              background: "hsl(var(--rl-gold-400) / 0.12)",
              color:      "hsl(var(--rl-gold-400))",
            }}
          >
            {incidents.length}
          </span>
        </div>
        <p
          className="text-[11px]"
          style={{ color: "hsl(var(--rl-ink-500))" }}
        >
          Avg match{" "}
          <span
            className="font-semibold"
            style={{ color: "hsl(var(--rl-gold-400))" }}
          >
            {Math.round(parseFloat(avgScore) * 100)}%
          </span>
        </p>
      </div>

      {/* Cards */}
      <div className="space-y-2 p-3">
        {incidents.map((incident, index) => (
          <IncidentCard
            key={`${incident.incident_number}-${index}`}
            incident={incident}
          />
        ))}
      </div>
    </div>
  );
}