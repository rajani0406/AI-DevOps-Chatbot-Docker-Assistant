# ===============================================
# 📘 Docker Exit Code Reference Module with Commands
# Author: Rajani Sharma
# ===============================================

exit_code_details = {
    0: {
        "title": "Purposely Stopped",
        "description": (
            "Exit Code 0 indicates that the container was intentionally stopped after completing its task."
        ),
        "actions": [
            "Check logs to confirm expected stop behavior.",
            "Validate that no dependent service failed due to the stop."
        ],
        "commands": [
            "docker ps -a --filter 'status=exited'",
            "docker logs <container_name> | tail -20"
        ]
    },
    1: {
        "title": "Application Error",
        "description": (
            "Exit Code 1 means the container stopped due to an application error — for example, a missing dependency or an uncaught exception."
        ),
        "actions": [
            "Inspect container logs for specific application errors.",
            "Ensure correct configuration files and environment variables are provided.",
            "Validate entrypoint script and app dependencies."
        ],
        "commands": [
            "docker logs <container_name>",
            "docker inspect <container_name> --format '{{.State.Error}}'",
            "docker exec -it <container_name> /bin/bash"
        ]
    },
    125: {
        "title": "Container Failed to Run",
        "description": (
            "Exit Code 125 means Docker itself failed to run the container (not the app inside)."
        ),
        "actions": [
            "Check Docker daemon status and system resources.",
            "Validate command syntax and permissions."
        ],
        "commands": [
            "systemctl status docker",
            "journalctl -u docker --no-pager | tail -30",
            "docker run hello-world"
        ]
    },
    126: {
        "title": "Command Invoke Error",
        "description": (
            "Exit Code 126 means a command in the container could not be invoked (permission denied or not executable)."
        ),
        "actions": [
            "Check if the entrypoint script or binary has execute permissions.",
            "Ensure correct user context (root/non-root)."
        ],
        "commands": [
            "docker logs <container_name>",
            "docker exec <container_name> ls -l /usr/local/bin/",
            "chmod +x <file_name> (inside Dockerfile or container)"
        ]
    },
    127: {
        "title": "File or Command Not Found",
        "description": (
            "Exit Code 127 means the container tried to run a file or command that doesn't exist."
        ),
        "actions": [
            "Verify entrypoint or CMD in Dockerfile.",
            "Ensure required binaries or paths exist."
        ],
        "commands": [
            "docker inspect <container_name> --format '{{.Path}} {{.Args}}'",
            "docker exec -it <container_name> which <command>",
            "docker exec -it <container_name> ls /usr/bin/"
        ]
    },
    128: {
        "title": "Invalid Exit Argument",
        "description": (
            "Exit Code 128 occurs when the container process called exit() with an invalid value or signal."
        ),
        "actions": [
            "Check application code for invalid exit() usage.",
            "Ensure signals are handled properly inside the application."
        ],
        "commands": [
            "docker logs <container_name> | grep 'exit'",
            "docker inspect <container_name> --format '{{.State.ExitCode}}'"
        ]
    },
    134: {
        "title": "Abnormal Termination (SIGABRT)",
        "description": (
            "Exit Code 134 means the process aborted due to a detected inconsistency (assert failure or abort())."
        ),
        "actions": [
            "Check logs for 'Aborted' or 'core dumped'.",
            "Inspect application crash reports or core dumps."
        ],
        "commands": [
            "docker logs <container_name> | tail -50",
            "docker exec -it <container_name> dmesg | grep -i abort",
            "ulimit -c unlimited  # enable core dump for debugging"
        ]
    },
    137: {
        "title": "Immediate Termination (SIGKILL)",
        "description": (
            "Exit Code 137 means the container was killed with SIGKILL (often due to OOMKilled or manual docker kill)."
        ),
        "actions": [
            "Check for OOM events using Docker or kernel logs.",
            "Review container memory limits and usage.",
            "Avoid forcing SIGKILL; handle SIGTERM gracefully."
        ],
        "commands": [
            "docker inspect <container_name> --format '{{.State.OOMKilled}}'",
            "docker logs <container_name> | tail -20",
            "dmesg | grep -i kill",
            "docker stats --no-stream"
        ]
    },
    139: {
        "title": "Segmentation Fault (SIGSEGV)",
        "description": (
            "Exit Code 139 means the container crashed due to invalid memory access."
        ),
        "actions": [
            "Rebuild image ensuring correct library versions.",
            "Check code for pointer/memory management bugs.",
            "Run container in debug mode with strace/gdb."
        ],
        "commands": [
            "docker logs <container_name> | tail -40",
            "docker exec -it <container_name> strace -p <pid>",
            "docker exec -it <container_name> gdb <binary>"
        ]
    },
    143: {
        "title": "Graceful Termination (SIGTERM)",
        "description": (
            "Exit Code 143 means the container received SIGTERM (usually via docker stop or orchestrator)."
        ),
        "actions": [
            "Confirm it’s part of a planned shutdown or rolling update.",
            "If unplanned, check orchestrator or host-level stop signals."
        ],
        "commands": [
            "docker ps -a | grep <container_name>",
            "journalctl -u docker | grep -i stop",
            "docker inspect <container_name> --format '{{.State.FinishedAt}}'"
        ]
    },
    255: {
        "title": "Exit Status Out of Range",
        "description": (
            "Exit Code 255 means the process exited with an undefined or out-of-range exit value."
        ),
        "actions": [
            "Rebuild container image cleanly.",
            "Check entrypoint or script for unexpected exits.",
            "Restart Docker daemon if corruption suspected."
        ],
        "commands": [
            "docker logs <container_name> | tail -30",
            "docker ps -a --no-trunc",
            "systemctl restart docker"
        ]
    }
}


def explain_exit_code(code: int) -> str:
    """
    Returns detailed explanation, actions, and troubleshooting commands
    for a given Docker container exit code.
    """
    details = exit_code_details.get(code)
    if not details:
        return (
            f"Exit Code {code} is not recognized.\n\n"
            "Typical patterns:\n"
            "- 0–128 → Application-related errors\n"
            "- 129–255 → OS or signal-based termination (e.g., SIGKILL, SIGTERM)\n\n"
            "🧩 Use: docker ps -a --no-trunc | grep Exited"
        )

    response = f"### Exit Code {code}: {details['title']}\n\n"
    response += f"**🧩 Description:** {details['description']}\n\n"
    response += "#### 🧭 Recommended Actions:\n"
    for step in details["actions"]:
        response += f"- {step}\n"
    response += "\n#### 💻 Troubleshooting Commands:\n"
    for cmd in details["commands"]:
        response += f"`{cmd}`\n\n"
    return response

def handle_exit_code_query(q_lower: str) -> str:
    """
    Extracts an exit code number from the user query and explains it.
    """
    parts = q_lower.split()
    code = None

    for p in parts:
        if p.isdigit():
            code = int(p)
            break

    if code is not None:
        return explain_exit_code(code)
    else:
        return "⚠️ Please provide a valid exit code number, e.g., 'exit code 137'."