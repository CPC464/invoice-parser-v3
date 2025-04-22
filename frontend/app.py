import os
import streamlit as st
import requests
from dotenv import load_dotenv
import tempfile
import time
import threading
import queue
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# API Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_URL = f"{BACKEND_URL}/api/v1"
FILES_ENDPOINT = f"{API_URL}/files/"

# Thread configuration
NUMBER_OF_WORKER_THREADS = int(os.getenv("NUMBER_OF_WORKER_THREADS", 10))

# Upload queue
upload_queue = queue.Queue()
upload_results: List[Dict[str, Any]] = []
upload_in_progress = False
upload_completed = 0
upload_total = 0

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
    .upload-status {
        margin-top: 20px;
        padding: 10px;
        border-radius: 5px;
    }
    .upload-progress {
        margin-top: 10px;
        margin-bottom: 20px;
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

        # Send request with increased timeout
        response = requests.post(FILES_ENDPOINT, files=files, data=data, timeout=60)

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
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {str(e)}"
    except requests.exceptions.Timeout as e:
        return False, f"Request timed out: {str(e)}"
    except Exception as e:
        return False, f"Error uploading file: {str(e)}"


# Worker function for the thread pool
def upload_worker():
    global upload_completed
    while True:
        # Get file from queue
        try:
            file_data = upload_queue.get()
            if file_data is None:  # Sentinel value to terminate worker
                upload_queue.task_done()
                break

            file, user_name = file_data

            # Add retry logic
            max_retries = 3
            retry_delay = 2  # seconds
            success = False
            result = None

            for attempt in range(max_retries):
                if attempt > 0:
                    # Wait before retrying
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

                success, result = upload_file(file, user_name)
                if success:
                    break

                # If it's a connection error, retry
                if "Connection error" in str(result) or "timed out" in str(result):
                    continue
                else:
                    # For other errors, don't retry
                    break

            # Store result
            upload_results.append(
                {
                    "filename": file.name,
                    "success": success,
                    "result": result,
                    "attempts": attempt + 1,
                }
            )

            upload_completed += 1
            upload_queue.task_done()
        except Exception as e:
            # Catch any unexpected errors in the worker thread itself
            upload_results.append(
                {
                    "filename": file_data[0].name if file_data else "Unknown",
                    "success": False,
                    "result": f"Worker thread error: {str(e)}",
                    "attempts": 0,
                }
            )
            upload_completed += 1
            upload_queue.task_done()


# Start worker threads
def start_upload_threads():
    # Create and start worker threads
    threads = []
    for _ in range(NUMBER_OF_WORKER_THREADS):
        t = threading.Thread(target=upload_worker, daemon=True)
        t.start()
        threads.append(t)
    return threads


# Process batch of files
def process_files(files, common_name=None):
    global upload_in_progress, upload_completed, upload_total, upload_results

    # Reset counters
    upload_completed = 0
    upload_total = len(files)
    upload_results = []
    upload_in_progress = True

    # Start worker threads
    threads = start_upload_threads()

    # Add files to queue with a small delay between each file
    for i, file in enumerate(files):
        # Generate custom name if common name is provided
        custom_name = None
        if common_name:
            extension = os.path.splitext(file.name)[1]
            custom_name = f"{common_name}_{i+1}{extension}"

        # Add to queue
        upload_queue.put((file, custom_name))
        # Small delay between queuing files to avoid overwhelming the server
        time.sleep(0.1)

    # Return threads for potential cleanup later
    return threads


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
    st.header("Upload Files")

    # File upload section - Using a more explicit approach for multiple file upload
    st.markdown("### Select multiple files for upload")
    st.markdown(
        "You can select multiple files by holding Ctrl/Cmd while clicking or by dragging over them"
    )
    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        accept_multiple_files=True,
        key="file_uploader",
    )
    # Add a clearer message about multiple file selection
    if not uploaded_files:
        st.info(
            "👆 Please select one or more files to upload. Hold Ctrl/Cmd to select multiple files."
        )

    common_name = st.text_input(
        "Common Base Name (optional)",
        help="If provided, files will be named [base_name]_1, [base_name]_2, etc.",
    )

    if uploaded_files:
        # Display file count more prominently
        st.success(f"**{len(uploaded_files)}** files selected for upload")
        # Show file list in a container
        with st.expander("View selected files", expanded=True):
            for i, file in enumerate(uploaded_files):
                st.write(f"{i+1}. {file.name} ({file.size} bytes)")

        if st.button("Upload Files", key="upload_btn", type="primary"):
            # Start uploading files
            with st.spinner(f"Preparing to upload {len(uploaded_files)} files..."):
                threads = process_files(uploaded_files, common_name)

    # Display upload progress if in progress
    if "upload_in_progress" in globals() and upload_in_progress:
        # Create a progress container that will be updated
        progress_container = st.container()

        with progress_container:
            if upload_total > 0:
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Update progress until complete
                while upload_completed < upload_total:
                    # Calculate progress
                    progress = upload_completed / upload_total
                    progress_bar.progress(progress)
                    status_text.text(
                        f"Uploading: {upload_completed} of {upload_total} completed"
                    )
                    time.sleep(0.1)

                # Final update
                progress_bar.progress(1.0)
                status_text.text(f"Upload complete: {upload_total} files processed")

                # Display results
                st.subheader("Upload Results")
                for result in upload_results:
                    if result["success"]:
                        st.success(f"✅ {result['filename']} uploaded successfully")
                    else:
                        st.error(f"❌ {result['filename']}: {result['result']}")

                # Reset upload state
                upload_in_progress = False

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
