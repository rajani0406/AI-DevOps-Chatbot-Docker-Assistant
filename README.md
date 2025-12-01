🐳 Docker Assistant — Prompt Guide

<img width="1832" height="963" alt="image" src="https://github.com/user-attachments/assets/3f83d3c4-a6a5-4202-bb3f-37afd31ab9d6" />


A complete reference on how to interact with the bot using natural language.

🧭 Overview

You can talk to the Docker Assistant in plain English — no complex syntax needed.
The bot understands intent (e.g., “start container webapp”), asks for clarification if required, and performs the requested Docker actions automatically.

🧩 1. Show Containers & Status
💬 What to Type
show all containers
list containers
show running containers
show stopped containers
show container health

🤖 What the Bot Does

Returns a table or list of containers (name, status, image, id).

For show container health, displays 🟢 / 🟠 / 🔴 statuses with healthcheck info.

🧾 Example
You: show stopped containers
Bot: 🔴 Stopped Containers
 - webapp → Image: nginx:latest, Exit Code: 0, Last stopped at: 2025-11-11T12:05:23Z

▶️ 2. Start a Container
💬 What to Type
start container <name>
start container
start all stopped containers
start all stopped

💡 Follow-Up (if you omit container name)
Bot: Do you want to start a specific container or all stopped containers?
1) Provide container name (e.g., webapp)
2) Or type 'all' to start all stopped containers

🤖 What the Bot Does

If paused → unpauses automatically.

If stopped → starts it.

If already running → reports as already running.

🧾 Examples
You: start container
Bot: Provide a name or type 'all'
You: webapp
Bot: ✅ Container 'webapp' started successfully.

You: start all stopped
Bot: ✅ Started 3 stopped containers.

⏹️ 3. Stop a Container
💬 What to Type
stop container <name>
stop container
stop all running containers
stop all running

🤖 What the Bot Does

Stops the specified container(s). If already stopped, the bot notifies you.

🧾 Example
You: stop container
Bot: Which container? (or type 'all')
You: api
Bot: 🛑 Container 'api' stopped successfully.

🔁 4. Restart a Container
💬 What to Type
restart container <name>
restart container
restart all
restart all running

🤖 What the Bot Does

Unpauses paused containers before restarting.

Confirms upon success.

🧾 Example
You: restart container webapp
Bot: 🔁 Container 'webapp' restarted successfully.

⏸️ 5. Pause / Resume a Container
💬 What to Type
pause container <name>
resume container <name>
unpause container <name>

🤖 What the Bot Does

Pauses (suspends) or resumes (unpauses) containers as requested.

🧾 Example
You: pause container db
Bot: ⏸️ Container 'db' paused successfully.
You: resume container db
Bot: ▶️ Container 'db' resumed successfully.

🗑️ 6. Remove / Delete Containers
💬 What to Type
remove container <name>
remove container
remove all stopped containers
delete all stopped

🤖 What the Bot Does

Removes the container(s) — force remove by default.

🧾 Example
You: remove container
Bot: Provide name or 'all' to remove all stopped
You: all
Bot: 🗑️ All stopped containers deleted successfully.

🚀 7. Create / Run a New Container
💬 What to Type
create container <name> from <image>
create container <name> from <image> on port <port>

🤖 What the Bot Does

Creates and starts a new container from the specified image.
If details are missing, it shows a usage template and common images.

🧾 Example
You: create container myweb from nginx:latest on port 8080
Bot: 🚀 New container 'myweb' started from image 'nginx:latest' on port 8080.

📜 8. Logs & Analysis
💬 What to Type
show logs for <container_name>
get logs <container_name>
tail logs <container_name>

🤖 What the Bot Does

Shows recent logs and may analyze them for common issues.

🧾 Example
You: show logs for webapp
Bot: 📄 Logs for 'webapp':
<last 400 chars>
Bot: 🔍 Likely cause: port conflict / missing env var / DB connection refused

🧰 9. Troubleshooting & Diagnostics
💬 Useful Prompts
troubleshooting
show troubleshooting
show port conflicts
check ports
restart stopped containers

🤖 What the Bot Does

Checks for port 80/443 conflicts (e.g., Apache or Nginx).

Suggests stopping conflicting services.

Provides troubleshooting steps.

🧾 Example
You: show port conflicts
Bot: Port 80 in use by apache2 (pid 1047)
Bot: Suggestion: sudo systemctl stop apache2

⚙️ 10. Bulk / Shorthand Commands
💬 Examples
start all stopped
stop all running
restart all
remove all stopped

🤖 What the Bot Does

Performs the bulk action and returns a summary (count + confirmation).

🧩 11. Interactive Flow Summary
Example Flow
You: stop container
Bot: Would you like to specify a name or type 'all'?
You: all
Bot: 🛑 Stopped 4 running containers.

❗ 12. Common Errors & Fixes
Error	Meaning / Fix
cannot start a paused container, try unpause instead	Bot now detects paused state and unpauses automatically.
address already in use	Port conflict (80/443). Bot suggests stopping Apache/Nginx.
container not found	Check spelling with show all containers. Names are case-sensitive.
💡 13. Tips for Users

Use clear verbs: start, stop, restart, pause, resume, remove, create, show logs.

Unsure of name? → show all containers first.

⚠️ Double-check destructive commands (remove all) — they’re permanent.

Bot automatically handles paused containers.

If OpenAI (AI mode) is down, fallback logic still performs container operations locally.

📘 14. Quick Reference Cheat Sheet
Command	Action
show all containers	List all containers
show running containers	Only running
show stopped containers	Only stopped/exited
start container <name>	Start/unpause
stop container <name>	Stop
restart container <name>	Restart
pause container <name>	Pause
resume container <name>	Resume
remove container <name>	Delete container
remove all stopped containers	Delete all exited
create container <name> from <image> on port <port>	Create new
show logs for <name>	View logs
show port conflicts	Check port 80/443 usage
