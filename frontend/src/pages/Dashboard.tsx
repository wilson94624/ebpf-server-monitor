import { useEffect, useMemo, useState } from "react";
import { Server, RefreshCw } from "lucide-react";

import { getJson } from "../api/client";
import type { ProcessEvent, SystemMetric } from "../api/types";
import { MetricCard } from "../components/MetricCard";
import { ProcessTable } from "../components/ProcessTable";


export function Dashboard() {
  const [metrics, setMetrics] = useState<SystemMetric[]>([]);
  const [processEvents, setProcessEvents] = useState<ProcessEvent[]>([]);
  const [processQuery, setProcessQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("-");

  async function loadData() {
    try {
      const [metricRows, eventRows] = await Promise.all([
        getJson<SystemMetric[]>("/api/metrics/system?limit=20"),
        getJson<ProcessEvent[]>("/api/events/process?limit=10")
      ]);
      setMetrics(metricRows);
      setProcessEvents(eventRows);
      setError(null);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load data");
    }
  }

  useEffect(() => {
    void loadData();
    const timer = window.setInterval(() => void loadData(), 3000);
    return () => window.clearInterval(timer);
  }, []);

  const latest = metrics[0];
  const host = latest?.host ?? processEvents[0]?.host ?? "waiting for data";
  const filteredProcessEvents = useMemo(() => {
    const query = processQuery.trim().toLowerCase();
    if (!query) return processEvents;

    return processEvents.filter((event) => {
      const filename = event.filename ?? "";
      return (
        event.comm.toLowerCase().includes(query) ||
        String(event.pid).includes(query) ||
        filename.toLowerCase().includes(query)
      );
    });
  }, [processEvents, processQuery]);

  const memoryText = useMemo(() => {
    if (!latest) return "-";
    const usedGb = latest.memory_used / 1024 / 1024 / 1024;
    const totalGb = latest.memory_total / 1024 / 1024 / 1024;
    return `${usedGb.toFixed(1)} / ${totalGb.toFixed(0)} GB`;
  }, [latest]);

  return (
    <main>
      <header className="topbar">
        <div>
          <h1>eBPF Server Monitor</h1>
          <p>Phase 3 Process Monitoring Dashboard</p>
        </div>
        <div className="host-pill">
          <Server size={18} />
          <span>{host}</span>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <section className="status-row">
        <MetricCard
          icon="cpu"
          label="CPU Usage"
          value={latest ? `${latest.cpu_usage.toFixed(1)}%` : "-"}
          subtext={`Updated ${lastUpdated}`}
        />
        <MetricCard
          icon="memory"
          label="Memory Usage"
          value={latest ? `${latest.memory_usage.toFixed(1)}%` : "-"}
          subtext={memoryText}
        />
        <MetricCard
          icon="load"
          label="Load Average"
          value={latest ? latest.load_avg_1.toFixed(2) : "-"}
          subtext={
            latest
              ? `5m ${latest.load_avg_5.toFixed(2)} / 15m ${latest.load_avg_15.toFixed(2)}`
              : "Waiting for metrics"
          }
        />
        <MetricCard
          icon="process"
          label="Process Event Count"
          value={String(processEvents.length)}
          subtext="Recent exec events from the latest poll"
        />
      </section>

      <section className="panel compact">
        <div className="panel-header">
          <h2>Recent CPU Samples</h2>
          <span>
            <RefreshCw size={14} /> polling every 3s
          </span>
        </div>
        <div className="bars">
          {metrics.slice(0, 12).reverse().map((metric) => (
            <div className="bar-item" key={metric.id}>
              <div
                className="bar-fill"
                style={{ height: `${Math.max(metric.cpu_usage, 4)}%` }}
                title={`${metric.cpu_usage}%`}
              />
            </div>
          ))}
        </div>
      </section>

      <section className="info-panel">
        Process Events are collected from Linux eBPF through BCC
        execsnoop-bpfcc, parsed by the Ubuntu agent, filtered for VSCode Remote
        background noise, and stored through the FastAPI backend.
      </section>

      <ProcessTable
        events={filteredProcessEvents}
        totalEvents={processEvents.length}
        query={processQuery}
        onQueryChange={setProcessQuery}
      />
    </main>
  );
}
