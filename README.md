# eBPF Server Monitor

基於 eBPF 的 Linux 主機監控平台。

本專案利用 Linux eBPF 技術收集系統執行資訊，並透過 FastAPI 與 React Dashboard 進行即時監控與視覺化展示。

目前已完成 CPU、記憶體、Load Average 監控，以及基於 eBPF 的 Process Monitoring 功能。

---

# 專案目標

傳統監控工具大多只能看到：

- CPU 使用率
- 記憶體使用率
- 磁碟空間
- 網路流量

但管理 Linux 主機時，往往更需要了解：

- 系統正在執行哪些程式
- 有哪些新程序被啟動
- 主機是否出現異常行為
- 是否存在潛在安全風險

因此本專案希望透過 eBPF 技術建立一套輕量化 Linux 可觀測性（Observability）平台，提供更深入的系統行為分析能力。

---

# 系統架構

```text
Linux Host
    │
    ▼
eBPF (BCC execsnoop)
    │
    ▼
Python Agent
    │
    ▼
FastAPI Backend
    │
    ▼
SQLite Database
    │
    ▼
React Dashboard
```

---

# 已完成功能

## Phase 1：環境建置

- Linux 開發環境建立
- eBPF 工具安裝驗證
- BCC 工具測試
- FastAPI Backend 建立
- React Frontend 建立

---

## Phase 2：系統監控平台

### 主機監控

- CPU Usage
- Memory Usage
- Load Average

### 後端服務

- FastAPI REST API
- SQLite 資料儲存
- Metrics API

### 前端儀表板

- 即時資料更新
- 歷史資料顯示
- Dashboard 視覺化介面

---

## Phase 3：eBPF 程序監控

### eBPF Process Monitoring

透過 BCC 提供的：

```bash
execsnoop-bpfcc
```

監控 Linux 主機上的程序執行事件。

### 已完成內容

- eBPF Process Event 收集
- Ubuntu Agent 事件解析
- VSCode Remote 背景噪音過濾
- Process Event 儲存至 SQLite
- Process Event API
- Dashboard 顯示最近執行事件
- Process Event 搜尋功能

### 範例事件

```text
時間：2026-06-22 20:17:01

PID：57162

Command：
run-parts

Executable：
/usr/bin/run-parts --report /etc/cron.hourly
```

---

# 技術架構

## Backend

- FastAPI
- SQLite
- Pydantic

## Frontend

- React
- TypeScript
- Vite

## Monitoring

- eBPF
- BCC
- execsnoop-bpfcc
- psutil

---

# 專案目前狀態

| 階段 | 狀態 |
|--------|--------|
| Phase 1：環境建置 | ✅ 完成 |
| Phase 2：監控平台 | ✅ 完成 |
| Phase 3：Process Monitoring | ✅ 完成 |
| Phase 4：Network Monitoring | 🚧 規劃中 |
| Phase 5：AI 風險分析 | 🚧 規劃中 |
| Phase 6：本地 LLM 整合 | 🚧 規劃中 |
| Phase 7：XDP 主動防禦 | 🚧 規劃中 |

---

# 未來發展方向

本專案最終目標並非單純監控工具，而是打造：

> 基於 eBPF 與 AI 的 Linux 主機可觀測性與安全分析平台

預計未來加入：

## Network Monitoring

透過 eBPF 收集：

- TCP 連線
- UDP 流量
- 網路行為分析

---

## File Monitoring

監控：

- 檔案建立
- 檔案刪除
- 敏感檔案存取

---

## AI 風險分析

根據系統事件：

- 建立風險評分
- 偵測異常行為
- 分析潛在攻擊

---

## Local LLM 整合

透過本地大型語言模型：

- 解釋系統事件
- 分析異常原因
- 提供管理建議

避免敏感資料上傳至雲端服務。

---

## XDP 主動防禦

當系統偵測到高風險流量時：

- 封鎖來源 IP
- 流量限制
- 即時封包丟棄

實現主動式防禦能力。

---

# 適用對象

- Linux 初學者
- 學校實驗室
- 小型伺服器管理者
- Homelab 使用者
- 資訊安全研究

---

# 專案願景

打造一套：

**輕量化、可擴充、具備 AI 分析能力的 eBPF Linux 監控平台。**

從傳統監控進一步發展為：

**監控（Monitoring） → 分析（Analysis） → 解釋（Explanation） → 防禦（Mitigation）**

的一體化解決方案。
