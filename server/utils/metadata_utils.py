import os, json, tempfile, shutil
from threading import Lock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_FILE = os.path.join(BASE_DIR, "metadata.json")
metadata_lock = Lock()


def load_metadata():
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_metadata(data):
    with metadata_lock:
        tmp = tempfile.NamedTemporaryFile("w", delete=False, dir=os.path.dirname(METADATA_FILE))
        json.dump(data, tmp, indent=2)
        tmp.close()
        shutil.move(tmp.name, METADATA_FILE)
