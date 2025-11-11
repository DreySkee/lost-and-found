import os, json, tempfile, shutil
from threading import Lock

metadata_lock = Lock()

def get_metadata_file_path():
    """Get the metadata file path"""
    # Check for persistent disk path (Render)
    persistent_disk = os.getenv("RENDER_PERSISTENT_DISK_PATH", "/opt/render/project/src")
    
    if os.path.exists(persistent_disk):
        # Use persistent disk for metadata
        metadata_folder = persistent_disk
    else:
        # Fall back to local storage
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        metadata_folder = BASE_DIR
    
    return os.path.join(metadata_folder, "metadata.json")


def load_metadata():
    metadata_file = get_metadata_file_path()
    if not os.path.exists(metadata_file):
        return []
    with open(metadata_file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_metadata(data):
    metadata_file = get_metadata_file_path()
    metadata_dir = os.path.dirname(metadata_file)
    os.makedirs(metadata_dir, exist_ok=True)
    
    with metadata_lock:
        tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=metadata_dir)
        json.dump(data, tmp, indent=2)
        tmp.close()
        shutil.move(tmp.name, metadata_file)
