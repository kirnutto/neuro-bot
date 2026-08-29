from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from keyboards import (
    get_admin_main_kb,
    get_student_main_kb,
    get_admin_materials_kb,
    get_admin_module_edit_kb,
    get_admin_cancel_kb
)
from database import (
    get_all_users,
    get_user_stats,
    get_module_materials,
    update_module_material
)
from data import COURSE_CURRICULUM

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

class AdminMaterialsState(StatesGroup):
    waiting_for_video = State()
    waiting_for_pres = State()
    waiting_for_cheat = State()

async def format_admin_module_card(mod_id: str) -> str:
    mod_data = COURSE_CURRICULUM.get(mod_id, {})
    title = mod_data.get("title", mod_id)
    materials = await get_module_materials(mod_id)
    
    # Video status
    if materials.get("recording_video_id"):
        video_status = "✅ Загружено видеофайлом"
    elif materials.get("recording_url"):
        video_status = f"🔗 Ссылка: {materials['recording_url']}"
    else:
        video_status = "❌ Не загружено"
        
    # Pres status
    if materials.get("presentation_file_id"):
        pres_status = "✅ Загружен файл презентации"
    elif materials.get("presentation_url"):
        pres_status = f"🔗 Ссылка: {materials['presentation_url']}"
    else:
        pres_status = "❌ Не загружена"
        
    # Cheat status
    if materials.get("cheatsheet_file_id"):
        cheat_status = "✅ Загружен файл шпаргалки"
    elif materials.get("cheatsheet_text"):
        preview = materials['cheatsheet_text'][:40].replace('\n', ' ')
        cheat_status = f"📝 Текст: {preview}..."
    elif materials.get("cheatsheet_url"):
        cheat_status = f"🔗 Ссылка: {materials['cheatsheet_url']}"
    else:
        cheat_status = "❌ Не загружена"
        
    text = (
        f"⚙️ *Управление материалами*\n\n"
        f"📖 *{title}*\n\n"
        f"🎥 *Запись урока:* {video_status}\n"
        f"📊 *Презентация:* {pres_status}\n"
        f"📌 *Шпаргалка:* {cheat_status}\n\n"
        f"👇 Выберите, что хотите обновить:"
    )
    return text

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("👑 *Панель администратора*", parse_mode="Markdown", reply_markup=get_admin_main_kb())

@router.message(F.text == "📊 Статистика учеников")
async def stats_menu(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    users = await get_all_users()
    if not users:
        await message.answer("Учеников пока нет.")
        return

    text = "👥 *Список учеников:*\n"
    for u in users:
        text += f"- {u[1] or 'без юзернейма'} (ID: `{u[0]}`)\n"
    
    first_user_id = users[0][0]
    stats = await get_user_stats(first_user_id)
    
    text += f"\n*Последние действия первого ученика ({first_user_id}):*\n"
    for action, timestamp in stats:
        text += f"- {action} в {timestamp}\n"
        
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📚 Режим ученика")
async def student_mode(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer("Переключаю в режим ученика.", reply_markup=get_student_main_kb())

# ───────────────────────── УПРАВЛЕНИЕ МАТЕРИАЛАМИ (АДМИН) ─────────────────────────

@router.message(F.text.in_({"🎬 Управление материалами", "📝 Добавить материал", "Добавить материал", "Управление материалами"}))
async def admin_materials_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        "🎬 *Управление материалами курса*\n\n"
        "Выберите модуль, материалы которого хотите обновить или проверить 👇",
        parse_mode="Markdown",
        reply_markup=get_admin_materials_kb()
    )

@router.callback_query(F.data == "admin_modules_list")
async def admin_modules_list(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.answer()
    try:
        await callback.message.edit_text(
            "🎬 *Управление материалами курса*\n\n"
            "Выберите модуль, материалы которого хотите обновить или проверить 👇",
            parse_mode="Markdown",
            reply_markup=get_admin_materials_kb()
        )
    except Exception:
        await callback.message.answer(
            "🎬 *Управление материалами курса*\n\n"
            "Выберите модуль, материалы которого хотите обновить или проверить 👇",
            parse_mode="Markdown",
            reply_markup=get_admin_materials_kb()
        )

@router.callback_query(F.data.startswith("admin_select_mod_"))
async def admin_select_module(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    mod_id = callback.data.replace("admin_select_mod_", "")
    await callback.answer()
    
    text = await format_admin_module_card(mod_id)
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_module_edit_kb(mod_id))
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_admin_module_edit_kb(mod_id))

@router.callback_query(F.data.startswith("admin_edit_video_"))
async def admin_edit_video(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    mod_id = callback.data.replace("admin_edit_video_", "")
    await state.set_state(AdminMaterialsState.waiting_for_video)
    await state.update_data(mod_id=mod_id)
    await callback.answer()
    
    mod_title = COURSE_CURRICULUM.get(mod_id, {}).get("title", mod_id)
    text = (
        f"🎥 *Обновление записи: {mod_title}*\n\n"
        f"Отправьте **видеофайл** прямо в этот чат или отправьте **текстовую ссылку на видео** (YouTube, Rutube, Google Диск):"
    )
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))

@router.callback_query(F.data.startswith("admin_edit_pres_"))
async def admin_edit_pres(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    mod_id = callback.data.replace("admin_edit_pres_", "")
    await state.set_state(AdminMaterialsState.waiting_for_pres)
    await state.update_data(mod_id=mod_id)
    await callback.answer()
    
    mod_title = COURSE_CURRICULUM.get(mod_id, {}).get("title", mod_id)
    text = (
        f"📊 *Обновление презентации: {mod_title}*\n\n"
        f"Отправьте **файл презентации** (PDF или PPTX) или отправьте **ссылку на презентацию**:"
    )
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))

@router.callback_query(F.data.startswith("admin_edit_cheat_"))
async def admin_edit_cheat(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    mod_id = callback.data.replace("admin_edit_cheat_", "")
    await state.set_state(AdminMaterialsState.waiting_for_cheat)
    await state.update_data(mod_id=mod_id)
    await callback.answer()
    
    mod_title = COURSE_CURRICULUM.get(mod_id, {}).get("title", mod_id)
    text = (
        f"📌 *Обновление шпаргалки: {mod_title}*\n\n"
        f"Отправьте **документ/фотографию** шпаргалки, отправьте **ссылку** или просто напишите **текст шпаргалки** сюда в чат:"
    )
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=get_admin_cancel_kb(mod_id))

# ───────────────────────── ОБРАБОТКА ВХОДЯЩИХ МАТЕРИАЛОВ В СОСТОЯНИЯХ ─────────────────────────

@router.message(AdminMaterialsState.waiting_for_video)
async def process_admin_video(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    mod_id = data.get("mod_id")
    if not mod_id:
        await state.clear()
        return

    if message.video:
        file_id = message.video.file_id
        await update_module_material(mod_id, "recording_video_id", file_id)
        await update_module_material(mod_id, "recording_url", "")
        await message.answer("✅ *Видеофайл успешно прикреплен к уроку!*", parse_mode="Markdown")
    elif message.document:
        file_id = message.document.file_id
        await update_module_material(mod_id, "recording_video_id", file_id)
        await update_module_material(mod_id, "recording_url", "")
        await message.answer("✅ *Видеофайл (документ) успешно прикреплен к уроку!*", parse_mode="Markdown")
    elif message.text:
        url = message.text.strip()
        await update_module_material(mod_id, "recording_url", url)
        await update_module_material(mod_id, "recording_video_id", "")
        await message.answer(f"✅ *Ссылка на видео успешно сохранена:*\n{url}", parse_mode="Markdown")
    else:
        await message.answer("Пожалуйста, отправьте видеофайл или текстовую ссылку.")
        return

    await state.clear()
    card_text = await format_admin_module_card(mod_id)
    await message.answer(card_text, parse_mode="Markdown", reply_markup=get_admin_module_edit_kb(mod_id))

@router.message(AdminMaterialsState.waiting_for_pres)
async def process_admin_pres(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    mod_id = data.get("mod_id")
    if not mod_id:
        await state.clear()
        return

    if message.document:
        file_id = message.document.file_id
        await update_module_material(mod_id, "presentation_file_id", file_id)
        await update_module_material(mod_id, "presentation_url", "")
        await message.answer("✅ *Файл презентации успешно прикреплен к уроку!*", parse_mode="Markdown")
    elif message.text:
        url = message.text.strip()
        await update_module_material(mod_id, "presentation_url", url)
        await update_module_material(mod_id, "presentation_file_id", "")
        await message.answer(f"✅ *Ссылка на презентацию сохранена:*\n{url}", parse_mode="Markdown")
    else:
        await message.answer("Пожалуйста, отправьте файл презентации (документ) или ссылку.")
        return

    await state.clear()
    card_text = await format_admin_module_card(mod_id)
    await message.answer(card_text, parse_mode="Markdown", reply_markup=get_admin_module_edit_kb(mod_id))

@router.message(AdminMaterialsState.waiting_for_cheat)
async def process_admin_cheat(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    mod_id = data.get("mod_id")
    if not mod_id:
        await state.clear()
        return

    if message.document:
        file_id = message.document.file_id
        await update_module_material(mod_id, "cheatsheet_file_id", file_id)
        await update_module_material(mod_id, "cheatsheet_text", "")
        await update_module_material(mod_id, "cheatsheet_url", "")
        await message.answer("✅ *Файл шпаргалки успешно прикреплен!*", parse_mode="Markdown")
    elif message.photo:
        file_id = message.photo[-1].file_id
        await update_module_material(mod_id, "cheatsheet_file_id", file_id)
        await update_module_material(mod_id, "cheatsheet_text", "")
        await update_module_material(mod_id, "cheatsheet_url", "")
        await message.answer("✅ *Изображение шпаргалки успешно прикреплено!*", parse_mode="Markdown")
    elif message.text:
        text = message.text.strip()
        if text.startswith("http://") or text.startswith("https://"):
            await update_module_material(mod_id, "cheatsheet_url", text)
            await update_module_material(mod_id, "cheatsheet_text", "")
            await update_module_material(mod_id, "cheatsheet_file_id", "")
            await message.answer(f"✅ *Ссылка на шпаргалку сохранена:*\n{text}", parse_mode="Markdown")
        else:
            await update_module_material(mod_id, "cheatsheet_text", text)
            await update_module_material(mod_id, "cheatsheet_file_id", "")
            await update_module_material(mod_id, "cheatsheet_url", "")
            await message.answer("✅ *Текст шпаргалки успешно сохранен!*", parse_mode="Markdown")
    else:
        await message.answer("Пожалуйста, отправьте файл, фото или текст шпаргалки.")
        return

    await state.clear()
    card_text = await format_admin_module_card(mod_id)
    await message.answer(card_text, parse_mode="Markdown", reply_markup=get_admin_module_edit_kb(mod_id))

