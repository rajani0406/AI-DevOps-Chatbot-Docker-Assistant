# modules/dns_resolution_error.py


### ✅ Step 2: Add the actual fixer function


import json
import os
import subprocess

def fix_dns_issue():
    """
    Automatically fixes DNS resolution issues in Docker by updating /etc/docker/daemon.json
    and restarting the Docker service.
    """
    daemon_path = "/etc/docker/daemon.json"
    dns_config = {"dns": ["8.8.8.8", "8.8.4.4"]}

    try:
        # Step 1: Backup existing file
        if os.path.exists(daemon_path):
            os.system(f"sudo cp {daemon_path} {daemon_path}.bak")

        # Step 2: Load or create config
        if os.path.exists(daemon_path):
            with open(daemon_path, "r") as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError:
                    config = {}
        else:
            config = {}

        # Step 3: Update DNS section
        config["dns"] = dns_config["dns"]

        # Step 4: Write new file
        with open("/tmp/daemon.json", "w") as f:
            json.dump(config, f, indent=2)
        os.system(f"sudo mv /tmp/daemon.json {daemon_path}")
        os.system(f"sudo chmod 644 {daemon_path}")

        # Step 5: Restart Docker
        subprocess.run(["sudo", "systemctl", "restart", "docker"], check=True)
        return "✅ DNS configuration updated successfully and Docker restarted."

    except Exception as e:
        return f"❌ Failed to update Docker DNS configuration: {e}"


def Dnsissue():
    """
    Handles DNS resolution issues like 'Temporary failure resolving' during Docker builds or pulls.
    """

    return """
 🌐 **Fix for 'Temporary failure resolving' in Docker**

  This issue usually occurs when Docker cannot resolve domain names (DNS failure)
    while building images, pulling images, or installing packages inside containers.

Follow these steps to fix it:

---

 🧰 Step 1: Edit Docker Daemon Configuration
Open Docker’s daemon configuration file (create it if it does not exist):

#```bash
sudo vi /etc/docker/daemon.json
paste the below code

{
  "dns": ["8.8.8.8", "4.4.4.4"]
}
or 

{"dns": ["8.8.8.8", "8.8.4.4"]}

sudo systemctl restart docker

**Alternatively, connecting to a different network (such as another Wi-Fi or mobile hotspot) can also resolve this issue.

📚 For more details, refer to this helpful discussion:

(https://askubuntu.com/questions/769227/ubuntu-16-04-server-updates-temporary-failure-resolving-ro-archive-ubuntu-com?noredirect=1&lq=1
)

(https://askubuntu.com/questions/884604/temporary-failure-resolving-us-archive-ubuntu-com-live-usb-rescue?noredirect=1&lq=1
)

(https://askubuntu.com/questions/91543/apt-get-update-fails-to-fetch-files-temporary-failure-resolving-error
)

(https://askubuntu.com/questions/1385005/errors-while-updating-temporary-faliure-resolving-archive-ubuntu-com?noredirect=1&lq=1
)

If you want I can fix it say: fix dns issue
"""
