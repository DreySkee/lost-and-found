"""
Storage utility for handling file uploads
Supports both local filesystem and persistent disk on Render
"""
import os

def get_upload_folder(base_dir=None) -> str:
    """Get the upload folder path, using persistent disk if available"""
    # Check for persistent disk path (Render)
    # Render mounts persistent disks at /opt/render/project/src
    persistent_disk = os.getenv("RENDER_PERSISTENT_DISK_PATH", "/opt/render/project/src")
    
    if os.path.exists(persistent_disk):
        # Use persistent disk for uploads
        upload_folder = os.path.join(persistent_disk, "uploads")
    else:
        # Fall back to local storage
        if base_dir:
            upload_folder = os.path.join(base_dir, "uploads")
        else:
            # Calculate base_dir relative to this file
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_folder = os.path.join(BASE_DIR, "server", "uploads")
    
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_metadata_folder(base_dir=None) -> str:
    """Get the metadata folder path, using persistent disk if available"""
    # Check for persistent disk path (Render)
    persistent_disk = os.getenv("RENDER_PERSISTENT_DISK_PATH", "/opt/render/project/src")
    
    if os.path.exists(persistent_disk):
        # Use persistent disk for metadata
        return persistent_disk
    else:
        # Fall back to local storage
        if base_dir:
            return base_dir
        else:
            # Calculate base_dir relative to this file
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            return os.path.join(BASE_DIR, "server")

