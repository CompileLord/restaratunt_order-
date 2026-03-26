import os
import shutil
from uuid import uuid4

def save_images(upload_file) -> str:
    upload_dir = "static/images"
    os.makedirs(upload_dir, exist_ok=True)

    ext = upload_file.filename.split(".")[-1]
    filename = f"{uuid4()}.{ext}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return f"static/images/{filename}"

