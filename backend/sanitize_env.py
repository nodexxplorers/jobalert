
import os

env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, "rb") as f:
        content = f.read()
    
    # Remove \r (carriage return) characters
    clean_content = content.replace(b"\r", b"")
    
    if clean_content != content:
        with open(env_path, "wb") as f:
            f.write(clean_content)
        print("Sanitized .env file (removed carriage returns).")
    else:
        print(".env file was already clean.")
else:
    print(".env file not found.")





