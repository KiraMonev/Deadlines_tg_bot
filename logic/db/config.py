import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "task_planner"
COLLECTION_NAME = "tasks"
