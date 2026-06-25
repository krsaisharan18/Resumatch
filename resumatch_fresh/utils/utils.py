import os, json, tempfile
from pathlib import Path

def save_upload(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.read())
    tmp.close()
    return tmp.name

def pretty_json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
