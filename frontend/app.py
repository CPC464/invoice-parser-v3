import os
import streamlit as st
import requests
from dotenv import load_dotenv
import tempfile
import time

# Load environment variables
load_dotenv()

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_URL = f"{BACKEND_URL}/api/v1"
FILES_ENDPOINT = f"{API_URL}/files/"

# Public URL for browser access
PUBLIC_BACKEND_URL = "http://localhost:8888"  # Use the exposed port from docker-compose

# App title and configuration
st.set_page_config(
    page_title="Invoice Parser",
    page_icon="📄",
    layout="wide",
)

# Custom styling
st.markdown(
    """
<style>
    .file-uploader > section > div > button {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    .stButton > button {
        width: 100%;
    }
    .fullwidth {
        width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title
st.title("📄 Invoice Parser")
st.markdown("Upload, manage, and process your invoice files")


# Function to get all files
def get_files():
    try:
        response = requests.get(FILES_ENDPOINT)
        if response.status_code == 200:
            results = response.json().get("results", [])
            # Fix URLs for browser access
            for file in results:
                if file.get("file_url"):
                    file["file_url"] = file["file_url"].replace(
                        "backend:8000", f"localhost:8888"
                    )
            return results
        else:
            st.error(f"Error fetching files: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []


# Function to upload a file
def upload_file(file, user_defined_name=None):
    try:
        # Create a temporary file with the same name
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.name)[1]
        ) as tmp_file:
            tmp_file.write(file.getbuffer())
            tmp_file_path = tmp_file.name

        # Prepare form data
        files = {"file": open(tmp_file_path, "rb")}
        data = {}
        if user_defined_name:
            data["user_defined_file_name"] = user_defined_name

        # Send request
        response = requests.post(FILES_ENDPOINT, files=files, data=data)

        # Clean up temporary file
        os.unlink(tmp_file_path)

        if response.status_code == 201:
            result = response.json()
            # Fix URL for browser access
            if result.get("file_url"):
                result["file_url"] = result["file_url"].replace(
                    "backend:8000", f"localhost:8888"
                )
            return True, result
        else:
            return (
                False,
                f"Failed to upload file: {response.status_code} - {response.text}",
            )
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"


# Function to delete a file
def delete_file(file_id):
    try:
        response = requests.delete(f"{FILES_ENDPOINT}{file_id}/")
        return response.status_code == 204, response.status_code
    except Exception as e:
        return False, str(e)


# Function to update file name
def update_file_name(file_id, new_name):
    try:
        response = requests.patch(
            f"{FILES_ENDPOINT}{file_id}/", json={"user_defined_file_name": new_name}
        )
        if response.status_code == 200:
            result = response.json()
            # Fix URL for browser access
            if result.get("file_url"):
                result["file_url"] = result["file_url"].replace(
                    "backend:8000", f"localhost:8888"
                )
            return True, result
        else:
            return (
                False,
                f"Failed to update file name: {response.status_code} - {response.text}",
            )
    except Exception as e:
        return False, f"Error updating file name: {str(e)}"


# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Upload File", "Manage Files"])

# Tab 1: File Upload
with tab1:
    st.header("Upload a File")

    # File upload section
    uploaded_file = st.file_uploader(
        "Choose a file", type=["pdf", "png", "jpg", "jpeg", "txt"], key="file_uploader"
    )
    user_name = st.text_input("Custom File Name (optional)")

    if uploaded_file is not None:
        st.write("File details:")
        st.write(f"- Name: {uploaded_file.name}")
        st.write(f"- Type: {uploaded_file.type}")
        st.write(f"- Size: {uploaded_file.size} bytes")

        if st.button("Upload File", key="upload_btn"):
            with st.spinner("Uploading file..."):
                success, result = upload_file(uploaded_file, user_name)
                if success:
                    st.success("File uploaded successfully!")
                    st.json(result)
                else:
                    st.error(result)

# Tab 2: File Management
with tab2:
    st.header("Manage Files")

    # Add a refresh button
    if st.button("Refresh File List"):
        st.experimental_rerun()

    # Get all files
    with st.spinner("Loading files..."):
        files = get_files()

    if not files:
        st.info("No files found. Upload some files in the Upload tab.")
    else:
        st.write(f"Found {len(files)} files")

        # Create a container for each file
        for file in files:
            with st.expander(
                f"{file.get('user_defined_file_name') or file.get('original_file_name')}",
                expanded=True,
            ):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"**Original filename:** {file.get('original_file_name')}")
                    st.write(f"**Upload date:** {file.get('uploaded_at')}")
                    if file.get("file_url"):
                        st.markdown(f"[View/Download File]({file.get('file_url')})")

                with col2:
                    # Edit name form
                    new_name = st.text_input(
                        "New name",
                        value=file.get("user_defined_file_name", ""),
                        key=f"name_{file.get('id')}",
                    )
                    if st.button("Update Name", key=f"update_{file.get('id')}"):
                        with st.spinner("Updating..."):
                            success, result = update_file_name(file.get("id"), new_name)
                            if success:
                                st.success("Name updated!")
                                time.sleep(1)
                                st.experimental_rerun()
                            else:
                                st.error(result)

                with col3:
                    # Delete button
                    st.write("&nbsp;", unsafe_allow_html=True)  # Spacing
                    if st.button(
                        "Delete File", key=f"delete_{file.get('id')}", type="primary"
                    ):
                        with st.spinner("Deleting..."):
                            success, result = delete_file(file.get("id"))
                            if success:
                                st.success("File deleted!")
                                time.sleep(1)
                                st.experimental_rerun()
                            else:
                                st.error(f"Error: {result}")

# Footer
st.markdown("---")
st.markdown("📄 Invoice Parser System | Developed with Django and Streamlit")
