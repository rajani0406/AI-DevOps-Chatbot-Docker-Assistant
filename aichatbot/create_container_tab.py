import streamlit as st
import subprocess

# --- Helper Functions ---
def list_local_images():
    """Return a list of local Docker images."""
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True, text=True
        )
        images = result.stdout.strip().split("\n")
        return images if images[0] else []
    except FileNotFoundError:
        return []

def create_container(image_name):
    """Create a container from a given image in detached mode with a default command."""
    try:
        cmd = ["docker", "run", "-d"]
        
        # Add container name if provided
        
        # Use image name
        cmd.append(image_name)
        
        # Add a default command to keep container alive if none is provided
        cmd += ["tail", "-f", "/dev/null"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ Container created from {image_name} (ID: {result.stdout.strip()})"
        else:
            return f"❌ Failed to create container: {result.stderr.strip()}"
    except FileNotFoundError:
        return "❌ Docker not installed"

# --- Streamlit UI ---
def docker_create_container_tab():
    st.title("🐳 Create Docker Container")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📦 Local Docker Images")
        images = list_local_images()

        if images:
            for idx, img in enumerate(images):
              col_img, col_btn = st.columns([3,1])
              with col_img:
               st.text(img)
              with col_btn:
        # Replace ":" with "_" to avoid key issues and add index to make it unique
               safe_key = f"create_{img.replace(':', '_')}_{idx}"
               if st.button("Create Container", key=safe_key):
                with st.spinner(f"Creating container from {img}..."):
                 output = create_container(img)
                 st.success(output)
        else:
            st.info("No local images found. Please ask the ChatBot to pull an image first and return here.")

    # --- Right-side Status Panel ---
    with col_right:
        st.subheader("📊 Docker Status")
        try:
            running_containers = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True, text=True
            ).stdout.strip().split("\n")
            running_containers = [c for c in running_containers if c]
            st.markdown(f"**Running Containers:** {len(running_containers)}")
            for c in running_containers:
                st.text(f"▶️ {c}")
        except FileNotFoundError:
            st.text("❌ Docker not installed")
