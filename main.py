importimport os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, executor


API_TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- RENDER UCHUN VEB SERVER (PORT OCHISH) ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Veb-serverni orqa fonda (thread) ishga tushiramiz
threading.Thread(target=run_server, daemon=True).start()
# ---------------------------------------------

# Oddiy /start buyrug'i uchun misol handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Assalomu alaykum! Botimiz 24/7 rejimda muvaffaqiyatli ishga tushdi! 🚀")

if __name__ == "__main__":
    print("Bot tayyor va ishga tushmoqda...")
    executor.start_polling(dp, skip_updates=True)
