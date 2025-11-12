import docker
import subprocess
import sys
import time
import streamlit as st
from datetime import datetime
from docker import from_env
from tabulate import tabulate  # ✅ for clean table display

# Initialize Docker client safely
try:
    client = docker.from_env()
except Exception as e:
    client = None
    print(f"⚠️ Docker not available or not running: {e}")

# ================================
# 🔍 Container Info and Health
# ================================
def get_all_containers_info():
    """Return info including name, image, status, and health (if available)."""
    containers_info = []
    for c in client.containers.list(all=True):
        container_data = {
            "name": c.name,
            "id": c.short_id,
            "image": c.image.tags or ["<none>"],
            "status": c.status,
            "health": c.attrs.get("State", {}).get("Health", {}).get("Status", "unknown"),
        }
        try:
            stats = c.stats(stream=False)
            container_data["cpu_percent"] = stats["cpu_stats"]["cpu_usage"]["total_usage"]
            container_data["mem_usage"] = stats["memory_stats"]["usage"]
        except Exception:
            container_data["cpu_percent"] = None
            container_data["mem_usage"] = None
        containers_info.append(container_data)
    return containers_info


def get_container_health_summary():
  """Summarize container health status with distinct icons."""
  containers = get_all_containers_info()  # Your existing function
  health_summary = []

  for c in containers:
        name = c.get("name", "unknown")
        status = c.get("status", "").lower()
        health = c.get("health")

        # If health is None, try fetching from Docker directly
        if health is None:
            try:
                container_obj = client.containers.get(name)
                health = container_obj.attrs.get("State", {}).get("Health", {}).get("Status")
            except docker.errors.NotFound:
                health = "unknown"
            except Exception:
                health = "unknown"

        # Determine icon and health text
        if status == "paused":
            icon = "🟣"
            health_text = "Paused"
        elif health is None:
            icon = "🔵"
            health_text = "Health check not defined"
        elif health.lower() == "healthy":
            icon = "🟢"
            health_text = "healthy"
        elif health.lower() == "starting":
            icon = "🟡"
            health_text = "starting"
        elif health.lower() == "unhealthy":
            icon = "🔴"
            health_text = "unhealthy"
        else:
            icon = "🟠"
            health_text = health or "unknown"

        health_summary.append(f"{icon} {name}: {health_text}")

  return "\n".join(health_summary)


# ================================
# 🐳 Container Summary - Interactive
# ================================

def health_emoji(status):
    """Return emoji for container health status"""
    return {
        "healthy": "🟢",
        "unhealthy": "🔴",
        "starting": "🟠",
        "none": "⚪",
        "unknown": "⚪"
    }.get(status, "⚪")

def list_all_containers():
    """Return list of containers and formatted table"""
    containers = client.containers.list(all=True)
    if not containers:
        return [], "No containers found."
    
    table_data = []
    for c in containers:
        try:
            health_status = getattr(c.attrs, 'State', {}).get('Health', {}).get('Status', 'unknown')
        except Exception:
            health_status = "unknown"
        
        table_data.append([
            c.name,
            c.status,
            (c.image.tags[0] if c.image.tags else "<none>"),
            c.short_id,
            health_emoji(health_status)
        ])
    
    table = tabulate(table_data, headers=["Name", "Status", "Image", "ID", "Health"], tablefmt="fancy_grid")
    return containers, table


# ================================
# ⚙️ Lifecycle Management
# ================================
def manage_container(action, name=None):
    """
    Perform start/stop/restart/pause/resume/remove actions.
    If no name provided, list containers for user selection.
    """
    try:
        containers, table = list_all_containers()

        if not name:
            return (
                f"🧩 Available containers:\n\n{table}\n\n"
                "👉 Please specify the container name or choose one of:\n"
                "`start all stopped`, `stop all running`, `restart all`, `remove all stopped`."
            )

        # Bulk actions
        if name.lower() == "all stopped" and action == "start":
            stopped = [c for c in containers if c.status != "running"]
            for c in stopped:
                c.start()
            return f"🚀 Started {len(stopped)} stopped containers."

        if name.lower() == "all running" and action == "stop":
            running = [c for c in containers if c.status == "running"]
            for c in running:
                c.stop()
            return f"🛑 Stopped {len(running)} running containers."

        if name.lower() == "all" and action in ["restart", "pause", "unpause", "remove"]:
            for c in containers:
                getattr(c, action)()
            return f"🔁 {action.capitalize()}ed all containers."

        # Single container action
        c = client.containers.get(name)
        if action == "start":
            c.start()
        elif action == "stop":
            c.stop()
        elif action == "restart":
            c.restart()
        elif action == "pause":
            c.pause()
        elif action in ["resume", "unpause"]:
            c.unpause()
        elif action in ["remove", "delete"]:
            c.remove(force=True)
        else:
            return f"⚠️ Unsupported action '{action}'."

        return f"✅ Successfully {action}ed '{name}'."

    except docker.errors.NotFound:
        return f"❌ No container found with name '{name}'."
    except Exception as e:
        return f"⚠️ Error managing container: {str(e)}"


# ================================
# 🚀 Container Creation
# ================================
def create_new_container(image=None, name=None, port=None):
    """Create a new container from a public image."""
    try:
        if not image or not name:
            return (
                "🧩 To create a new container, specify:\n"
                "`create container <name> from <image> [on port <port>]`\n\n"
                + show_popular_images()
            )

        existing = client.containers.list(all=True, filters={"name": name})
        if existing:
            return f"⚠️ A container named '{name}' already exists."

        ports = {f"{port}/tcp": port} if port else {}
        client.containers.run(image, name=name, detach=True, ports=ports)
        return f"🚀 New container '{name}' started from image '{image}' on port {port or 'default'}."
    except Exception as e:
        return f"❌ Failed to create container: {str(e)}"


# ================================
# 🧱 Reference Docker Hub Images
# ================================
reference_images = {
    "Web Servers": ["nginx:latest", "httpd:latest", "caddy:latest"],
    "Databases": ["mysql:8.0", "postgres:15", "mongo:7", "redis:7"],
    "Python Environments": [
        "python:3.12-alpine",
        "python:3.10-slim",
        "python:3.9-buster"
    ],
    "Utilities": ["busybox", "alpine", "ubuntu:22.04"]
}

def show_popular_images():
    """Display commonly used public Docker images."""
    return (
        "🧱 **Popular Public Docker Images** from [Docker Hub](https://hub.docker.com/):\n\n"
        "**🐍 Python:** `python:3.12-alpine`, `python:3.10-slim`\n"
        "**🗄 Databases:** `mysql:8.0`, `postgres:15`, `mongo:7`\n"
        "**🌐 Web Servers:** `nginx:latest`, `httpd:latest`\n"
        "**⚙️ Utilities:** `alpine`, `ubuntu:22.04`\n\n"
        "👉 Visit https://hub.docker.com/ to explore more."
    )


# ================================
# 🧠 Diagnostics & Logs
# ================================

def analyze_port_conflict(port):
    """
  #  Checks which process is using the given host port and returns a suggestion.
    """
    try:
        output = subprocess.check_output(f"sudo lsof -i :{port}", shell=True, text=True)
        return f"Port {port} is currently used by:\n```\n{output}\n```\nConsider stopping that process before restarting the container."
    except subprocess.CalledProcessError:
        return f"Port {port} might be in use, but could not detect the process automatically."

def restart_stopped_containers():
    containers = client.containers.list(all=True)
    restarted_names = []
    troubleshooting_info = {}

    for c in containers:
        if c.status != "running":
            try:
                c.restart()
                restarted_names.append(c.name)
            except APIError as e:
                # Detect port conflict from Docker error message
                explanation = str(e.explanation)
                if "address already in use" in explanation.lower() or "failed to bind host port" in explanation.lower():
                    # Extract port number from error string
                    import re
                    match = re.search(r'0\.0\.0\.0:(\d+)', explanation)
                    port = match.group(1) if match else "unknown"
                    explanation += "\n" + analyze_port_conflict(port)
                troubleshooting_info[c.name] = explanation
            except Exception as e:
                troubleshooting_info[c.name] = str(e)
    return restarted_names, troubleshooting_info

def get_container_logs(container_name, tail=20):
    """Fetch the last few lines of logs for a given container."""
    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=tail).decode("utf-8", errors="ignore")
        return logs if logs else f"No logs found for container '{container_name}'."
    except Exception as e:
        return f"Could not fetch logs for {container_name}: {str(e)}"

def show_stopped_containers():
    try:
        stopped = client.containers.list(all=True, filters={"status": "exited"})
        if not stopped:
            return "✅ No stopped containers found."
        
        output = "### 🔴 Stopped Containers\n\n"
        for c in stopped:
            name = c.name
            image = c.image.tags[0] if c.image.tags else "untagged"
            exit_code = c.attrs["State"].get("ExitCode", "N/A")
            finished_at = c.attrs["State"].get("FinishedAt", "unknown")
            output += f"- **{name}** → Image: `{image}`, Exit Code: `{exit_code}`, Last stopped at: `{finished_at}`\n"
        return output
    except Exception as e:
        return f"⚠️ Error fetching stopped containers: {e}"

def smart_start_container(container_name):
    try:
        container = client.containers.get(container_name)
        state = container.attrs["State"]

        if state.get("Paused"):
            container.unpause()
            return f"▶️ `{container_name}` was paused — now unpaused successfully."
        elif state.get("Running"):
            return f"⚠️ `{container_name}` is already running."
        else:
            container.start()
            return f"✅ `{container_name}` started successfully."
    except docker.errors.NotFound:
        return f"❌ Container `{container_name}` not found."
    except docker.errors.APIError as e:
        return f"⚠️ Docker API error: {e.explanation}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"
    
def restart_stopped_containers():
    """
    Restarts all containers in 'exited' state.
    Returns:
        restarted (list): names of containers successfully restarted
        troubleshooting (dict): container_name -> error message if any
    """
    restarted = []
    troubleshooting = {}

    try:
        stopped_containers = client.containers.list(all=True, filters={"status": "exited"})
        for c in stopped_containers:
            try:
                c.start()
                restarted.append(c.name)
            except Exception as e:
                troubleshooting[c.name] = str(e)

    except Exception as e:
        # Global error
        troubleshooting["__global__"] = str(e)

    return restarted, troubleshooting