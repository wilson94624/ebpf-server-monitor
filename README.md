# eBPF Server Monitor

這是畢業專題 MVP 的 Phase 1 到 Phase 3 最小可跑版本。

目前先不包含 Docker、WebSocket、PostgreSQL。此版本使用 `psutil_agent.py` 收集 CPU、Memory 與 Load Average，並使用 `execsnoop_agent.py` 讀取 `execsnoop-bpfcc` 的 process events，送到 FastAPI Backend 後在 React Dashboard 顯示。

## 技術

- Backend: FastAPI + SQLite
- Agent: Python psutil agent + execsnoop process agent
- Frontend: React + Vite

## Phase Status

- Phase 1 - Environment Setup: completed
- Phase 2 - Verify eBPF Tools: completed
- Phase 3 - Process Monitoring Agent: completed

Phase 3 completed includes:

- eBPF exec monitoring with BCC `execsnoop-bpfcc`
- Ubuntu agent parses process exec events into JSON
- VSCode Remote background process noise filtering
- FastAPI stores process events in SQLite
- Dashboard and API query recent process events

## 專案結構

```text
ebpf-server-monitor/
├── agent/
│   ├── execsnoop_agent.py
│   ├── psutil_agent.py
│   └── requirements.txt
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── events.py
│   │   │   └── metrics.py
│   │   ├── db/
│   │   │   └── database.py
│   │   ├── schemas/
│   │   │   ├── events.py
│   │   │   └── metrics.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 啟動 Backend

開一個 terminal：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend 啟動後會自動建立 SQLite DB：

```text
backend/monitor.db
```

健康檢查：

```bash
curl http://127.0.0.1:8000/api/health
```

預期回應：

```json
{"status":"ok"}
```

## 啟動 psutil Agent

再開一個 terminal：

```bash
cd agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python psutil_agent.py
```

它會每 3 秒收集並送出一筆真實 system metric：

- `host`
- `cpu_usage`
- `memory_total`
- `memory_used`
- `memory_usage`
- `load_avg_1`
- `load_avg_5`
- `load_avg_15`

如果 backend 不是跑在預設網址，可以指定：

```bash
python psutil_agent.py --backend http://127.0.0.1:8000 --interval 3
```

## 啟動 execsnoop Process Agent

`execsnoop-bpfcc` 需要 root 權限。Backend 啟動後，再開一個 terminal：

```bash
cd agent
source .venv/bin/activate
sudo -E .venv/bin/python execsnoop_agent.py --backend http://127.0.0.1:8000
```

預設會優先執行：

```bash
stdbuf -oL -eL execsnoop-bpfcc -U
```

如果系統沒有 `stdbuf`，會自動退回 `execsnoop-bpfcc -U`。`-U` 讓輸出包含 UID，符合目前 Process Events API 需要的欄位。agent 會從 `execsnoop-bpfcc` 的 header 動態偵測欄位名稱，不依賴固定欄位位置。

如果需要檢查 `execsnoop-bpfcc` 的原始輸出是否有進入 Python agent，可以使用 debug 模式：

```bash
sudo -E .venv/bin/python execsnoop_agent.py --backend http://127.0.0.1:8000 --debug
```

agent 會在送入 Backend 前過濾常見 VSCode Remote 背景事件，例如 `cpuUsage.sh`、`/proc/*/stat`、`sed ... /proc/stat`、`ps -ax -o ...`、`which ps`、`sleep 1`、`/bin/sh -c which ps`、`lesspipe`、`basename`、`dirname`、`dircolors`、`uname`。debug 模式會印出被忽略事件的原因。

如果需要指定不同的 execsnoop 指令：

```bash
sudo -E .venv/bin/python execsnoop_agent.py \
  --backend http://127.0.0.1:8000 \
  --execsnoop-command execsnoop-bpfcc -U
```

## 啟動 Frontend

再開一個 terminal：

```bash
cd frontend
npm install
npm run dev
```

打開：

```text
http://127.0.0.1:5173
```

Dashboard 會顯示：

- CPU Usage
- Memory Usage
- Load Average
- Process Event Count
- Recent CPU Samples
- Recent Process Events from eBPF `execsnoop-bpfcc`
- Process event search by command, PID, or filename

## API

### Health

```http
GET /api/health
```

### System Metrics

```http
POST /api/metrics/system
GET /api/metrics/system?limit=50
```

POST 範例：

```json
{
  "host": "localhost",
  "cpu_usage": 42.5,
  "memory_total": 17179869184,
  "memory_used": 8589934592,
  "memory_usage": 50.0,
  "load_avg_1": 1.2,
  "load_avg_5": 1.1,
  "load_avg_15": 0.9
}
```

### Process Events

```http
POST /api/events/process
GET /api/events/process?limit=50
```

POST 範例：

```json
{
  "host": "localhost",
  "event_type": "exec",
  "pid": 1234,
  "ppid": 1,
  "uid": 501,
  "comm": "curl",
  "filename": "/usr/bin/curl",
  "exit_code": null
}
```

## 開發備註

- SQLite schema 目前在 `backend/app/db/database.py` 中初始化。
- Frontend 目前用 HTTP polling，每 3 秒重新抓一次資料。
- `psutil_agent.py` 只會送 system metrics。
- `execsnoop_agent.py` 會把 `execsnoop-bpfcc` 輸出轉成 Process Events API payload。
- Phase 3 已完成 process exec monitoring；目前尚未加入 WebSocket、Network eBPF、File I/O eBPF、PostgreSQL 或 Docker。
