import argparse
import os
import queue
import re
import shutil
import socket
import subprocess
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests


EVENT_TYPE_EXEC = "exec"
PROCESS_EVENTS_PATH = "/api/events/process"
USER_COMMANDS_TO_KEEP = {"ls", "whoami", "python3", "curl"}


@dataclass(frozen=True)
class BccToolConfig:
    name: str
    command: list[str]
    event_type: str


class ExecsnoopParser:
    def __init__(self, hostname: str, event_type: str) -> None:
        self.hostname = hostname
        self.event_type = event_type
        self.headers: Optional[list[str]] = None

    def parse_line(self, line: str) -> Optional[dict]:
        text = line.strip()
        if not text:
            return None

        headers = self._parse_header(text)
        if headers:
            self.headers = headers
            print(f"detected execsnoop columns: {', '.join(headers)}", flush=True)
            return None

        if not self.headers:
            return None

        row = self._parse_row(text)
        if not row:
            return None

        return self._build_payload(row)

    def _parse_header(self, text: str) -> Optional[list[str]]:
        tokens = text.split()
        if not tokens or tokens[0].isdigit():
            return None

        headers = [normalize_column_name(token) for token in tokens]

        # eBPF/BCC tool output can vary by version and flags, so detect the
        # header by column names instead of relying on fixed positions.
        has_required_fields = all(
            name in headers for name in ("pid", "ppid", "ret", "args")
        )
        has_command = any(name in headers for name in ("pcomm", "comm", "command"))
        if has_required_fields and has_command:
            return headers
        return None

    def _parse_row(self, text: str) -> Optional[dict]:
        assert self.headers is not None

        parts = split_row_by_headers(text, self.headers)
        if len(parts) != len(self.headers):
            return None
        return dict(zip(self.headers, parts))

    def _build_payload(self, row: dict) -> Optional[dict]:
        pid = get_int(row, "pid")
        ppid = get_int(row, "ppid")
        uid = get_int(row, "uid")
        comm = get_value(row, "pcomm", "comm", "command")
        args = get_value(row, "args", "argv", "filename")
        ret = get_int(row, "ret", "retval", "exit_code")

        if pid is None or ppid is None or uid is None or not comm:
            return None

        return {
            "host": self.hostname,
            "event_type": self.event_type,
            "pid": pid,
            "ppid": ppid,
            "uid": uid,
            "comm": comm,
            "filename": args,
            "exit_code": ret,
        }


def normalize_column_name(value: str) -> str:
    normalized = []
    for char in value.lower():
        normalized.append(char if char.isalnum() else "_")
    return "".join(normalized).strip("_")


def split_row_by_headers(text: str, headers: list[str]) -> list[str]:
    args_index = find_args_column_index(headers)
    tokens = text.split()
    if args_index is None or args_index == len(headers) - 1:
        return text.split(maxsplit=len(headers) - 1)

    before_count = args_index
    after_count = len(headers) - args_index - 1
    if len(tokens) < len(headers):
        return tokens

    before = tokens[:before_count]
    after = tokens[len(tokens) - after_count :]
    args = " ".join(tokens[before_count : len(tokens) - after_count])
    return before + [args] + after


def find_args_column_index(headers: list[str]) -> Optional[int]:
    for index, header in enumerate(headers):
        if header in ("args", "argv", "filename"):
            return index
    return None


def get_value(row: dict, *names: str) -> Optional[str]:
    for name in names:
        value = row.get(name)
        if value:
            return str(value)
    return None


def get_int(row: dict, *names: str) -> Optional[int]:
    value = get_value(row, *names)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def should_ignore_event(payload: dict) -> bool:
    return get_ignore_reason(payload) is not None


def get_ignore_reason(payload: dict) -> Optional[str]:
    comm = str(payload.get("comm") or "").strip()
    filename = str(payload.get("filename") or "").strip()
    comm_lower = comm.lower()
    filename_lower = filename.lower()

    if comm_lower in USER_COMMANDS_TO_KEEP:
        return None

    if comm_lower == "cpuusage.sh" or "cpuusage.sh" in filename_lower:
        return "vscode remote cpuUsage.sh polling"

    if filename == "/usr/bin/sleep 1":
        return "vscode remote sleep polling"

    if comm == "cat" and re.match(r"^/usr/bin/cat /proc/\d+/stat$", filename):
        return "vscode remote /proc stat polling"

    if filename == "/bin/sh -c which ps":
        return "vscode remote ps discovery shell wrapper"

    if filename == "/bin/sh -c /usr/bin/ps -ax -o pid=,ppid=,pcpu=,pmem=,command=":
        return "vscode remote process list shell wrapper"

    if comm == "bash" and ".vscode-server" in filename and "--init-file" in filename:
        return "vscode remote bash init shell"

    if filename == "/usr/bin/lesspipe":
        return "vscode remote shell startup lesspipe"

    if filename == "/usr/bin/basename /usr/bin/lesspipe":
        return "vscode remote shell startup basename lesspipe"

    if filename == "/usr/bin/dirname /usr/bin/lesspipe":
        return "vscode remote shell startup dirname lesspipe"

    if filename == "/usr/bin/dircolors -b":
        return "vscode remote shell startup dircolors"

    if filename == "/usr/bin/uname -s":
        return "vscode remote shell startup uname"

    if filename_lower.startswith("/proc/") and filename_lower.endswith("/stat"):
        return "vscode remote /proc stat polling"

    if comm_lower == "sed" and "/proc/stat" in filename_lower:
        return "vscode remote cpu stat parsing"

    if comm_lower == "ps" and "-ax" in filename_lower and "pcpu" in filename_lower:
        return "vscode remote process list polling"

    if comm_lower == "which" and filename_lower.endswith(" ps"):
        return "vscode remote ps discovery"

    return None


def post_json(base_url: str, path: str, payload: dict) -> None:
    response = requests.post(f"{base_url}{path}", json=payload, timeout=5)
    response.raise_for_status()


def read_bcc_events(
    tool: BccToolConfig,
    parser: ExecsnoopParser,
    event_queue: queue.Queue,
    stop_event: threading.Event,
    debug: bool,
) -> None:
    command = build_line_buffered_command(tool.command)
    print(f"starting {tool.name}: {' '.join(command)}", flush=True)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
    except OSError as exc:
        print(f"failed to start {tool.name}: {exc}", flush=True)
        stop_event.set()
        return

    stderr_thread = threading.Thread(
        target=print_stderr,
        args=(process, stop_event),
        daemon=True,
    )
    stderr_thread.start()

    try:
        assert process.stdout is not None
        for line in process.stdout:
            if stop_event.is_set():
                break

            if debug:
                print(f"raw execsnoop line: {line.rstrip()}", flush=True)

            payload = parser.parse_line(line)
            if payload:
                ignore_reason = get_ignore_reason(payload)
                if ignore_reason:
                    if debug:
                        print(
                            "ignored process event "
                            f"reason={ignore_reason} "
                            f"pid={payload['pid']} "
                            f"comm={payload['comm']} "
                            f"filename={payload.get('filename')}",
                            flush=True,
                        )
                    continue

                event_queue.put(payload)
                print(
                    "queued process event "
                    f"pid={payload['pid']} "
                    f"comm={payload['comm']}",
                    flush=True,
                )
    finally:
        stop_event.set()
        if process.poll() is None:
            process.terminate()
        stderr_thread.join(timeout=1)


def print_stderr(process: subprocess.Popen, stop_event: threading.Event) -> None:
    if process.stderr is None:
        return

    for line in process.stderr:
        if stop_event.is_set():
            break
        text = line.strip()
        if text:
            print(f"execsnoop stderr: {text}", flush=True)


def build_line_buffered_command(command: list[str]) -> list[str]:
    if command and command[0] == "stdbuf":
        return command

    stdbuf_path = shutil.which("stdbuf")
    if not stdbuf_path:
        return command

    return [stdbuf_path, "-oL", "-eL", *command]


def send_events(
    backend: str,
    event_queue: queue.Queue,
    stop_event: threading.Event,
    reader_thread: threading.Thread,
) -> None:
    while reader_thread.is_alive() or not event_queue.empty():
        try:
            payload = event_queue.get(timeout=0.5)
        except queue.Empty:
            if stop_event.is_set() and not reader_thread.is_alive():
                break
            continue

        try:
            post_json(backend, PROCESS_EVENTS_PATH, payload)
            now = datetime.now().strftime("%H:%M:%S")
            print(
                f"[{now}] sent process event "
                f"host={payload['host']} "
                f"pid={payload['pid']} "
                f"comm={payload['comm']}",
                flush=True,
            )
        except requests.RequestException as exc:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] failed to send process event: {exc}", flush=True)
        finally:
            event_queue.task_done()


def main() -> None:
    parser = argparse.ArgumentParser(description="execsnoop process events agent")
    parser.add_argument("--backend", default="http://127.0.0.1:8000")
    parser.add_argument("--queue-size", type=int, default=1000)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--execsnoop-command",
        nargs="+",
        default=["execsnoop-bpfcc", "-U"],
        help="command used to run execsnoop; default: execsnoop-bpfcc -U",
    )
    args = parser.parse_args()

    hostname = socket.gethostname()
    tool = BccToolConfig(
        name="execsnoop",
        command=args.execsnoop_command,
        event_type=EVENT_TYPE_EXEC,
    )
    event_queue: queue.Queue = queue.Queue(maxsize=args.queue_size)
    stop_event = threading.Event()
    parser = ExecsnoopParser(hostname=hostname, event_type=tool.event_type)

    reader_thread = threading.Thread(
        target=read_bcc_events,
        args=(tool, parser, event_queue, stop_event, args.debug),
        daemon=True,
    )

    print(f"execsnoop agent sending process events to {args.backend}", flush=True)
    reader_thread.start()

    try:
        send_events(args.backend, event_queue, stop_event, reader_thread)
    except KeyboardInterrupt:
        print("stopping execsnoop agent", flush=True)
        stop_event.set()
    finally:
        reader_thread.join(timeout=2)


if __name__ == "__main__":
    main()
