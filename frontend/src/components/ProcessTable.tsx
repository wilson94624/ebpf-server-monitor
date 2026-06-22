import type { ProcessEvent } from "../api/types";


interface ProcessTableProps {
  events: ProcessEvent[];
  totalEvents: number;
  query: string;
  onQueryChange: (value: string) => void;
}


export function ProcessTable({
  events,
  totalEvents,
  query,
  onQueryChange
}: ProcessTableProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Recent Process Events</h2>
          <p>Latest 10 exec events from eBPF execsnoop-bpfcc</p>
        </div>
        <span>
          {events.length} of {totalEvents} rows
        </span>
      </div>
      <div className="table-tools">
        <input
          aria-label="Search process events"
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search comm, pid, or filename"
        />
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Host</th>
              <th>Event</th>
              <th>PID</th>
              <th>PPID</th>
              <th>UID</th>
              <th>Command</th>
              <th>Executable</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={event.id}>
                <td>{formatTime(event.created_at)}</td>
                <td>{event.host}</td>
                <td>
                  <span className="badge">{event.event_type}</span>
                </td>
                <td>{event.pid}</td>
                <td>{event.ppid}</td>
                <td>{event.uid}</td>
                <td>{event.comm}</td>
                <td className="mono">{event.filename ?? "-"}</td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr>
                <td colSpan={8} className="empty">
                  No matching process events in the latest eBPF execsnoop sample.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}


function formatTime(value: string) {
  return new Date(`${value}Z`).toLocaleTimeString();
}
