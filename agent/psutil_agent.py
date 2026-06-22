import argparse
import socket
from datetime import datetime

import psutil
import requests


def post_json(base_url: str, path: str, payload: dict) -> None:
    response = requests.post(f"{base_url}{path}", json=payload, timeout=5)
    response.raise_for_status()


def collect_system_metric(hostname: str, interval: float) -> dict:
    cpu_usage = psutil.cpu_percent(interval=interval)
    memory = psutil.virtual_memory()
    load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()

    return {
        "host": hostname,
        "cpu_usage": round(cpu_usage, 2),
        "memory_total": memory.total,
        "memory_used": memory.used,
        "memory_usage": round(memory.percent, 2),
        "load_avg_1": round(load_avg_1, 2),
        "load_avg_5": round(load_avg_5, 2),
        "load_avg_15": round(load_avg_15, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="psutil system metrics agent")
    parser.add_argument("--backend", default="http://127.0.0.1:8000")
    parser.add_argument("--interval", type=float, default=3.0)
    args = parser.parse_args()

    hostname = socket.gethostname()
    print(f"psutil agent sending metrics to {args.backend} every {args.interval}s")

    while True:
        metric = collect_system_metric(hostname, args.interval)

        try:
            post_json(args.backend, "/api/metrics/system", metric)
            now = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{now}] sent host={metric['host']} "
                f"cpu={metric['cpu_usage']}% "
                f"mem={metric['memory_usage']}% "
                f"load={metric['load_avg_1']}/{metric['load_avg_5']}/{metric['load_avg_15']}"
            )
        except requests.RequestException as exc:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] failed to send metrics: {exc}")


if __name__ == "__main__":
    main()

