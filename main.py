import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Tokeningizni qo'shtirnoq ichiga yozing
API_TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04"

# Render uchun oddiy veb-server (port talabini bajarish uchun)
async def handle(request):
    return web.Response(text="Bot is alive and running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.message(lambda message: message.text == "/start")
    async def command_start_handler(message: types.Message) -> None:
        await message.answer("Assalomu alaykum! Bot 24/7 rejimda muvaffaqiyatli ishga tushdi! 🚀")

    # Veb-server va botni bir vaqtda ishga tushiramiz
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
