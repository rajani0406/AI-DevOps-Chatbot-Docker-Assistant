import streamlit as st
import subprocess

# --- Helpers for Docker check ---
def check_docker_environment():
    """Check Docker installation and service status."""
    try:
        subprocess.run(["docker", "info"], capture_output=True, text=True, check=True)
        return {"status": "running", "message": "Docker is installed and running."}
    except FileNotFoundError:
        return {"status": "not_installed", "message": "Docker is not installed."}
    except subprocess.CalledProcessError:
        return {"status": "not_running", "message": "Docker installed but service not running."}

def setup_docker_environment():
    """Dummy function to simulate Docker setup."""
    return "Docker environment setup executed."

def start_docker_service():
    """Dummy function to simulate starting Docker service."""
    return "Docker service started."

def check_docker_socket():
    """Checks if Docker socket is available."""
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return "✅"
    except subprocess.CalledProcessError:
        return "⚠️"
    except FileNotFoundError:
        return "❌"

def get_docker_version():
    """Returns Docker version if available."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Unknown"
    except FileNotFoundError:
        return "Not Installed"

# --- Streamlit UI ---
def docker_environment_tab():
    st.title("🐳 Docker Environment Assistant")
    st.write("This tool verifies your system’s Docker setup and helps fix any missing components automatically.")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("🔍 Environment Check")

        if st.button("Run Docker Environment Check"):
            with st.spinner("Checking Docker environment..."):
                result = check_docker_environment()
                st.session_state["docker_status"] = result

        if "docker_status" in st.session_state:
            result = st.session_state["docker_status"]
            st.info(result["message"])

            if result["status"] == "not_installed":
                if st.button("⚙️ Prepare Environment for Docker"):
                    with st.spinner("Setting up Docker environment..."):
                        output = setup_docker_environment()
                        st.success(output)

            elif result["status"] == "not_running":
                if st.button("▶️ Start Docker Service"):
                    with st.spinner("Starting Docker service..."):
                        output = start_docker_service()
                        st.success(output)

            elif result["status"] == "running":
                st.success("🎉 Docker is fully operational!")

    # Right-side status
    with col_right:
        st.subheader("📊 Docker Status Overview")

        status = st.session_state.get("docker_status", {})
        docker_installed = "✅" if status.get("status") != "not_installed" else "❌"
        docker_running = "✅" if status.get("status") == "running" else "⚠️"
        docker_socket = check_docker_socket()
        docker_version = get_docker_version()

        def show_status(label, value):
            st.markdown(f"**{label}:** {value}")

        show_status("Docker Installed", docker_installed)
        show_status("Docker Service", docker_running)
        show_status("Docker Socket", docker_socket)
        show_status("Docker Version", docker_version)
