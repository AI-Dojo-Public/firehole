import os


DEBUG = True if os.getenv("FIREHOLE_DEBUG", "false").lower() == "true" else False
