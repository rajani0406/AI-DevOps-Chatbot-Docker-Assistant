Docker Assistant — Prompt Guide (How to talk to the bot)

Short: type plain English prompts. The bot will ask for clarification when needed (e.g., which container), then run the requested action and confirm.

1. Show containers & status

What to type

show all containers

list containers

show running containers

show stopped containers

show container health

What bot does / asks

Immediately returns a neat table or list of containers (name, status, image, id).

For show container health it returns 🟢 / 🟠 / 🔴 statuses and healthcheck values.

Example

You: show stopped containers
Bot: 🔴 Stopped Containers
 - webapp → Image: nginx:latest, Exit Code: 0, Last stopped at: 2025-11-11T12:05:23Z

2. Start a container

What to type

start container <name> — e.g. start container webapp

start container — bot will prompt for which container

start all stopped containers or start all stopped — bulk action

Follow-up prompt (if you typed just start container)

Bot: Do you want to start a specific container or all stopped containers?
1) Provide container name (e.g., webapp)
2) Or type 'all' to start all stopped containers


What bot does

If container is paused → bot automatically unpauses it and confirms.

If container is stopped → bot starts it and confirms.

If container already running → bot says it’s already running.

Example flows

You: start container
Bot: Provide a name or type 'all'
You: webapp
Bot: ✅ Container `webapp` started successfully.


or

You: start all stopped
Bot: ✅ Started 3 stopped containers.

3. Stop a container

What to type

stop container <name> — e.g. stop container db

stop container — bot will ask which one

stop all running containers or stop all running

Follow-up prompt (if you typed just stop container)

same: bot lists containers and asks to provide a name or all.

What bot does

Stops the container(s) and confirms. If container already stopped, bot reports that.

Example

You: stop container
Bot: Which container? (or type 'all')
You: api
Bot: 🛑 Container `api` stopped successfully.

4. Restart a container

What to type

restart container <name>

restart container (bot will prompt)

restart all or restart all running

What bot does

If container is paused → bot will unpause then restart as needed.

Confirms after successful restart.

Example

You: restart container webapp
Bot: 🔁 Container `webapp` restarted successfully.

5. Pause / Resume (Unpause)

What to type

pause container <name>

pause container (bot will prompt)

resume container <name> or unpause container <name>

What bot does

Pauses a running container (suspends processes) or resumes a paused one.

Confirms success.

Example

You: pause container db
Bot: ⏸️ Container `db` paused successfully.
You: resume container db
Bot: ▶️ Container `db` resumed successfully.

6. Remove / Delete container(s)

What to type

remove container <name> or delete container <name>

remove container (bot will prompt)

remove all stopped containers or delete all stopped

What bot does

For single container: removes (force remove) and confirms.

For all variants: removes appropriate set and returns count. (Use caution)

Example

You: remove container
Bot: Provide name or 'all' to remove all stopped
You: all
Bot: 🗑️ All stopped containers deleted successfully.

7. Create / Run new container

What to type

create container <name> from <image>

create container <name> from <image> on port <port>

If you omit details

Bot will show the usage template and a list of popular images to choose from.

Example

You: create container myweb from nginx:latest on port 8080
Bot: 🚀 New container 'myweb' started from image 'nginx:latest' on port 8080.

8. Logs & analysis

What to type

show logs for <container_name>

get logs <container_name>

tail logs <container_name>

What bot does

Returns last N lines (default tail) of logs and may run analyze_logs() to give suggestions.

Example

You: show logs for webapp
Bot: 📄 Logs for 'webapp':
<last 400 chars>
Bot: 🔍 Likely cause: port conflict / missing env var / DB connection refused

9. Troubleshooting & diagnostics

Useful prompts

troubleshooting or show troubleshooting — shows common Docker commands and steps.

show port conflicts or check ports — checks ports 80 and 443 and suggests actions.

restart stopped containers — attempts to restart all stopped containers and reports per-container troubleshooting if a restart fails.

What bot does

Runs sudo lsof -i :80 and :443 checks, suggests stopping apache2/nginx if found, shows commands to fix, and provides helpful next steps.

Example

You: show port conflicts
Bot: Port 80 in use by apache2 (pid 1047)
Bot: Suggestion: sudo systemctl stop apache2

10. Bulk / shorthand commands

Accepted natural shortcuts

start all stopped — start every stopped container

stop all running — stop all running containers

restart all — restart every container

remove all stopped — delete all exited containers

Bot behavior

For bulk commands, bot performs the bulk operation and returns a count/confirmation.

11. Interactive flow summary (how the pending prompt works)

You say a lifecycle command but don’t provide a container name (e.g., start container).

Bot replies with options:

Provide a single container name (example: webapp)

Or type all to perform the action on all matching containers (all stopped for start, all running for stop, etc.)

You reply with the name or all.

Bot executes and confirms the outcome.

Example

You: stop container
Bot: Would you like to specify a name or type 'all'?
You: all
Bot: 🛑 Stopped 4 running containers.

12. Common errors & what to do

"cannot start a paused container, try unpause instead"
→ Bot will now detect paused state and unpause instead of start. If you see this, let the bot unpause or use resume/unpause.

Port conflict errors (address already in use)
→ Bot will show processes using port 80/443 and recommend sudo systemctl stop apache2 or sudo systemctl stop nginx. Use caution with these commands.

Container not found
→ Check exact container name with show all containers. Names are case-sensitive.

13. Tips for users

For best results, use the words shown (start/stop/restart/pause/unpause/remove/create/show logs). The assistant recognizes many variations, but these are the clearest.

If you’re unsure of container name, type show all containers first — then copy/paste the name.

For destructive commands (remove all, delete all) double-check — these remove containers permanently.

The bot auto-handles paused containers (it will unpause rather than failing).

If AI (OpenAI) is unavailable, the bot falls back to rule-based replies and still performs container operations locally.

14. Quick reference cheat-sheet

show all containers → list all

show running containers → running only

show stopped containers → exited containers (with exit codes)

start container <name> → start/unpause as needed

start container → bot will ask: name or all

stop container <name> or stop container → same interactive flow

restart container <name> or restart all

pause container <name> / resume container <name>

remove container <name> / remove all stopped containers

create container <name> from <image> on port <port>

show logs for <name> → last logs + analysis

show port conflicts → check port 80 / 443 and suggestion
