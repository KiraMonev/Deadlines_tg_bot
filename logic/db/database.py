from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from logic.db.config import COLLECTION_NAME, DB_NAME, MONGO_URI


class Database:
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def add_task(self, user_id: int, text: str, deadline_date: str, deadline_time: str, reminder_date: str,
                       reminder_time: str):
        task = {
            "user_id": user_id,
            "text": text,
            "deadline_date": deadline_date,
            "deadline_time": deadline_time,
            "is_completed": False,
            "reminder_date": reminder_date,
            "reminder_time": reminder_time,
            "created_at": datetime.now(timezone.utc)+timedelta(hours=3),
            "updated_at": datetime.now(timezone.utc)+timedelta(hours=3)
        }
        return await self.collection.insert_one(task)

    async def update_task(self, task_id, update_data: dict):
        update_data["updated_at"] = datetime.now(timezone.utc) + timedelta(hours=3)
        return await self.collection.update_one({"_id": task_id}, {"$set": update_data})

    async def update_task_details(
            self, task_id, new_text: str = None,
            new_deadline_date: str = None, new_deadline_time: str = None,
            reminder_date: str = None, reminder_time: str = None
    ):
        update_data = {}
        if new_text:
            update_data["text"] = new_text
        if new_deadline_date:
            update_data["deadline_date"] = new_deadline_date
        if new_deadline_time:
            update_data["deadline_time"] = new_deadline_time
        if reminder_date:
            update_data["reminder_date"] = reminder_date
        if reminder_time:
            update_data["reminder_time"] = reminder_time

        if update_data:
            await self.update_task(task_id, update_data)

    async def mark_task_completed(self, task_id):
        return await self.update_task(task_id, {"is_completed": True})

    async def delete_task(self, task_id):
        return await self.collection.delete_one({"_id": task_id})

    async def delete_tasks_by_date(self, user_id: int, date: str):
        return await self.collection.delete_many({"user_id": user_id, "deadline_date": date})

    async def get_tasks(self, user_id: int):
        tasks = await self.collection.find({"user_id": user_id}).sort(
            [("deadline_date", 1), ("created_at", 1)]).to_list(length=None)
        return tasks

    async def get_task(self, object_id: str):
        task = await self.collection.find_one({"_id": object_id})
        return task

    async def get_tasks_with_reminders_date_and_time(self):
        now = datetime.now(timezone.utc) + timedelta(hours=3)
        now_date = now.strftime("%d.%m.%Y")
        now_time = now.strftime("%H:%M")
        tasks = await self.collection.find({"reminder_date": {"$eq": now_date},
                                            "reminder_time": {"$eq": now_time},
                                            "is_completed": False}).to_list()
        return tasks

    async def get_overdue_tasks(self):
        now = datetime.now(timezone.utc) + timedelta(hours=3)
        now_date = now.strftime("%d.%m.%Y")
        now_time = now.strftime("%H:%M")
        tasks = await self.collection.find({"deadline_date": {"$eq": now_date},
                                            "deadline_time": {"$eq": now_time},
                                            "is_completed": False}).to_list()
        return tasks

    async def close(self):
        self.client.close()


db = Database(MONGO_URI, DB_NAME, COLLECTION_NAME)
