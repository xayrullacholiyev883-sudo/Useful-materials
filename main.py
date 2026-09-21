import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiohttp import web

# --- SOZLAMALAR ---
BOT_TOKEN = "8938280108:AAEfLcyHub_hokl3LS7KM_hujT8ZrWTD-t0"
ADMIN_ID = 8243336938
ADMIN_USERNAME = "@narzullayevich_2010"
STORAGE_CHANNEL_ID = -1003662758278  # Doimiy saqlash uchun yopiq kanal ID raqami

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Ma'lumotlarni saqlash uchun fayl nomi
DB_FILE = "materials_db.json"

# Boshlang'ich baza strukturasi
default_db = {
    "Reading": [],
    "Writing": [],
    "Listening": [],
    "Speaking": [],
    "Vocabulary": [],
    "Grammar": [],
    "CEFR": [],
    "Real Exam": [],
    "Useful": []
}

# Bazani yuklash funksiyasi
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("db", default_db), data.get("counter", 0)
        except:
            return default_db, 0
    return default_db, 0

# Bazani saqlash funksiyasi
def save_db():
    data = {
        "db": materials_db,
        "counter": item_counter
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

materials_db, item_counter = load_db()
CATEGORIES = list(materials_db.keys())

# --- FSM (Holatlar) ---
class AdminStates(StatesGroup):
    waiting_for_caption = State()
    waiting_for_file = State()

# --- TUGMALAR ---
def get_main_keyboard(user_id: int):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row(types.KeyboardButton("📚 Useful Materials"), types.KeyboardButton("ℹ️ About Me"))
    kb.row(types.KeyboardButton("📞 Biz bilan bog'lanish"))
    if user_id == ADMIN_ID:
        kb.add(types.KeyboardButton("⚙️ Admin Panel"))
    return kb

def get_categories_keyboard(prefix="cat_"):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat in CATEGORIES:
        text = f"➕ {cat}" if prefix == "admin_" else cat
        kb.add(types.InlineKeyboardButton(text=text, callback_data=f"{prefix}{cat}"))
    return kb

def get_admin_action_keyboard(cat_name: str):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text="📄 Fayl qo'shish", callback_data="type_file"),
        types.InlineKeyboardButton(text="🎬 Video qo'shish", callback_data="type_video")
    )
    kb.add(types.InlineKeyboardButton(text="🗑 Fayllarni bittalab o'chirish", callback_data=f"list_delete_{cat_name}"))
    return kb

# --- WEB SERVER (Render uchun) ---
async def handle(request):
    return web.Response(text="Bot is running live 24/7 with Persistent Storage!")

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

@dp.message_handler(lambda msg: msg.text == "📞 Biz bilan bog'lanish", state="*")
async def contact_us(message: types.Message):
    text = (
        "<b>📞 Biz bilan bog'lanish:</b>\n\n"
        "Savollaringiz, takliflaringiz yoki reklama masalalari bo'yicha admin bilan bog'lanishingiz mumkin:\n\n"
        f"👨‍💻 <b>Admin:</b> {ADMIN_USERNAME}"
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
            if item["file_type"] == "file":
                await callback.message.answer_document(document=item["file_id"], caption=item["caption"])
            elif item["file_type"] == "video":
                await callback.message.answer_video(video=item["file_id"], caption=item["caption"])
    await callback.answer()

# --- ADMIN PANEL ---
@dp.message_handler(lambda msg: msg.text == "⚙️ Admin Panel", state="*")
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.finish()
    await message.answer("⚙️ <b>Admin Panel:</b> Kerakli bo'limni tanlang:", 
                         reply_markup=get_categories_keyboard(prefix="admin_"), parse_mode="HTML")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith("admin_"), state="*")
async def admin_cat_click(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_name = callback.data.split("admin_")[1]
    async with state.proxy() as data:
        data["selected_category"] = cat_name
    await callback.message.answer(f"<b>{cat_name}</b> bo'limi bo'yicha amalni tanlang:", reply_markup=get_admin_action_keyboard(cat_name), parse_mode="HTML")
    await callback.answer()

# --- BITTALAB O'CHIRISH RO'YXATI ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("list_delete_"), state="*")
async def list_files_for_delete(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    cat_name = callback.data.split("list_delete_")[1]
    items = materials_db.get(cat_name, [])
    
    if not items:
        await callback.message.answer(f"<b>{cat_name}</b> bo'limida o'chirish uchun fayllar yo'q.", parse_mode="HTML")
    else:
        await callback.message.answer(f"🗑 <b>{cat_name}</b> bo'limidagi fayllar ro'yxati:", parse_mode="HTML")
        for item in items:
            del_kb = types.InlineKeyboardMarkup()
            del_kb.add(types.InlineKeyboardButton(text="❌ Ushbu faylni o'chirish", callback_data=f"del_{item['id']}"))
            
            if item["file_type"] == "file":
                await callback.message.answer_document(document=item["file_id"], caption=item["caption"], reply_markup=del_kb)
            elif item["file_type"] == "video":
                await callback.message.answer_video(video=item["file_id"], caption=item["caption"], reply_markup=del_kb)
    await callback.answer()

# --- FAYLNI O'CHIRISH HANDLERI ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith("del_"), state="*")
async def delete_single_file(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    target_id = int(callback.data.split("del_")[1])
    
    deleted = False
    for cat in materials_db:
        for item in materials_db[cat]:
            if item["id"] == target_id:
                try:
                    await bot.delete_message(chat_id=STORAGE_CHANNEL_ID, message_id=item["message_id"])
                except:
                    pass
                materials_db[cat].remove(item)
                save_db()
                deleted = True
                break
        if deleted:
            break
            
    if deleted:
        await callback.message.answer("✅ Fayl kanal va botdan muvaffaqiyatli o'chirildi!", parse_mode="HTML")
    else:
        await callback.message.answer("⚠️ Fayl topilmadi.", parse_mode="HTML")
        
    await callback.message.delete()
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

@dp.message_handler(state=AdminStates.waiting_for_caption, content_types=types.ContentTypes.TEXT)
async def process_caption(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    async with state.proxy() as data:
        data["caption_text"] = message.text
        f_type = "faylni (PDF/Doc)" if data.get("file_type") == "file" else "videoni"
    
    await message.answer(f"2-qadam: Endi {f_type} yuboring:")
    await AdminStates.waiting_for_file.set()

@dp.message_handler(state=AdminStates.waiting_for_file, content_types=[types.ContentType.DOCUMENT, types.ContentType.VIDEO])
async def process_file(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    
    global item_counter
    async with state.proxy() as data:
        cat_name = data.get("selected_category")
        file_type = data.get("file_type")
        caption = data.get("caption_text", "Material")
    
    file_id = message.document.file_id if message.document else message.video.file_id
    
    try:
        if file_type == "file":
            sent_msg = await bot.send_document(chat_id=STORAGE_CHANNEL_ID, document=file_id, caption=f"[{cat_name}] {caption}")
        else:
            sent_msg = await bot.send_video(chat_id=STORAGE_CHANNEL_ID, video=file_id, caption=f"[{cat_name}] {caption}")
        
        item_counter += 1
        materials_db[cat_name].append({
            "id": item_counter,
            "file_type": file_type,
            "file_id": file_id,
            "caption": caption,
            "message_id": sent_msg.message_id
        })
        
        save_db()
        
        await message.answer("✅ Material yopiq kanalga va botga muvaffaqiyatli saqlandi!")
        
        if file_type == "file":
            await message.answer_document(document=file_id, caption=caption)
        else:
            await message.answer_video(video=file_id, caption=caption)
            
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: Bot kanalga admin qilinganligini va huquqlari to'g'riligini tekshiring.\nXatolik: {e}")
        
    await state.finish()

# --- ISHGA TUSHIRISH ---
async def on_startup(dp):
    await start_web_server()

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
