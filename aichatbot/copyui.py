import streamlit as st
import requests
import pandas as pd
import subprocess
import shlex
import re
from tabulate import tabulate
from docker_ops import list_all_containers
from docker_ops import analyze_port_conflict
from troubleshooting import get_troubleshooting_guide
import urllib.parse


# ===============================
# Page config for full width
# ===============================
st.set_page_config(
    page_title="AI DevOps Chatbot & Docker Dashboard",
    layout="wide",  # full window width
    initial_sidebar_state="auto"
)

LOG_SNIPPET_LENGTH = 5  # last 5 lines for exited containers

# -------------------------------
# 💻 Docker Command Terminal (Top Bar)
# -------------------------------
with st.expander("💻 Docker Command Terminal", expanded=False):
    st.caption("Run Docker commands here (safe mode). Example: `docker ps`, `docker logs <container>`, `docker exec -it <container> bash`")

    cmd = st.text_input("Enter Docker command:", placeholder="e.g. docker ps -a or docker logs my_container")

 # Reference link section
    st.markdown(
        """
        📘 **Quick Docker CLI Reference:**
        - [Container List (`docker container ls`)](https://docs.docker.com/reference/cli/docker/container/ls/)
        - [Docker Images (`docker image ls`)](https://docs.docker.com/reference/cli/docker/image/ls/)
        - [Docker Volumes (`docker volume ls`)](https://docs.docker.com/reference/cli/docker/volume/ls/)
        - [Docker Logs (`docker logs`)](https://docs.docker.com/reference/cli/docker/container/logs/)
        - [Docker Exec (`docker exec`)](https://docs.docker.com/reference/cli/docker/container/exec/)
        - [Full CLI Reference](https://docs.docker.com/reference/cli/)
        - [Docker Troubleshooting](https://github.com/rajani0406/AI-DevOps-Chatbot-Docker-Assistant/wiki/%23-%F0%9F%A7%BE-Docker-Troubleshooting-Summary)
        """
    )

    # Security filters
    UNSAFE_KEYWORDS = [
        "rm -rf", "shutdown", "reboot", "poweroff", "dd", ":(){:|:&};:",
        "mkfs", "systemctl", "service", "killall", "halt"
    ]

    if st.button("▶ Run Command"):
        if not cmd.strip():
            st.warning("Please enter a Docker command.")
        elif any(bad in cmd for bad in UNSAFE_KEYWORDS):
            st.error("❌ Unsafe command detected. Operation blocked.")
        elif not cmd.startswith("docker "):
            st.error("⚠️ Only Docker commands are allowed in this terminal.")
        else:
            try:
                st.info(f"Running: `{cmd}`")
                result = subprocess.run(
                    shlex.split(cmd),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    st.code(result.stdout if result.stdout else "✅ Command executed successfully", language="bash")
                else:
                    st.error(f"⚠️ Error:\n{result.stderr}")
            except subprocess.TimeoutExpired:
                st.error("⏳ Command timed out.")
            except Exception as e:
                st.error(f"❌ Failed to execute: {e}")
# ===============================
# Troubleshooting Guide
# ===============================
st.subheader("🛠 Docker Troubleshooting Guide")
with st.expander("View Full Troubleshooting Guide", expanded=False):
    st.markdown(get_troubleshooting_guide(), unsafe_allow_html=True)

# ===============================
# Docker command reference
# ===============================
def show_docker_command_reference():
    st.subheader("🤖 Docker Assistant Command Reference")
    data = [
        {"Command": "🔁 Restart Stopped Containers", 
         "Query": "restart stopped containers / restart all stopped containers", 
         "Bot Response": "Asks for confirmation: '⚠️ Are you sure you want to restart all stopped containers? (yes / no)' → Restarts stopped containers if confirmed, shows restarted container names and any troubleshooting issues."},
        
        {"Command": "🧩 Show Stopped Containers", 
         "Query": "show stopped / list stopped / exited containers", 
         "Bot Response": "Lists all stopped containers using show_stopped_containers()."},
        
        {"Command": "🩺 Health Check", 
         "Query": "health / healthy", 
         "Bot Response": "Returns container health summary via get_container_health_summary()."},
        
        {"Command": "🌐 DNS Troubleshooting", 
         "Query": "dns resolution issues / temporary failure resolving", 
         "Bot Response": "Returns DNS troubleshooting info via Dnsissue()."},
        
        {"Command": "🛠 Fix DNS", 
         "Query": "fix dns issue / fix dns", 
         "Bot Response": "Fixes DNS issue programmatically via fix_dns_issue()."},
        
        {"Command": "🚪 Port Conflict", 
         "Query": "port conflict / port already in use", 
         "Bot Response": "Returns instructions to troubleshoot port conflicts via PortConflict()."},
        
        {"Command": "🔍 Check Port", 
         "Query": "check port <number>", 
         "Bot Response": "Checks which process/service is using the given port via check_port_usage(port). If no port provided, asks: '⚠️ Please specify a valid port number, e.g. check port 8080.'"},
        
        {"Command": "⚙️ Lifecycle Commands", 
         "Query": "start, stop, restart, pause, delete, remove", 
         "Bot Response": "Sets pending_action['action'] and asks whether to apply to a specific container or all."},
        
        {"Command": "🧱 Create Container", 
         "Query": "create ... from <image> named <name> on port <port>", 
         "Bot Response": "Creates a new container using create_new_container(image, name, port)."},
        
        {"Command": "📦 Show Images", 
         "Query": "show images / public images", 
         "Bot Response": "Returns popular images using show_popular_images()."},
        
        {"Command": "📊 Container Counts", 
         "Query": "Questions about container counts", 
         "Bot Response": "Returns number of running and stopped containers."},
        
        {"Command": "📄 Container Status", 
         "Query": "Questions about container status / show", 
         "Bot Response": "Returns running/stopped container summary."},
        
        {"Command": "🪵 Logs", 
         "Query": "Questions about container logs (log / error)", 
         "Bot Response": "Fetches logs via get_container_logs(name) and analyzes them using analyze_logs(logs)."},
        
        {"Command": "▶️ Start / ⏹ Stop / 🗑 Remove", 
         "Query": "Commands like start container <name>, stop container <name>, remove container <name>", 
         "Bot Response": "Instructs user how to start/stop/remove containers."},
        
        {"Command": "⬇️ Pull Image", 
         "Query": "Commands like pull image <image>", 
         "Bot Response": "Provides instruction on pulling/updating images."},
        
        {"Command": "🌐 Network Issues", 
         "Query": "Network issues", 
         "Bot Response": "Returns info about network issues or misconfigured ports."},
        
        {"Command": "💡 General Questions", 
         "Query": "Any other general question", 
         "Bot Response": "Returns AI fallback: instructions about Docker tasks (status, logs, restart, network troubleshooting, etc.)."}
    ]
    
    df = pd.DataFrame(data)
    st.dataframe(df, width="stretch", hide_index=True)
    st.markdown("""
    ---
    🧠 **Tip:** You can ask natural questions too, like:
    - “Is my container healthy?”
    - “Stop nginx and restart database container”
    - “Show Docker troubleshooting commands”
    - "Stop, Restart, Start, Remove to get Further Details.Then Provide Container Name to proceed with Action"                       
    - "Restart stopped containers"
    -  Show container status"
    - "Check logs for container"
    - "Why is my app not accessible?"
    - "List all running containers"
    - "Troubleshooting"
    -"check logs"
    -"show logs of XYZ"
    - "Show Stopped Containers"
    """)

show_docker_command_reference()

# ===============================
# Full-width layout with two columns
# Left: AI Chatbot | Right: Container tab
# ===============================
col_ai, col_dash = st.columns([4, 6])  # 30% / 70% width

# -------------------------------
# Left: AI DevOps Chatbot
# -------------------------------
with col_ai:
    st.title("🤖 AI DevOps Chatbot – Docker Assistant")
    user_input = st.text_input(
        "Ask your Docker assistant a question, e.g.:\n"
        "• 'Restart stopped containers'\n"
        "• 'Show container status'\n"
        "• 'Check logs for container xyz'\n"
        "• 'Why is my app not accessible?'\n"
        "• 'List all running containers'\n"
        "• 'Troubleshooting'"
    )

    if st.button("🛰️ Roger That!"):
        try:
            res = requests.post("http://127.0.0.1:8000/ask", json={"question": user_input})
            res.raise_for_status()  # Raise error for 4xx/5xx
            data = res.json()
            st.subheader("🧠 AI Response")
            st.write(data["answer"])
            if data.get("action"):
                st.success(data["action"])
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Backend request failed: {e}")
            st.info("Is FastAPI running on port 8000?")
        except ValueError:
            st.error("❌ Invalid JSON received from backend. Check backend logs for errors.")

# -------------------------------
# Right: Container Tab
# -------------------------------
with col_dash:
    tabs = st.tabs(["Dashboard", "Containers", "Images", "Volumes"])  # added 2 new tabs

    # -------------------------------
    # Tab 1: Dashboard (summary)
    # -------------------------------
    with tabs[0]:
        st.title("🐳 Docker Container Dashboard")
        containers, _ = list_all_containers()
        RESTART_THRESHOLD = 2

        def check_frequent_restarts(container):
            try:
                restart_count = container.attrs.get("RestartCount", 0)
                return restart_count > RESTART_THRESHOLD
            except Exception:
                return False

        total = len(containers)
        running = sum(1 for c in containers if c.status == "running")
        exited = sum(1 for c in containers if c.status == "exited")
        frequent_restart_containers = [c.name for c in containers if check_frequent_restarts(c)]
        if frequent_restart_containers:
            st.warning(f"⚠️ Containers with frequent restarts (>2 times): {', '.join(frequent_restart_containers)}")
        st.subheader("📊 Containers Summary")
        st.markdown(f"- **Total:** {total}")
        st.markdown(f"- **Running:** 🟢 {running}")
        st.markdown(f"- **Exited:** 🔴 {exited}")

    # -------------------------------
    # Tab 2: Containers (full list & expanders)
    # -------------------------------
    with tabs[1]:
        st.title("📋 All Containers")
        
        def get_container_logs(container, lines=5):
            try:
                logs = container.logs(tail=lines).decode("utf-8")
                return logs
            except Exception:
                return "Unable to fetch logs."
        
        def health_emoji(status):
            if status == "healthy":
                return "🟢"
            elif status == "unhealthy":
                return "🔴"
            elif status == "starting":
                return "🟠"
            else:
                return "🟠"

        if not containers:
            st.info("No containers found.")
        else:
            for c in containers:
                try:
                    health_status = c.attrs.get('State', {}).get('Health', {}).get('Status', 'unknown')
                except Exception:
                    health_status = "unknown"

                title = f"{c.name} | Status: {c.status} | Health: {health_emoji(health_status)}"
                if check_frequent_restarts(c):
                    title += " ⚠️ Frequent Restarts!"

                with st.expander(title, expanded=False):
                    st.write(f"**Container ID:** {c.short_id}")
                    st.write(f"**Image:** {(c.image.tags[0] if c.image.tags else '<none>')}")
                    st.write(f"**Status:** {c.status}")
                    st.write(f"**Health:** {health_status}")

                    try:
                        stats = c.stats(stream=False)
                        cpu_total = stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", None)
                        mem_usage = stats.get("memory_stats", {}).get("usage", None)
                        st.write(f"**CPU Usage (Total):** {cpu_total if cpu_total else 'N/A'}")
                        st.write(f"**Memory Usage:** {mem_usage if mem_usage else 'N/A'} bytes")
                    except Exception:
                        st.write("**CPU / Memory Usage:** N/A")

                    if c.status.lower() == "exited":
                        logs = get_container_logs(c, lines=LOG_SNIPPET_LENGTH)
                        st.write(f"**Exited Logs (last {LOG_SNIPPET_LENGTH} lines):**\n```\n{logs}\n```")

                    #col1, col2, col3, col4 = st.columns(4)
                    col = st.container()
                    with col:
                        if st.button(f"Restart {c.name}"):
                            try:
                                c.restart()
                                st.success(f"✅ {c.name} restarted successfully!")
                            except Exception as e:
                                error_msg = str(e)
                                # Full width error/info box with Google & ChatGPT links
                                error_encoded = urllib.parse.quote_plus(error_msg)
                                st.markdown(
                                    
    f"""
    <div style="
        border:2px solid #ff4b4b;
        border-radius:5px;
        padding:10px;
        width:100%;
        background-color:#fff5f5;
        word-wrap:break-word;
    ">
    💡 <b>Suggested next step:</b><br>
    You can search this error online: <br><br>
    
    🔹 <a href="https://www.google.com/search?q={error_encoded}" target="_blank" style="padding:5px 10px; background:#4285F4; color:white; border-radius:5px; text-decoration:none;">Search on Google</a><br><br>
    🔹 <a href="https://chat.openai.com/?model=gpt-4&q={error_encoded}" target="_blank" style="padding:5px 10px; background:#00A67E; color:white; border-radius:5px; text-decoration:none;">Ask ChatGPT</a><br><br>
    
    <div style="
        max-height:250px;
        overflow:auto;
        background-color:#ffeeee;
        padding:5px;
        border-radius:3px;
        white-space: pre-wrap;
        font-family:monospace;
    ">
    Docker container {c.name} restart failed: {error_msg}
    </div>
    </div>
    """,
    unsafe_allow_html=True
)
                    with col:
                        if st.button(f"Stop {c.name}"):
                            try:
                                c.stop()
                                st.success(f"🛑 {c.name} stopped successfully!")
                            except Exception as e:
                                st.error(f"⚠️ Failed to stop {c.name}:\n{str(e)}")

                    with col:
                        if st.button(f"Remove {c.name}"):
                            try:
                                c.remove(force=True)
                                st.success(f"🗑️ {c.name} removed successfully!")
                            except Exception as e:
                                st.error(f"⚠️ Failed to remove {c.name}:\n{str(e)}")

    # -------------------------------
    # Tab 3: Images
    # -------------------------------
    with tabs[2]:
        import docker
        st.title("🖼 Docker Images")
        client = docker.from_env()

        try:
            images = client.images.list()
        except Exception as e:
            st.error(f"⚠️ Failed to fetch images: {e}")
            images = []

        if not images:
            st.info("No Docker images found.")
        else:
            for img in images:
                tags = img.tags if img.tags else ["<none>"]
                used_by = [
                    c.name for c in client.containers.list(all=True)
                    if img.short_id in c.image.id
                ]

                st.write(f"**ID:** {img.short_id} | **Tags:** {', '.join(tags)}")
                if used_by:
                    st.info(f"📦 Used by containers: {', '.join(used_by)}")

                if st.button(f"🗑️ Delete Image {img.short_id}"):
                    if used_by:
                        st.warning(f"⚠️ Cannot delete image {img.short_id} — used by container(s): {', '.join(used_by)}. Stop & remove them first.")
                    else:
                        try:
                            client.images.remove(image=img.id, force=True)
                            st.success(f"🗑️ Image {img.short_id} deleted successfully!")
                        except Exception as e:
                            st.error(f"⚠️ Failed to delete image {img.short_id}:\n{str(e)}")

    # -------------------------------
    # Tab 4: Volumes
    # -------------------------------
    with tabs[3]:
        st.title("💾 Docker Volumes")
        import docker
        client = docker.from_env()
        try:
            volumes = client.volumes.list()
        except Exception as e:
            st.error(f"⚠️ Failed to fetch volumes: {e}")
            volumes = []

        if not volumes:
            st.info("No Docker volumes found.")
        else:
            for vol in volumes:
                st.write(f"**Name:** {vol.name}")
                st.write(f"**Mountpoint:** {vol.attrs.get('Mountpoint', 'N/A')}")
                
                # Check if any container is using this volume
                containers_using = []
                for c in client.containers.list(all=True):
                    mounts = c.attrs.get("Mounts", [])
                    for m in mounts:
                        if m.get("Name") == vol.name:
                            containers_using.append(c.name)

                if containers_using:
                    st.info(f"📦 Used by containers: {', '.join(containers_using)}")

                if st.button(f"🗑️ Delete Volume {vol.name}"):
                    if containers_using:
                        st.warning(f"⚠️ Cannot delete volume '{vol.name}' — used by container(s): {', '.join(containers_using)}. Stop & remove them first.")
                    else:
                        try:
                            vol.remove(force=True)
                            st.success(f"🗑️ Volume '{vol.name}' deleted successfully!")
                        except Exception as e:
                            st.error(f"⚠️ Failed to delete volume '{vol.name}': {e}")