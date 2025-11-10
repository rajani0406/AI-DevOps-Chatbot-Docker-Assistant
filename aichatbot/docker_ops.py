import docker
from datetime import datetime

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


def restart_stopped_containers():
    containers = client.containers.list(all=True)
    restarted = []
    for c in containers:
        if c.status != "running":
            try:
                c.restart()
                restarted.append(c.name)
            except Exception as e:
                restarted.append(f"{c.name} (failed: {str(e)})")
    return restarted

