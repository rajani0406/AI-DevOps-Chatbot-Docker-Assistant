import streamlit as st
import requests

st.title("🤖 AI DevOps Chatbot – Docker Assistant")

user_input = st.text_input("Ask something about your containers (e.g. 'restart stopped', 'show status'):")

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

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Backend request failed: {e}")
        st.info("Is FastAPI running on port 8000?")
    except ValueError:
        st.error("❌ Invalid JSON received from backend. Check backend logs for errors.")

