import logging
from datetime import datetime, timedelta

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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return await self.collection.insert_one(task)

    async def update_task(self, task_id, update_data: dict):
        update_data["updated_at"] = datetime.utcnow()
        return await self.collection.update_one({"_id": task_id}, {"$set": update_data})

    async def update_task_details(self, task_id, new_text: str = None, new_deadline_date: str = None,
                                  new_deadline_time: str = None):
        update_data = {}
        if new_text:
            update_data["text"] = new_text
        if new_deadline_date:
            update_data["deadline_date"] = new_deadline_date
        if new_deadline_time:
            update_data["deadline_time"] = new_deadline_time

        if update_data:
            await self.update_task(task_id, update_data)

    async def mark_task_completed(self, task_id):
        return await self.update_task(task_id, {"is_completed": True})

    async def delete_task(self, task_id):
        return await self.collection.delete_one({"_id": task_id})

    async def delete_tasks_by_date(self, user_id: int, date: str):
        return await self.collection.delete_many({"user_id": user_id, "deadline_date": date})

    async def get_tasks(self, user_id: int):
        tasks = await self.collection.find({"user_id": user_id}).to_list(length=None)
        return tasks

    # Получить список невыполненных задач пользователя, у которых срок выполнения не истёк.
    async def get_pending_tasks(self, user_id: int):
        now = datetime.utcnow().strftime("%Y-%m-%d")
        tasks = await self.collection.find(
            {"user_id": user_id, "deadline_date": {"$gte": now}, "is_completed": False}).to_list(length=None)
        return tasks

    async def set_task_reminder(self, task_id, reminder_date: str, reminder_time: str):
        return await self.update_task(task_id, {"reminder_date": reminder_date, "reminder_time": reminder_time})

    async def get_tasks_with_reminders(self):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        tasks = await self.collection.find({"reminder_date": {"$lte": now}, "is_completed": False}).to_list(length=None)
        return tasks

    async def prolong_overdue_tasks(self):
        now = datetime.utcnow().strftime("%Y-%m-%d")
        # потом поиграемся со временем
        overdue_tasks = await self.collection.find({"deadline_date": {"$lt": now}, "is_completed": False}).to_list(
            length=None)
        for task in overdue_tasks:
            new_deadline = datetime.strptime(task["deadline_date"], "%Y-%m-%d") + timedelta(days=1)
            await self.update_task(task["_id"], {"deadline_date": new_deadline.strftime("%Y-%m-%d")})
            logging.info(f"Продлили задачу {task['_id']} до {new_deadline.strftime('%Y-%m-%d')}")
            # надо добавить информацию о продлении пользователю

    async def close(self):
        self.client.close()


db = Database(MONGO_URI, DB_NAME, COLLECTION_NAME)
