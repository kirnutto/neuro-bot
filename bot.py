import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import init_db
from handlers import student, admin
from aiohttp import web, ClientSession

logging.basicConfig(level=logging.INFO)

async def handle_ping(request):
    return web.Response(text="Bot is running! AI-Mentor active.")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    app.router.add_get('/ping', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def self_ping_loop():
    """Ping ourselves every 14 minutes to prevent Render from sleeping."""
    # Render automatically sets this variable
    url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not url:
        logging.info("RENDER_EXTERNAL_URL not set, self-ping disabled (running locally).")
        return
    ping_url = f"{url}/ping"
    await asyncio.sleep(60)  # Wait 1 minute after startup before first ping
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(ping_url, timeout=10) as resp:
                    logging.info(f"Self-ping OK: {resp.status}")
        except Exception as e:
            logging.warning(f"Self-ping failed: {e}")
        await asyncio.sleep(14 * 60)  # Every 14 minutes

async def main():
    if BOT_TOKEN == "YOUR_TOKEN_HERE" or not BOT_TOKEN:
        logging.error("Пожалуйста, укажите BOT_TOKEN в файле .env")
        return

    await init_db()
    await start_dummy_server()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(admin.router)
    dp.include_router(student.router)

    # Start self-ping in background
    asyncio.create_task(self_ping_loop())

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
