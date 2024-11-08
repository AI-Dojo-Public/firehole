import os


DEBUG = False if os.getenv("FIREHOLE_DEBUG", "false").lower() == "false" else True
