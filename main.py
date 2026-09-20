import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# O'zingizning bot tokeningizni yozing
API_TOKEN = "8938280108:AAEkHbfii44vTJlvIR9rhfeoEZ9oA-4Hr04"

# O'zingizning Telegram ID raqamingizni yozing (Faqat siz admin bo'lasiz)
ADMIN_ID = 8243336938  # O'z ID raqamingiz bilan almashtiring!

# Sizning Telegram username'ingiz (Bog'lanish uchun)
MY_TELEGRAM = "@narzullayevich_2010"

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Har bir bo'lim uchun ro'yxat (Bir nechta fayl saqlash uchun)
materials = {
    "📖 Reading": [],
    "🎧 Listening": [],
    "📚 Grammar": [],
    "🗣 Speaking": [],
    "✍️ Writing": [],
    "🧠 Vocabulary": [],
    "🎯 CEFR / Multilevel": [],
    "📑 Real exam's materials": [],
    "📂 Useful Materials": []
}

class AdminStates(StatesGroup):
    waiting_for_material = State()

# --- RENDER PORT SERVERI ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# --------------------------

# Asosiy menyu
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📖 Reading"),
        types.KeyboardButton("🎧 Listening"),
        types.KeyboardButton("📚 Grammar"),
        types.KeyboardButton("🗣 Speaking"),
        types.KeyboardButton("✍️ Writing"),
        types.KeyboardButton("🧠 Vocabulary"),
        types.KeyboardButton("🎯 CEFR / Multilevel"),
        types.KeyboardButton("📑 Real exam's materials"),
        types.KeyboardButton("📂 Useful Materials"),
        types.KeyboardButton("ℹ️ About Me"),
        types.KeyboardButton("📞 Biz bilan bog'lanish")
    )
    await message.reply("Assalomu alaykum! English Materials botimizga xush kelibsiz. Kerakli bo'limni tanlang:", reply_markup=markup)

# About Me bo'limi
@dp.message_handler(lambda message: message.text == "ℹ️ About Me")
async def about_me(message: types.Message):
    text = (
        "ℹ️ **About Me**\n\n"
        "Ushbu bot ingliz tilini o'rganuvchilar uchun barcha kerakli materiallarni jamlash maqsadida yaratilgan.\n\n"
        f"Loyiha muallifi / Admin: "@narzullayevich_2010"
    )
    await message.reply(text, parse_mode="Markdown")

# Biz bilan bog'lanish bo'limi
@dp.message_handler(lambda message: message.text == "📞 Biz bilan bog'lanish")
async def contact_us(message: types.Message):
    text = (
        "📞 **Biz bilan bog'lanish**\n\n"
        "Savollar, takliflar yoki reklama bo'yicha murojaat qilish uchun quyidagi manzilga yozishingiz mumkin:\n\n"
        f"👉 Admin bilan bog'lanish: @narzullayevich_2010"
    )
    await message.reply(text, parse_mode="Markdown")

# Foydalanuvchi bo'limni bosganda saqlangan BARCHA materiallarni chiqarish
@dp.message_handler(lambda message: message.text in materials.keys())
async def show_materials(message: types.Message):
    section = message.text
    items = materials[section]
    
    if not items:
        await message.reply(f"Hozircha <b>{section}</b> bo'limiga ma'lumot qo'shilmagan. Tez orada qo'shiladi!", parse_mode="HTML")
        return
    
    await message.reply(f"📂 <b>{section}</b> bo'limidagi materiallar:", parse_mode="HTML")
    
    for item in items:
        file_id = item['file_id']
        file_type = item['type']
        caption = item['caption']
        
        if file_type == 'document':
            await bot.send_document(message.chat.id, file_id, caption=caption)
        elif file_type == 'video':
            await bot.send_video(message.chat.id, file_id, caption=caption)
        elif file_type == 'photo':
            await bot.send_photo(message.chat.id, file_id, caption=caption)

# --- ADMIN PANEL ---

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("Siz bu buyruqdan foydalana olmaysiz!")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for section in materials.keys():
        markup.add(types.InlineKeyboardButton(f"{section}ga qo'shish", callback_data=f"add_{section}"))
        
    await message.reply("Salom Admin! Qaysi bo'limga material qo'shmoqchisiz?", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith('add_'))
async def process_callback_admin(callback_query: types.CallbackQuery, state: FSMContext):
    section = callback_query.data.replace('add_', '')
    
    async with state.proxy() as data:
        data['section'] = section
        
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id, 
        f"<b>{section}</b> uchun fayl, video yoki rasm yuboring.\n<i>(Pastiga o'z izohingizni va muallifni yozib yuborishingiz mumkin)</i>", 
        parse_mode="HTML"
    )
    await AdminStates.waiting_for_material.set()

@dp.message_handler(state=AdminStates.waiting_for_material, content_types=['document', 'video', 'photo'])
async def save_material(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        section = data['section']
        
    caption = message.caption or ""
    
    if message.document:
        materials[section].append({'file_id': message.document.file_id, 'type': 'document', 'caption': caption})
    elif message.video:
        materials[section].append({'file_id': message.video.file_id, 'type': 'video', 'caption': caption})
    elif message.photo:
        materials[section].append({'file_id': message.photo[-1].file_id, 'type': 'photo', 'caption': caption})
    
    count = len(materials[section])
    await message.reply(f"Muvaffaqiyatli qo'shildi! Hozirda '{section}' bo'limida jami {count} ta material bor.")
    await state.finish()

if __name__ == "__main__":
    print("Bot ishga tushmoqda...")
    executor.start_polling(dp, skip_updates=True)

