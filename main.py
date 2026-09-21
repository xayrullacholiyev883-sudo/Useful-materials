import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp import web

# --- SOZLAMALAR ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "8938280108:AAEsADtH0GzJpfelsCPm-f2QpYJMMM998mQ")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8243336938"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- BAZA (Xotirada saqlash) ---
materials_db = {
    "Reading": [], "Writing": [], "Listening": [], "Speaking": [],
    "Vocabulary": [], "Grammar": [], "CEFR": [], "Real Exam": [], "Useful": []
}

# --- FSM (Holatlar) ---
class AdminStates(StatesGroup):
    waiting_for_caption = State()
    waiting_for_file = State()

# --- TUGMALAR ---
def get_main_keyboard(user_id: int):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("📚 Useful Materials"), types.KeyboardButton("ℹ️ About Me"))
    if user_id == ADMIN_ID:
        kb.add(types.KeyboardButton("⚙️ Admin Panel"))
    return kb

def get_categories_keyboard(prefix="cat_"):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat in materials_db.keys():
        text = f"➕ {cat}" if prefix == "admin_" else cat
        kb.add(types.InlineKeyboardButton(text=text, callback_data=f"{prefix}{cat}"))
    return kb

def get_file_type_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text="📄 Fayl qo'shish", callback_data="type_file"),
        types.InlineKeyboardButton(text="🎬 Video qo'shish", callback_data="type_video")
    )
    return kb

# --- WEB SERVER (Render uchun) ---
async def handle(request):
    return web.Response(text="Bot is running live 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# --- HANDLERLAR ---
@dp.message_handler(commands=["start"], state="*")
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Xush kelibsiz! English Materials botiga marhamat.",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

@dp.message_handler(lambda msg: msg.text == "ℹ️ About Me", state="*")
async def about_me(message: types.Message):
    text = (
        "<b>Bot haqida:</b>\n"
        "Ushbu bot ingliz tilini o'rganuvchilar uchun foydali manbalarni ulashish maqsadida yaratilgan.\n\n"
        "Barcha materiallar mualliflik huquqini hurmat qilgan holda, faqat ta'limiy maqsadda taqdim etiladi."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message_handler(lambda msg: msg.text == "📚 Useful Materials", state="*")
async def show_materials(message: types.Message):
    await message.answer("Kerakli bo'limni tanlang:", reply_markup=get_categories_keyboard(prefix="cat_"))

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("cat_"), state="*")
async def process_category_select(callback: types.CallbackQuery):
    cat_name = callback.data.split("cat_")[1]
    items = materials_db.get(cat_name, [])
    if not items:
        await callback.message.answer(f"Hozircha {cat_name} bo'limida materiallar yo'q.")
    else:
        await callback.message.answer(f"<b>{cat_name}</b> bo'limidagi materiallar:", parse_mode="HTML")
        for item in items:
            if item["type"] == "file":
                await callback.message.answer_document(document=item["file_id"], caption=item["caption"])
            elif item["type"] == "video":
                await callback.message.answer_video(video=item["file_id"], caption=item["caption"])
    await callback.answer()

# --- ADMIN PANEL ---
@dp.message_handler(lambda msg: msg.text == "⚙️ Admin Panel", state="*")
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.finish()
    await message.answer("⚙️ <b>Admin Panel:</b> Material qo'shmoqchi bo'lgan bo'limni tanlang:", 
                         reply_markup=get_categories_keyboard(prefix="admin_"), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("admin_"), state="*")
async def admin_cat_click(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_name = callback.data.split("admin_")[1]
    async with state.proxy() as data:
        data["selected_category"] = cat_name
    await callback.message.answer(f"<b>{cat_name}</b> bo'limiga nima qo'shasiz?", reply_markup=get_file_type_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("type_"), state="*")
async def admin_type_click(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    file_type = "file" if callback.data == "type_file" else "video"
    async with state.proxy() as data:
        data["file_type"] = file_type
    
    await callback.message.answer("1-qadam: Material uchun izoh (sarlavha) matnini yuboring:")
    await AdminStates.waiting_for_caption.set()
    await callback.answer()

# 1. Avval izoh matnini qabul qilish
@dp.message_handler(state=AdminStates.waiting_for_caption, content_types=types.ContentTypes.TEXT)
async def process_caption(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    async with state.proxy() as data:
        data["caption_text"] = message.text
        f_type = "faylni (PDF/Doc)" if data.get("file_type") == "file" else "videoni"
    
    await message.answer(f"2-qadam: Endi {f_type} yuboring:")
    await AdminStates.waiting_for_file.set()

# 2. Keyin fayl yoki videoni saqlash
@dp.message_handler(state=AdminStates.waiting_for_file, content_types=[types.ContentType.DOCUMENT, types.ContentType.VIDEO])
async def process_file(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    async with state.proxy() as data:
        cat_name = data.get("selected_category")
        file_type = data.get("file_type")
        caption = data.get("caption_text", "Material")
    
    file_id = message.document.file_id if message.document else message.video.file_id
    
    materials_db[cat_name].append({
        "type": file_type,
        "file_id": file_id,
        "caption": caption
    })
    
    await message.answer("✅ Material muvaffaqiyatli saqlandi!")
    
    if file_type == "file":
        await message.answer_document(document=file_id, caption=caption)
    else:
        await message.answer_video(video=file_id, caption=caption)
        
    await state.finish()

# --- ISHGA TUSHIRISH ---
async def on_startup(dp):
    await start_web_server()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
