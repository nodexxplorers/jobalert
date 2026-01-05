
import os

env_path = ".env"
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    clean_lines = []
    for line in lines:
        # Strip trailing \r and \n, then add a clean \n
        clean_line = line.strip("\r\n").strip() 
        if clean_line:
            clean_lines.append(clean_line + "\n")
    
    with open(env_path, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(clean_lines)
    print("Sanitized .env file (removed all carriage returns and extra whitespace).")
else:
    print(".env file not found.")
