# Implementation Log

## Phase 1 - Environment Setup

Status: completed

- Confirmed Ubuntu 22.04 development environment.
- Set up FastAPI backend structure.
- Set up React + Vite frontend structure.
- Added SQLite database initialization for MVP storage.

## Phase 2 - Verify eBPF Tools

Status: completed

- Verified BCC tools are installed in the Ubuntu environment.
- Confirmed `execsnoop-bpfcc` works with real process execution events.
- Confirmed `opensnoop-bpfcc` and `tcpconnect-bpfcc` are available for future phases.

## Phase 3 - Process Monitoring Agent

Status: completed

- Added Python `execsnoop_agent.py` for BCC `execsnoop-bpfcc` process exec monitoring.
- Parsed `execsnoop-bpfcc -U` output into process event JSON.
- Sent process events to the existing FastAPI `POST /api/events/process` endpoint.
- Stored process events in SQLite through the existing backend schema.
- Added VSCode Remote background process noise filtering in the agent.
- Added parser and filter sample tests for the process agent.
- Updated the React Dashboard to show recent process events from eBPF.
- Added Process Event Count and client-side search for the latest process events.

## Not Implemented Yet

- WebSocket streaming
- Network eBPF monitoring
- File I/O eBPF monitoring
- PostgreSQL
- Docker deployment
