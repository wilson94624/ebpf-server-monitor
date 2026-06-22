---
title: eBPF Server Monitor - Development Environment

---

# eBPF Server Monitor - Development Environment

## Project Overview

Graduation Project

Goal:
Build a Linux observability platform using eBPF.

The system monitors:

* Process Events
* Network Events
* File I/O Events
* System Metrics

and visualizes them through a web dashboard.

---

## Architecture

Ubuntu Server
↓
eBPF / BCC Tools
↓
Python Agent
↓
FastAPI Backend
↓
React Frontend

---

## Tech Stack

### Kernel Monitoring

* eBPF
* BCC Tools

Current tools:

* execsnoop-bpfcc
* opensnoop-bpfcc
* tcpconnect-bpfcc

Future:

* tcptracer-bpfcc
* biosnoop-bpfcc
* custom eBPF programs

---

## Backend

Framework:

* FastAPI

Language:

* Python 3.10

Default API:

http://127.0.0.1:8000

---

## Frontend

Framework:

* React

Future UI:

* Process Monitor
* Network Monitor
* File Activity
* Dashboard
* Event Timeline

---

## Development Environment

Operating System:

Ubuntu 22.04

User:

liu1221

Python:

3.10.12

Verified Commands:

sudo execsnoop-bpfcc
sudo opensnoop-bpfcc
sudo tcpconnect-bpfcc

VSCode:

Remote SSH

Development Machine:

MacBook Pro

Editor:

VSCode

---

## Verified eBPF Status

execsnoop-bpfcc has been successfully tested.

Observed process events:

* ls
* whoami
* python3 --version

eBPF environment is working correctly.

---

## Current Development Phase

Phase 1:
Environment Setup
✅ Completed

Phase 2:
Verify eBPF Tools
✅ Completed

Phase 3:
Process Monitoring Agent
🚧 In Progress

Tasks:

* Parse execsnoop output
* Convert to JSON
* Send to FastAPI backend
* Store process events
* Display in frontend

---

## Coding Rules

1. Prefer simple and maintainable code.

2. Do not introduce unnecessary abstractions.

3. MVP first, optimization later.

4. Use existing BCC tools before writing custom eBPF code.

5. Keep compatibility with Ubuntu 22.04.

6. Avoid breaking existing APIs.

7. Add comments for all eBPF-related code.

8. Update README when adding major features.

---

## AI Agent Instructions

Before making changes:

1. Read DEVELOPMENT.md
2. Understand current architecture
3. Verify project structure
4. Check existing API routes
5. Avoid duplicate implementations

When implementing features:

1. Prefer incremental changes
2. Keep commits small
3. Explain design decisions
4. Provide testing instructions
5. Do not remove existing functionality unless requested
