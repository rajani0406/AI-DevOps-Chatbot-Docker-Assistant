import os
import openai

# Try to initialize the OpenAI client safely
openai.api_key = os.getenv("OPENAI_API_KEY")

def interpret_docker_question(question, containers):
    """
    Process user questions about Docker containers.
    If OpenAI API key is missing or quota exceeded, use mock responses.
    """

    # --- If no key or quota issue, use mock ---
    if not openai.api_key:
        return mock_ai_response(question, containers)

    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a DevOps assistant that monitors Docker containers and explains issues clearly.",
                },
                {
                    "role": "user",
                    "content": f"User question: {question}\n\nContainer info:\n{containers}",
                },
            ],
        )
        return resp.choices[0].message["content"]

    except Exception as e:
        print(f"⚠️ AI error: {e}")
        # Fallback to mock mode
        return mock_ai_response(question, containers)

def mock_ai_response(question, containers):
    """
    Simulate AI answers without OpenAI API.
    Produces clean, readable summaries of Docker container states.
    """
    question = question.lower()

    # Normalize container info
    running = []
    stopped = []

    for c in containers:
        status = c.get("status", "").lower()
        name = c.get("name", "unknown")
        image = ", ".join(c.get("image", [])) if isinstance(c.get("image"), list) else c.get("image", "unknown")

        if "up" in status or "running" in status:
            running.append(f"{name} ({image})")
        elif "exited" in status or "stopped" in status:
            stopped.append(f"{name} ({image})")

    # Build a clean summary
    summary = []
    if running:
        summary.append(f"🟢 Running containers ({len(running)}):\n" + "\n".join(f"• {r}" for r in running))
    if stopped:
        summary.append(f"🔴 Stopped containers ({len(stopped)}):\n" + "\n".join(f"• {s}" for s in stopped))
    if not summary:
        summary.append("No containers found.")

    # --- Responses based on question intent ---
    if "how many" in question and "container" in question:
        return f"There are {len(running)} running containers and {len(stopped)} stopped containers."

    elif "status" in question or "show" in question:
        return "\n\n".join(summary)

    elif "restart" in question:
        if stopped:
            return f"I would restart these stopped containers:\n" + "\n".join(f"• {s}" for s in stopped)
        else:
            return "All containers are running. No need to restart."

    elif "not accessible" in question or "down" in question:
        return "It seems one of your containers is not running. Try `docker ps -a` or restarting the service."

    else:
        return "I can check container status, count them, or simulate restarts. Try asking 'show status' or 'restart stopped containers'."


