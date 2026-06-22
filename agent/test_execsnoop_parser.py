from execsnoop_agent import EVENT_TYPE_EXEC, ExecsnoopParser, should_ignore_event


def parse_lines(lines: list[str]) -> list[dict]:
    parser = ExecsnoopParser(hostname="test-host", event_type=EVENT_TYPE_EXEC)
    events = []
    for line in lines:
        event = parser.parse_line(line)
        if event:
            events.append(event)
    return events


def test_execsnoop_u_header_and_data_line() -> None:
    events = parse_lines(
        [
            "UID PCOMM PID PPID RET ARGS",
            "1000 python3 4242 4000 0 /usr/bin/python3 --version",
        ]
    )

    assert events == [
        {
            "host": "test-host",
            "event_type": "exec",
            "pid": 4242,
            "ppid": 4000,
            "uid": 1000,
            "comm": "python3",
            "filename": "/usr/bin/python3 --version",
            "exit_code": 0,
        }
    ]


def test_header_detection_rejects_numeric_first_token() -> None:
    events = parse_lines(
        [
            "1000 UID PCOMM PID PPID RET ARGS",
            "1000 ls 5001 4000 0 /usr/bin/ls -la /tmp",
        ]
    )

    assert events == []


def test_header_detection_is_case_insensitive() -> None:
    events = parse_lines(
        [
            "uid comm pid ppid ret args",
            "1000 whoami 5002 4000 0 /usr/bin/whoami",
        ]
    )

    assert events[0]["uid"] == 1000
    assert events[0]["comm"] == "whoami"
    assert events[0]["pid"] == 5002
    assert events[0]["ppid"] == 4000
    assert events[0]["exit_code"] == 0


def test_args_can_contain_spaces() -> None:
    events = parse_lines(
        [
            "UID PCOMM PID PPID RET ARGS",
            "1000 bash 5003 4000 0 /usr/bin/bash -c echo hello",
        ]
    )

    assert events[0]["filename"] == "/usr/bin/bash -c echo hello"


def test_filter_ignores_vscode_remote_noise() -> None:
    ignored_payloads = [
        {"comm": "cpuUsage.sh", "filename": "/home/user/.vscode-server/bin/cpuUsage.sh"},
        {"comm": "cat", "filename": "/proc/1234/stat"},
        {"comm": "cat", "filename": "/usr/bin/cat /proc/27366/stat"},
        {"comm": "sed", "filename": "sed -n s/^cpu\\s//p /proc/stat"},
        {
            "comm": "ps",
            "filename": "ps -ax -o pid=,ppid=,pcpu=,pmem=,command=",
        },
        {"comm": "which", "filename": "which ps"},
        {"comm": "sleep", "filename": "/usr/bin/sleep 1"},
        {"comm": "sh", "filename": "/bin/sh -c which ps"},
        {
            "comm": "sh",
            "filename": "/bin/sh -c /usr/bin/ps -ax -o pid=,ppid=,pcpu=,pmem=,command=",
        },
        {
            "comm": "bash",
            "filename": "bash --init-file /home/user/.vscode-server/bin/server-env-setup",
        },
        {"comm": "lesspipe", "filename": "/usr/bin/lesspipe"},
        {"comm": "basename", "filename": "/usr/bin/basename /usr/bin/lesspipe"},
        {"comm": "dirname", "filename": "/usr/bin/dirname /usr/bin/lesspipe"},
        {"comm": "dircolors", "filename": "/usr/bin/dircolors -b"},
        {"comm": "uname", "filename": "/usr/bin/uname -s"},
    ]

    for payload in ignored_payloads:
        assert should_ignore_event(payload), payload


def test_filter_keeps_common_user_commands() -> None:
    kept_payloads = [
        {"comm": "ls", "filename": "/usr/bin/ls -la"},
        {"comm": "whoami", "filename": "/usr/bin/whoami"},
        {"comm": "python3", "filename": "/usr/bin/python3 --version"},
        {"comm": "curl", "filename": "/usr/bin/curl http://127.0.0.1:8000/api/health"},
    ]

    for payload in kept_payloads:
        assert not should_ignore_event(payload), payload


def run_sample_tests() -> None:
    test_execsnoop_u_header_and_data_line()
    test_header_detection_rejects_numeric_first_token()
    test_header_detection_is_case_insensitive()
    test_args_can_contain_spaces()
    test_filter_ignores_vscode_remote_noise()
    test_filter_keeps_common_user_commands()
    print("execsnoop parser sample tests passed")


if __name__ == "__main__":
    run_sample_tests()
