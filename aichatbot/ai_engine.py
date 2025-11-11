import os
import openai
from docker_ops import get_container_logs, get_all_containers_info
from log_analyzer import analyze_logs
from troubleshooting import handle_port_conflict

# Initialize OpenAI safely
openai.api_key = os.getenv("OPENAI_API_KEY")

LOG_SNIPPET_LENGTH = 400  # last N chars of logs

def interpret_docker_question(question, containers):
    """
    Process user questions about Docker containers.
    Returns a clean response for chatbot UI.
    """

    # --- Fallback mock if OpenAI API is missing ---
    if not openai.api_key:
        return mock_ai_response(question, containers)

    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a DevOps assistant that monitors Docker containers and explains issues clearly."
                },
                {
                    "role": "user",
                    "content": f"User question: {question}\n\nContainer info:\n{containers}"
                },
            ]
        )
        return resp.choices[0].message["content"]

    except Exception as e:
        print(f"⚠️ AI error: {e}")
        return mock_ai_response(question, containers)


def mock_ai_response(question, containers):
    """
    Simulate AI answers without OpenAI API.
    """

    question_lower = question.lower()

    running = []
    stopped = []

    for c in containers:
        status = c.get("status", "").lower()
        name = c.get("name", "unknown")
        image = c.get("image", "unknown")
        if isinstance(image, list):
            image = ", ".join(image)

        if "up" in status or "running" in status:
            running.append(f"{name} ({image})")
        elif "exited" in status or "stopped" in status:
            stopped.append(f"{name} ({image})")

    summary = []
    if running:
        summary.append(f"🟢 Running containers ({len(running)}):\n" + "\n".join(f"• {r}" for r in running))
    if stopped:
        summary.append(f"🔴 Stopped containers ({len(stopped)}):\n" + "\n".join(f"• {s}" for s in stopped))
    if not summary:
        summary.append("No containers found.")

    # --- Handle specific user intents ---
    if "troubleshoot" in question_lower or "troubleshooting" in question_lower:
        return (
         "🛠 **Docker Troubleshooting Guide**\n\n"
        "**1️⃣ Inspect running containers:**\n"
        "```bash\ndocker ps -a  # List all containers with status\n```\n\n"

        "**2️⃣ Access a container shell:**\n"
        "```bash\ndocker exec -it <container_name_or_id> bash\n```\n\n"

        "**3️⃣ Stop and remove all containers (if needed):**\n"
        "```bash\ndocker stop $(docker ps -a -q)\ndocker rm $(docker ps -a -q)\n```\n\n"

        "**4️⃣ Inspect container filesystem or logs:**\n"
        "```bash\ndocker exec -it <container_name_or_id> ls -l /app/app/data/db\ndocker logs <container_name_or_id>\n```\n\n"

        "**5️⃣ Clean up Docker system:**\n"
        "```bash\ndocker system prune -a -v\n```\n\n"

        "**6️⃣ If a container is not starting:**\n"
        "- Check logs with `docker logs <container_name_or_id>`\n"
        "- Check for port conflicts using `sudo lsof -i :<port>`\n"
        "- Ensure volumes and file permissions are correct\n"
        "- Try restarting the container manually\n"
        "- Remove the container and pull a fresh image if issues persist\n\n"

        "**7️⃣ Networking Troubleshooting:**\n"
        "```bash\n"
        "docker network ls                    # List all Docker networks\n"
        "docker network inspect <network>     # Inspect a specific network\n"
        "docker network connect <net> <ctr>   # Reconnect container to a network\n"
        "docker exec -it <ctr> ping 8.8.8.8   # Test connectivity inside container\n"
        "sudo systemctl restart docker        # Restart Docker networking\n"
        "sudo iptables -F && sudo systemctl restart docker  # Reset networking firewall\n"
        "```\n\n"

        "**8️⃣ Volume & Storage Troubleshooting:**\n"
        "```bash\n"
        "docker volume ls                     # List volumes\n"
        "docker volume inspect <volume_name>  # Inspect a specific volume\n"
        "docker volume rm <volume_name>       # Remove unused volume\n"
        "docker run -v /host/path:/container/path <image_name>  # Mount manually\n"
        "ls -l /path/to/volume && chmod -R 755 /path/to/volume  # Fix permissions\n"
        "```\n\n"

        "**9️⃣ Docker Compose Troubleshooting:**\n"
        "```bash\n"
        "docker-compose ps                   # Check service states\n"
        "docker-compose logs -f              # Tail logs for services\n"
        "docker-compose down && docker-compose up -d  # Recreate stack\n"
        "docker-compose config               # Validate YAML configuration\n"
        "```\n\n"

        "**🔟 Kubernetes (K8s) Quick Fixes:**\n"
        "```bash\n"
        "kubectl get pods -A                 # View all pods\n"
        "kubectl describe pod <pod_name>     # Inspect events and errors\n"
        "kubectl logs <pod_name>             # View logs\n"
        "kubectl get svc                     # Check exposed services\n"
        "kubectl rollout restart deploy/<deployment>  # Restart deployments\n"
        "kubectl get events --sort-by=.metadata.creationTimestamp  # Show cluster events\n"
        "```\n\n"

        "📦 **11️⃣ Port Conflict Troubleshooting:**\n"
        "```bash\n"
        "sudo lsof -i :80                    # Check if port 80 is in use\n"
        "sudo fuser -k 80/tcp                # Kill process using port 80\n"
        "```\n\n"

        "📚 **More Useful Resources:**\n"
        "- 🔗 [Essential DevOps Commands You Should Know](https://www.linkedin.com/pulse/essential-devops-commands-you-should-know-examples-your-khajuria-inq7c/?trackingId=jhzzWv0ZGJ9TZjKzer7npQ%3D%3D)\n"
        "- 🧩 [Why /entrypoint.sh Works in mysql:8.0 but Fails in mysql:8](https://www.linkedin.com/pulse/why-entrypointsh-works-mysql80-fails-mysql8-how-i-found-khajuria-cfm9c/?trackingId=M6fG%2F7LwT8mZ87gG1%2BJWYw%3D%3D)\n"
        "- 🚨 [PHP 8.0 Build Failure on Ubuntu 20.04 (Focal)? Here's the Fix](https://www.linkedin.com/pulse/php-80-build-failure-ubuntu-2004-focal-heres-why-how-i-khajuria-ncvrc/?trackingId=C%2F4WgPGJTzjyJOq3yyy5sg%3D%3D)\n"
        "- 🌐 [Docker Build Failing with DNS Errors? Here's the Fix](https://www.linkedin.com/pulse/docker-build-failing-dns-errors-heres-how-i-fixed-ubuntu-khajuria-uyzpc/?trackingId=xw5z16mCGa2I5dEWzHJDlw%3D%3D)\n\n"

        "✅ Follow these steps to resolve most Docker, Compose, and Kubernetes issues effectively."
        )    

    # --- Handle specific questions ---
    if "how many" in question_lower and "container" in question_lower:
        return f"There are {len(running)} running containers and {len(stopped)} stopped containers."

    elif "status" in question_lower or "show" in question_lower:
        return "\n\n".join(summary)

    elif "restart" in question_lower:
        if stopped:
            responses = []
            for s in stopped:
                name = s.split(" ")[0]
                logs = get_container_logs(name)
                troubleshooting = analyze_logs(logs)

                # Port conflict check
                if "address already in use" in logs.lower() or "failed to bind host port" in logs.lower():
                    troubleshooting += (
                        "\n\n⚙️ **Port conflict detected! Attempting to identify process using it...**\n"
                    )
                    handle_port_conflict()

                responses.append(
                    f"🔹 Container: {name}\nLogs snippet:\n```\n{logs[-LOG_SNIPPET_LENGTH:]}\n```\n{troubleshooting}"
                )
            return "🚨 Some stopped containers may require troubleshooting before restart:\n\n" + "\n\n".join(responses)
        else:
            return "All containers are running. No need to restart."

    elif "not accessible" in question_lower or "down" in question_lower:
        if stopped:
            responses = []
            for s in stopped:
                name = s.split(" ")[0]
                logs = get_container_logs(name)
                troubleshooting = analyze_logs(logs)

                # Port conflict auto-check
                if "address already in use" in logs.lower() or "failed to bind host port" in logs.lower():
                    troubleshooting += "\n\n⚙️ Port conflict detected! Checking which service is using it..."
                    handle_port_conflict()

                responses.append(
                    f"📄 **Logs for '{name}':**\n```\n{logs[-LOG_SNIPPET_LENGTH:]}\n```\n{troubleshooting}"
                )
            return "🚨 Issue detected with stopped containers:\n\n" + "\n\n".join(responses)
        else:
            return "All containers appear to be running. Check network configuration or firewall rules."

    elif "log" in question_lower or "error" in question_lower:
        for c in containers:
            name = c.get("name", "").lower()
            if name and name in question_lower:
                logs = get_container_logs(name)
                troubleshooting = analyze_logs(logs)
                return (
                    f"📄 **Logs for '{name}':**\n```\n{logs[-LOG_SNIPPET_LENGTH:]}\n```\n\n{troubleshooting}"
                )
        return "Please specify which container logs you want to see."

    elif "start container" in question_lower or "stop container" in question_lower or "remove container" in question_lower:
        return "✅ I can start, stop, or remove containers if you specify the container name. Example: 'start container webapp'."

    elif "pull image" in question_lower:
        return "✅ I can pull/update container images if you specify the image name. Example: 'pull image nginx:latest'."

    elif "network issue" in question_lower:
        return "⚠️ I can check container logs for network errors, unreachable hosts, or misconfigured ports."

    else:
        return (
            "I can help with the following Docker tasks:\n"
            "• Show container status or counts\n"
            "• Restart stopped containers with troubleshooting\n"
            "• Fetch container logs and analyze errors\n"
            "• Start/stop/remove containers\n"
            "• Pull/update container images\n"
            "• Troubleshoot app accessibility or network issues\n"
            "• Basic Trobleshooting\n"
            "• Basic Docker Commands\n"
            "\nTry asking: 'show status', 'restart stopped', or 'why is my app not accessible'."
            
        )
