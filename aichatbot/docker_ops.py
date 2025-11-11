import docker
import subprocess
import sys
import time
from datetime import datetime
from troubleshooting import handle_port_conflict

client = docker.from_env()

def get_all_containers_info():
    containers = client.containers.list(all=True)
    info = []
    for c in containers:
        started_at = c.attrs.get("State", {}).get("StartedAt", "")
        status = c.status
        started_time = ""
        if started_at:
            try:
                started_time = datetime.fromisoformat(started_at.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                started_time = started_at
        info.append({
            "name": c.name,
            "id": c.short_id,
            "image": c.image.tags,
            "status": status,
            "created": c.attrs["Created"],
            "started": started_time
        })
    return info

def get_port_conflicts():
    conflicts = {}
    try:
        result_80 = subprocess.getoutput("sudo lsof -i :80")
        result_443 = subprocess.getoutput("sudo lsof -i :443")

        if result_80:
            conflicts[80] = {"processes": result_80, "suggestion": None}
            if "apache2" in result_80:
                conflicts[80]["suggestion"] = "sudo systemctl stop apache2"
            elif "nginx" in result_80:
                conflicts[80]["suggestion"] = "sudo systemctl stop nginx"

        if result_443:
            conflicts[443] = {"processes": result_443, "suggestion": None}
            if "apache2" in result_443:
                conflicts[443]["suggestion"] = "sudo systemctl stop apache2"
            elif "nginx" in result_443:
                conflicts[443]["suggestion"] = "sudo systemctl stop nginx"

    except Exception as e:
        conflicts['error'] = str(e)

    return conflicts

def analyze_error(error_msg):
    """
    Returns troubleshooting steps if error indicates networking/port conflict.
    """
    if "failed to set up container networking" in error_msg.lower() or \
       "address already in use" in error_msg.lower():
        troubleshooting = "💡 Docker restart failed due to port conflict.\n"
        conflicts = get_port_conflicts()
        for port, detail in conflicts.items():
            troubleshooting += f"\nPort {port}:\n{detail}\n"
        troubleshooting += "\n👉 Suggestion: Stop conflicting services manually (e.g., apache2/nginx) before retrying."
        return troubleshooting
    return None

def restart_stopped_containers():
    containers = client.containers.list(all=True)
    restarted_names = []
    troubleshooting_info = {}

    for c in containers:
        if c.status != "running":
            try:
                c.restart()
                restarted_names.append(c.name)
            except Exception as e:
                restarted_names.append(c.name)
                steps = analyze_error(str(e))
                troubleshooting_info[c.name] = steps

    return restarted_names, troubleshooting_info

def get_container_logs(container_name, tail=20):
    """
    Fetch the last few lines of logs for a given container.
    Returns a string with the logs or an error message.
    """
    try:
        container = client.containers.get(container_name)
        logs = container.logs(tail=tail).decode("utf-8", errors="ignore")
        return logs if logs else f"No logs found for container '{container_name}'."
    except Exception as e:
        return f"Could not fetch logs for {container_name}: {str(e)}"

