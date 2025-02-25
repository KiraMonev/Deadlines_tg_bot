import json

with open("settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

BOT_API_TOKEN = str(settings['BotSettings']['api_key'])
BOT_NAME = str(settings['BotSettings']['bot_name'])
