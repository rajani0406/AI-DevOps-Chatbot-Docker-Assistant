def analyze_logs(logs: str) -> str:
    if not logs:
        return "No logs available for analysis."

    logs_lower = logs.lower()

    if "entrypoint requires the handler name" in logs_lower:
        return (
            "⚙️ **Troubleshooting Suggestion:**\n"
            "- The error indicates that your Lambda container's entrypoint is misconfigured.\n"
            "- Ensure the container command specifies the handler correctly, e.g., `CMD [\"handler.lambda_handler\"]`.\n"
            "- If you are using Dockerfile, check the last line. Example:\n"
            "  ```dockerfile\n"
            "  ENTRYPOINT [\"/usr/bin/aws-lambda-rie\", \"python3\", \"-m\", \"awslambdaric\", \"lambda_function.lambda_handler\"]\n"
            "  ```\n"
            "- If using `docker run`, ensure you pass the handler name after the image name.\n"
            "- Review your function handler in the AWS Lambda or Docker configuration."
        )

    elif (
        "address already in use" in logs_lower
        or "failed to bind" in logs_lower
        or "port is already allocated" in logs_lower
        or "failed programming external connectivity" in logs_lower
    ):
        return (
            "🌐 **Troubleshooting Suggestion:**\n"
            "- A container failed to start because a port (likely 80 or 443) is already in use.\n"
            "- Run `sudo lsof -i :80` or `sudo lsof -i :443` to find which service is using it.\n"
            "- If you find a local service like Apache or Nginx, stop it using:\n"
            "  ```bash\n"
            "  sudo systemctl stop apache2\n"
            "  sudo systemctl stop nginx\n"
            "  ```\n"
            "- You can also check active Docker containers: `docker ps`.\n"
            "- If another container (like nginx-proxy) is using the port, stop it first: `docker stop <container_id>`.\n"
            "- Alternatively, modify your port mapping in `docker-compose.yml` — for example, change `80:80` to `8080:80`.\n"
            "- Then restart your container using:\n"
            "  ```bash\n"
            "  docker-compose up -d\n"
            "  ```"
        )

    else:
        return "🤖 No specific troubleshooting found. Review logs for details or rerun with `--verbose`."

