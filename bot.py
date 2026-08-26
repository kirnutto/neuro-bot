import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import student, admin
from aiohttp import web

logging.basicConfig(level=logging.INFO)

async def handle_ping(request):
    return web.Response(text="Bot is running! AI-Mentor active.")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render assigns a dynamic port via the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Dummy web server started on port {port}")

async def main():
    if BOT_TOKEN == "YOUR_TOKEN_HERE" or not BOT_TOKEN:
        logging.error("Пожалуйста, укажите BOT_TOKEN в файле .env")
        return

    # Initialize DB (it will recreate itself on Render restarts, which is safe)
    await init_db()

    # Start dummy web server so Render thinks the app is healthy
    await start_dummy_server()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register routers
    dp.include_router(admin.router)
    dp.include_router(student.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
