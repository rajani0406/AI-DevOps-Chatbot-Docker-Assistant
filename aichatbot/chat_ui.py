import streamlit as st
import requests

st.title("🤖 AI DevOps Chatbot – Docker Assistant")

user_input = st.text_input(
    "Ask your Docker assistant a question, e.g.:\n"
    "• 'Restart stopped containers'\n"
    "• 'Show container status'\n"
    "• 'Check logs for container xyz'\n"
    "• 'Why is my app not accessible?'\n"
    "• 'List all running containers\n'"
    "•  'Troubleshooting'"
)

if st.button("Ask"):
    try:
        res = requests.post("http://127.0.0.1:8000/ask", json={"question": user_input})
        res.raise_for_status()  # Raise error for 4xx/5xx
        data = res.json()

        st.subheader("🧠 AI Response")
        st.write(data["answer"])

        if data.get("action"):
            st.success(data["action"])

        st.subheader("🐳 Container Summary")
        st.json(data["containers"])

        # ✅ Show troubleshooting info if present
        troubleshooting_text = data.get("troubleshooting")
        if troubleshooting_text:
            st.subheader("🛠 Docker Troubleshooting")
            st.code(troubleshooting_text, language="bash")

        if data.get("troubleshooting"):
           st.subheader("⚠️ Troubleshooting Steps")
           for container, steps in data["troubleshooting"].items():
             st.write(f"**{container}**:\n{steps}")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Backend request failed: {e}")
        st.info("Is FastAPI running on port 8000?")
    except ValueError:
        st.error("❌ Invalid JSON received from backend. Check backend logs for errors.")

