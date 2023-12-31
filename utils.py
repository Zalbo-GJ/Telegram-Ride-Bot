import json

from aiogram import Bot
from config import TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, BASE_WEBHOOK_URL



async def on_startup(bot: Bot, ) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")



def save_users_to_file(users):
    with open('user_data.json', 'w') as file:
        json.dump(users, file, indent=2)

def save_ongoing_rides_to_file(ongoing_rides):
    with open('ongoing_rides.json', 'w') as file:
        json.dump(ongoing_rides, file, indent=2)


def save_ratings_reviews_history_to_file(ride_history):
    with open('ride_history.json', 'w') as f:
        json.dump(ride_history, f, indent=2)