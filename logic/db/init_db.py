import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from datetime import datetime

from logic.db.config import MONGO_URI, DB_NAME, COLLECTION_NAME


async def init_db():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]

        # Проверяем, существует ли коллекция
        existing_collections = await db.list_collection_names()
        if COLLECTION_NAME not in existing_collections:
            print(f"Создаём коллекцию {COLLECTION_NAME}...")

            # Создаём индексы для быстрого поиска
            await db[COLLECTION_NAME].create_indexes([
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("deadline_date", ASCENDING)]),
                IndexModel([("is_completed", ASCENDING)])
            ])

            # Пример тестовой задачи (можно удалить)
            sample_task = {
                "user_id": 123456789,
                "text": "Купить молоко",
                "deadline_date": "2025-02-25",
                "deadline_time": "15:00",
                "is_completed": False,
                "reminder_date": "2025-02-25",
                "reminder_time": "14:30",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db[COLLECTION_NAME].insert_one(sample_task)
            print("Тестовая задача добавлена.")

        else:
            print(f"Коллекция {COLLECTION_NAME} уже существует => БД существует")
    except Exception as e:
        logging.error(f"Ошибка при подключении или работе с базой данных: {e}")
        print("Произошла ошибка при работе с базой данных. Проверьте логи.")

    finally:
        # Закрытие соединения (не обязательно, но хорошая практика)
        client.close()
