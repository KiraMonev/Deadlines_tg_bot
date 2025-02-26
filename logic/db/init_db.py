import logging
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, IndexModel

from logic.db.config import COLLECTION_NAME, DB_NAME, MONGO_URI


async def init_db():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]

        # Проверяем, существует ли коллекция
        existing_collections = await db.list_collection_names()
        if COLLECTION_NAME not in existing_collections:
            logging.info(f"Создаём коллекцию {COLLECTION_NAME}...")

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
            logging.info("Тестовая задача добавлена.")

        else:
            logging.info(f"Коллекция {COLLECTION_NAME} уже существует => БД существует")
    except Exception as e:
        logging.error(f"Ошибка при подключении или работе с базой данных: {e}")
        print("Произошла ошибка при работе с базой данных. Проверьте логи.")

    finally:
        # Закрытие соединения (не обязательно, но хорошая практика)
        client.close()
