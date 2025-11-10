
from fastapi import FastAPI, Request
from docker_ops import get_all_containers_info, restart_stopped_containers
from ai_engine import interpret_docker_question

app = FastAPI()

@app.post("/ask")
async def ask_docker_assistant(request: Request):
    data = await request.json()
    question = data.get("question", "")

    containers = get_all_containers_info()
    ai_response = interpret_docker_question(question, containers)

    # Action trigger
    action_taken = None
    if "restart" in question.lower() and "stopped" in question.lower():
        restarted = restart_stopped_containers()
        action_taken = f"Restarted containers: {', '.join(restarted)}"

    return {
        "answer": ai_response,
        "containers": containers,
        "action": action_taken
    }

