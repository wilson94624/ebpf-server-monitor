export interface SystemMetric {
  id: number;
  host: string;
  cpu_usage: number;
  memory_total: number;
  memory_used: number;
  memory_usage: number;
  load_avg_1: number;
  load_avg_5: number;
  load_avg_15: number;
  created_at: string;
}


export interface ProcessEvent {
  id: number;
  host: string;
  event_type: string;
  pid: number;
  ppid: number;
  uid: number;
  comm: string;
  filename: string | null;
  exit_code: number | null;
  created_at: string;
}

