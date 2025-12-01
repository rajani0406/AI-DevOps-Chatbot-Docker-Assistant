import docker
import time
import re

def troubleshoot_container(container_name: str) -> str:
    """
    Automatically troubleshoots a Docker container:
    - Checks container state and restart behavior
    - Attempts restart if exited/restarting
    - Fetches and analyzes logs
    - Maps exit codes to explanations
    - Returns detailed troubleshooting report
    """

    client = docker.from_env()

    # Find the container
    containers = client.containers.list(all=True)
    container = next((c for c in containers if container_name.lower() in c.name.lower()), None)

    if not container:
        return f"❌ No container found with name similar to '{container_name}'."

    name = container.name
    status = container.status.lower()
    report = [f"🧠 **Troubleshooting Report for `{name}`**", ""]

    # Step 1: Check initial state
    report.append(f"📦 Current Status: `{status}`")

    # Step 2: If container is not running, try to restart it
    if status in ["exited", "dead", "created", "restarting"]:
        try:
            report.append("🔄 Attempting to restart container...")
            container.restart()
            time.sleep(5)
            container.reload()
            new_status = container.status.lower()
            report.append(f"⚙️ New Status after restart: `{new_status}`")

            if new_status == "running":
                report.append("✅ Container restarted successfully and is now running.")
                return "\n".join(report)
            else:
                report.append("⚠️ Container failed to start after restart attempt. Fetching logs...")

        except Exception as e:
            report.append(f"❗ Failed to restart container: {e}")
    else:
        report.append("✅ Container is already running normally.")

    # Step 3: Gather logs (last 30 lines)
    try:
        logs = container.logs(tail=30).decode("utf-8", errors="ignore").strip()
        report.append("\n🪵 **Recent Logs (last 30 lines):**\n```\n" + (logs or "No logs found.") + "\n```")
    except Exception as e:
        logs = ""
        report.append(f"❗ Unable to fetch logs: {e}")

    # Step 4: Exit Code Analysis
    try:
        state = container.attrs.get("State", {})
        exit_code = state.get("ExitCode", None)
        if exit_code is not None:
            report.append(f"\n💀 **Exit Code:** `{exit_code}`")
            explanation = get_exit_code_explanation(exit_code)
            report.append(f"📘 **Meaning:** {explanation}")
    except Exception as e:
        report.append(f"❗ Unable to get exit code: {e}")

    # Step 5: Log Analysis for Common Errors
    issues = []
    if re.search(r"port.*already in use", logs, re.I):
        issues.append("🚪 Port conflict detected — another process might be using this port.")
    if re.search(r"error|fail|crash|exception", logs, re.I):
        issues.append("⚠️ Application crash or configuration error detected.")
    if re.search(r"network|dns|resolve", logs, re.I):
        issues.append("🌐 Network or DNS resolution issue.")
    if re.search(r"permission|denied", logs, re.I):
        issues.append("🔒 Permission issue — file or directory may not be accessible.")
    if not issues:
        issues.append("✅ No critical errors found in logs.")

    report.append("\n🧩 **Detected Issues:**")
    for i in issues:
        report.append(f"- {i}")

    # Step 6: Recommendations
    report.append("\n💡 **Recommendations:**")
    report.append("- Run `docker inspect " + name + "` to check environment, volumes, and entrypoint.")
    report.append("- Verify that dependent services (e.g., DB, API) are reachable.")
    report.append("- Check ports with `sudo lsof -i :<port>` if port conflicts suspected.")
    report.append("- Ensure proper file permissions and volume mounts.")
    report.append("- If issue persists, try `docker rm -f " + name + "` and redeploy a fresh instance.")

    return "\n".join(report)


def get_exit_code_explanation(code: int) -> str:
    """
    Returns human-readable meaning for common Docker container exit codes.
    """

    explanations = {
        0: "✅ **Normal exit** — container completed successfully with no errors.",
        1: "⚠️ **Generic error** — typically an application crash, missing file, or misconfiguration.",
        2: "🧩 **Incorrect usage or missing arguments** — check your command or entrypoint script.",
        126: "🚫 **Permission problem** — the entrypoint or command isn’t executable.",
        127: "❓ **Command not found** — likely missing binary or wrong ENTRYPOINT/CMD in Dockerfile.",
        128: "🔁 **Invalid exit argument** — usually due to a script exiting incorrectly.",
        129: "🛑 **SIGTERM received** — process terminated manually or by Docker stop.",
        130: "🧨 **SIGINT (Ctrl+C)** — container was interrupted manually.",
        137: "💀 **Killed (SIGKILL)** — usually out-of-memory (OOM) or manually killed.",
        139: "🐛 **Segmentation fault (SIGSEGV)** — memory access violation inside container process.",
        143: "🧯 **Graceful stop (SIGTERM)** — container stopped gracefully via `docker stop`.",
        255: "🚨 **Exit status out of range** — application exited unexpectedly with unknown error code."
    }

    return explanations.get(code, f"❔ Unknown exit code `{code}` — check container logs and entrypoint script.")
