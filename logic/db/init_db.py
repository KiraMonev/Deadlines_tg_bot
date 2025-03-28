import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, IndexModel

from logic.db.config import COLLECTION_NAME, DB_NAME, MONGO_URI


async def init_db():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]

        existing_collections = await db.list_collection_names()
        if COLLECTION_NAME not in existing_collections:
            logging.info(f"Создаём коллекцию {COLLECTION_NAME}...")

            await db[COLLECTION_NAME].create_indexes([
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("deadline_date", ASCENDING)]),
                IndexModel([("is_completed", ASCENDING)])
            ])

        else:
            logging.info(f"База данных уже существует")
    except Exception as e:
        logging.error(f"Ошибка при подключении или работе с базой данных: {e}")
        print("Произошла ошибка при работе с базой данных. Проверьте логи.")

    finally:
        client.close()
