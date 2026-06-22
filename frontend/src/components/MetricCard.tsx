import { Activity, Cpu, ListTree, MemoryStick } from "lucide-react";
import type { LucideIcon } from "lucide-react";


const iconMap: Record<string, LucideIcon> = {
  cpu: Cpu,
  memory: MemoryStick,
  load: Activity,
  process: ListTree
};


interface MetricCardProps {
  icon: "cpu" | "memory" | "load" | "process";
  label: string;
  value: string;
  subtext: string;
}


export function MetricCard({ icon, label, value, subtext }: MetricCardProps) {
  const Icon = iconMap[icon];

  return (
    <section className="metric-card">
      <div className="metric-icon" aria-hidden="true">
        <Icon size={20} />
      </div>
      <div>
        <p className="metric-label">{label}</p>
        <strong>{value}</strong>
        <span>{subtext}</span>
      </div>
    </section>
  );
}
