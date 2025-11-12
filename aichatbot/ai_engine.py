import os
import openai
import docker 
from docker_ops import get_container_logs, get_all_containers_info
from log_analyzer import analyze_logs
import re  # <--- Add this line
import docker_ops  # make sure docker_ops is imported if using its functions
from dns_resolution_error import Dnsissue 
from dns_resolution_error import fix_dns_issue
from port_conflict import PortConflict
from port_conflict import check_port_usage

from docker_ops import (
    client,
    get_all_containers_info,
    get_container_health_summary,
    create_new_container,
    restart_stopped_containers,
    get_container_logs,
    show_popular_images,
    show_stopped_containers,
    smart_start_container,
    
)
# 🧠 Track interactive container actions
pending_action = {"action": None}
pending_restart_all = {"awaiting_confirmation": False}

response = None
# Initialize OpenAI safely
#openai.api_key = os.getenv("OPENAI_API_KEY")

LOG_SNIPPET_LENGTH = 400  # last N chars of logs

def interpret_docker_question(question, containers):
   
    """
    Process user questions about Docker containers.
    Returns a clean response for chatbot UI.
    """
    global pending_action  # ✅ enables access to global variable
    
       # 🧠 Detect health or lifecycle management intent
    q_lower = question.lower()

         # 🧠 Step 1: User said "restart stopped containers"
   
    if re.search(r"\brestart (all )?stopped containers?\b", question, re.IGNORECASE) or pending_restart_all["awaiting_confirmation"]:
        if pending_restart_all["awaiting_confirmation"]:
            if q_lower in ["yes", "y"]:
                restarted, troubleshooting = docker_ops.restart_stopped_containers()
                pending_restart_all["awaiting_confirmation"] = False
                response = ""
                if restarted:
                    response += "✅ Restarted the following stopped containers:\n"
                    response += "\n".join([f" - {name}" for name in restarted])
                if troubleshooting:
                    response += "\n\n⚠️ Some issues were detected:\n"
                    for name, info in troubleshooting.items():
                        response += f"- {name}:\n{info}\n"
                if not restarted and not troubleshooting:
                    response = "ℹ️ No stopped containers found to restart."
                return response
            elif q_lower in ["no", "n"]:
                pending_restart_all["awaiting_confirmation"] = False
                return "❌ Restart operation cancelled."
            else:
                return "⚠️ Please confirm: yes / no"
        else:
            pending_restart_all["awaiting_confirmation"] = True
            return "⚠️ Are you sure you want to restart all stopped containers? (yes / no)"

    # 🟢 Step 2: Show stopped containers
    if "show stopped" in q_lower or "list stopped" in q_lower or "exited containers" in q_lower:
        return show_stopped_containers()
    

    # 🩺 Step 3: Health check
    if "health" in q_lower or "healthy" in q_lower:
        return get_container_health_summary()
    
        #when user says dns issues
    
    if "dns resolution issues" in q_lower or "temporary failure resolving" in q_lower:
        return Dnsissue()
    elif q_lower.strip() in ["fix dns issue", "fix dns"]:
        return fix_dns_issue()
   
    if "port conflict" in q_lower or "port in use" in q_lower:
     return PortConflict()
    
    elif "check port" in q_lower:
     words = q_lower.split()
     port = None
     for i, word in enumerate(words):
        if word == "port" and i + 1 < len(words):
            if words[i + 1].isdigit():
                port = int(words[i + 1])
                break
     if port:
        response = check_port_usage(port)
     else:
        response = "⚠️ Please specify a valid port number, e.g. `check port 8080`."

   # Finally return the response
     return response  

    # ⚙️ Step 4: Lifecycle actions (start/stop/restart/pause/delete)
    lifecycle_actions = ["start", "stop", "restart", "pause", "delete", "remove"]
    for act in lifecycle_actions:
        if act in q_lower:
            pending_action["action"] = "delete" if act in ["remove", "delete"] else act
            return (
                f"⚙️ You want to **{pending_action['action']} containers**.\n\n"
                "Would you like to:\n"
                "1️⃣ Provide a specific container name (e.g., `webapp`)\n"
                "2️⃣ Or type `all` to apply this to all matching containers?"
            )

    # ✅ Step 5: Create new container
    if "create" in q_lower or "run" in q_lower:
        words = question.split()
        image = None
        name = None
        port = None
        for i, word in enumerate(words):
            if word == "from" and i + 1 < len(words):
                image = words[i + 1]
            elif word == "named" and i + 1 < len(words):
                name = words[i + 1]
            elif word == "on" and "port" in words[i + 1:]:
                port_index = words.index("port")
                port = words[port_index + 1] if port_index + 1 < len(words) else None
        return create_new_container(image, name, port)

    # ✅ Step 6: Show popular images
    if "show images" in q_lower or "public images" in q_lower:
        return show_popular_images()

    # 🧠 Step 7: Fallback AI explanation
    if not openai.api_key:
        return mock_ai_response(question, containers)

    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a DevOps AI that manages Docker containers interactively."},
                {"role": "user", "content": f"User question: {question}\nContainers: {containers}"}
            ]
        )
        return resp.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ AI error: {e}"

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

    # --- Handle specific questions ---
    if "how many" in question_lower and "container" in question_lower:
        return f"There are {len(running)} running containers and {len(stopped)} stopped containers."

    elif "status" in question_lower or "show" in question_lower:
        return "\n\n".join(summary)

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
