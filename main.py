import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

API_TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04",

# Veb-server (Render port talabini bajarish uchun)
async def handle(request):
    return web.Response(text="Bot is alive!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.message(lambda message: message.text == "/start")
    async def command_start_handler(message: types.Message) -> None:
        await message.answer("Assalomu alaykum! Bot 24/7 ishlamoqda 🚀")

    # Veb-server va botni birgalikda ishga tushiramiz
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
