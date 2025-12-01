import subprocess

def check_port_usage(port):
    """
    Checks which process is using the given port and provides resolution suggestions.
    """
    try:
        # Run lsof to find process using the port
        result = subprocess.run(
            ["sudo", "lsof", "-i", f":{port}"],
            capture_output=True, text=True
        )

        if not result.stdout.strip():
            return f"""
✅ **Good news!**  
No process is currently using port **{port}**.  
You can safely use this port in your Docker container.
"""
        
        # Extract basic info
        lines = result.stdout.splitlines()
        header = lines[0]
        process_line = lines[1] if len(lines) > 1 else ""
        process_info = f"```\n{result.stdout}\n```"

        # Try to extract process name and PID
        parts = process_line.split()
        if len(parts) >= 2:
            process_name = parts[0]
            pid = parts[1]
        else:
            process_name = "Unknown"
            pid = "N/A"

        # Build suggestion message
        suggestion = ""
        if process_name in ["apache2", "nginx", "httpd"]:
            suggestion = f"🛑 The service **{process_name}** is using port {port}. You can free it by running:\n```bash\nsudo systemctl stop {process_name}\n```"
        else:
            suggestion = f"💀 The process **{process_name} (PID {pid})** is using port {port}. You can stop it using:\n```bash\nsudo kill -9 {pid}\n```"

        return f"""
⚠️ **Port {port} is currently in use, Please stop/kill the service or use another port**

{process_info}

{suggestion}

Alternatively, you can edit your Docker setup to use another port:
```yaml
ports:
  - "8081:{port}"""
   
    except Exception as e:
     return f"❌ Unable to check port Please check manually {port}: {e}"
    
def PortConflict():
    """
    Initial response when user reports a port conflict.
    """
    return """
⚓ **Port Conflict Detected**

It seems a container failed to start because the required port is already in use.

Please provide the port number you'd like me to check (for example: **8080** or **80**).

Just type:
**check port 8080**
and I’ll tell you which process is using it and how to fix it.
"""
