import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TOKEN, WEB_SERVER_HOST, WEB_SERVER_PORT, WEBHOOK_PATH, BASE_WEBHOOK_URL
from handlers import register_handlers
from utils import on_startup

def main() -> None:
    bot = Bot(TOKEN)
    dp = Dispatcher()
    router = Router()
    dp.include_router(router)
    register_handlers(router, bot)

    dp.startup.register(on_startup)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

async def log():
    bot = Bot(TOKEN)
    await bot.delete_webhook()
    dp = Dispatcher()
    router = Router()
    dp.include_router(router)
    register_handlers(router, bot)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    # main()
    
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(log())