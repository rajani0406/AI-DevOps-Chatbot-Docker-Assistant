import subprocess
import os

def get_troubleshooting():
    print("⚡ Checking which process is using port 80 or 443...\n")

    try:
        result_80 = subprocess.getoutput("sudo lsof -i :80")
        result_443 = subprocess.getoutput("sudo lsof -i :443")

        if result_80:
            print("🔍 Port 80 in use:\n", result_80)
        if result_443:
            print("🔍 Port 443 in use:\n", result_443)

        # Identify Apache or Nginx processes and suggest actions
        if "apache2" in result_80 or "apache2" in result_443:
            print("\n🛑 Apache2 service detected on port 80/443.")
            print("👉 Suggestion: stop it using:\n   sudo systemctl stop apache2")

        if "nginx" in result_80 or "nginx" in result_443:
            print("\n🛑 Nginx service detected on port 80/443.")
            print("👉 Suggestion: stop it using:\n   sudo systemctl stop nginx")

        if not result_80 and not result_443:
            print("✅ No process is currently using ports 80 or 443.")

    except Exception as e:
        print(f"⚠️ Error while checking ports: {e}")
# docker_troubleshoot.py

def get_troubleshooting_guide():
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
        "docker network ls\n"
        "docker network inspect <network>\n"
        "docker network connect <net> <ctr>\n"
        "docker exec -it <ctr> ping 8.8.8.8\n"
        "sudo systemctl restart docker\n"
        "sudo iptables -F && sudo systemctl restart docker\n"
        "```\n\n"
        "**8️⃣ Volume & Storage Troubleshooting:**\n"
        "```bash\n"
        "docker volume ls\n"
        "docker volume inspect <volume_name>\n"
        "docker volume rm <volume_name>\n"
        "docker run -v /host/path:/container/path <image_name>\n"
        "ls -l /path/to/volume && chmod -R 755 /path/to/volume\n"
        "```\n\n"
        "**9️⃣ Docker Compose Troubleshooting:**\n"
        "```bash\n"
        "docker-compose ps\n"
        "docker-compose logs -f\n"
        "docker-compose down && docker-compose up -d\n"
        "docker-compose config\n"
        "```\n\n"
        "**🔟 Kubernetes (K8s) Quick Fixes:**\n"
        "```bash\n"
        "kubectl get pods -A\n"
        "kubectl describe pod <pod_name>\n"
        "kubectl logs <pod_name>\n"
        "kubectl get svc\n"
        "kubectl rollout restart deploy/<deployment>\n"
        "kubectl get events --sort-by=.metadata.creationTimestamp\n"
        "```\n\n"
        "📦 **11️⃣ Port Conflict Troubleshooting:**\n"
        "```bash\n"
        "sudo lsof -i :80\n"
        "sudo fuser -k 80/tcp\n"
        "```\n\n"
        "📚 **More Useful Resources:**\n"
        "- 🔗 [Essential DevOps Commands](https://www.linkedin.com/pulse/essential-devops-commands-you-should-know-examples-your-khajuria-inq7c/)\n"
        "- 🧩 [Why /entrypoint.sh Works in mysql:8.0 but Fails in mysql:8](https://www.linkedin.com/pulse/why-entrypointsh-works-mysql80-fails-mysql8-how-i-found-khajuria-cfm9c/)\n"
        "- 🚨 [PHP 8.0 Build Failure on Ubuntu 20.04](https://www.linkedin.com/pulse/php-80-build-failure-ubuntu-2004-focal-heres-why-how-i-khajuria-ncvrc/)\n"
        "- 🌐 [Docker Build Failing with DNS Errors](https://www.linkedin.com/pulse/docker-build-failing-dns-errors-heres-how-i-fixed-ubuntu-khajuria-uyzpc/)\n\n"
        "✅ Follow these steps to resolve most Docker, Compose, and Kubernetes issues effectively."
    )
