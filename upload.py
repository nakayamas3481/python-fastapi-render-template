import os

UPLOAD_DIR = "uploads"
def upload_file(buceket_name, path, contents, content_type):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, path)
    with open(file_path, 'wb') as f:
        f.write(contents)
    return f"/{UPLOAD_DIR}/{path}"