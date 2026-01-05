
import json
from app.config import settings

config_data = {
    "X_CLIENT_ID": settings.X_CLIENT_ID,
    "X_CLIENT_SECRET": settings.X_CLIENT_SECRET,
    "FRONTEND_URL": settings.FRONTEND_URL,
    "DATABASE_URL": settings.DATABASE_URL,
    "SECRET_KEY": settings.SECRET_KEY,
}

with open("config_debug.json", "w") as f:
    json.dump(config_data, f, indent=4)

print("Config written to config_debug.json")
