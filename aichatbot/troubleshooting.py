import subprocess
import os

def handle_port_conflict():
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
