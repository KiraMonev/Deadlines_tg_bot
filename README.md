# Deadlines_tg_bot

## Запуск проекта

1. Создайте в корне проекта файл `settings.json` и добавьте в него следующие данные:

   {
     "BotSettings": {
       "api_key": "ваш токен",
       "bot_name": "bot"
     }
   }
   
2. Запустите контейнер с помощью Docker:
   docker-compose up --build
