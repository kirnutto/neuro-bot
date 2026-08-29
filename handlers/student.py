from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import (
    get_student_main_kb,
    get_materials_inline_kb,
    get_main_inline_kb,
    get_back_btn,
    get_module_back_kb,
    get_lesson_menu_kb,
    get_lesson_back_kb
)
from database import add_user, log_action, get_module_materials
from data import COURSE_CURRICULUM
from ai_helper import get_ai_response

router = Router()

# ───────────────────────── ОНБОРДИНГ / СТАРТ ─────────────────────────

ONBOARDING_TEXT = (
    "Привет, {name}! 👋\n\n"
    "Я — *AI-Ментор* курса *«AIO: AI-видео с нуля до профи»*.\n"
    "Твой преподаватель: *Кирилл Орещенко*.\n\n"
    "📚 *Материалы* — все 8 модулей курса\n"
    "❓ *Задать вопрос* — спроси что угодно по курсу\n"
    "📖 *О курсе* — программа и инструменты\n"
    "✍️ *Написать Кириллу* — прямая связь\n"
    "💡 *Помощь* — как пользоваться ботом\n\n"
    "👇 Выбери, с чего начать:"
)

class StudentState(StatesGroup):
    waiting_for_question = State()

MENU_BUTTONS = {"🏠 Главное меню"}

async def safe_edit_or_send(callback: CallbackQuery, text: str, reply_markup=None):
    """Safely edit message if it's text, or send a new message if previous was a file/video."""
    try:
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)

@router.message(Command("start"), StateFilter("*"))
@router.message(F.text == "🏠 Главное меню", StateFilter("*"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user = message.from_user
    is_new = await add_user(user.id, user.username, user.first_name)
    await log_action(user.id, "started_bot")

    # Notify admin about new user
    if is_new:
        from config import ADMIN_ID
        if ADMIN_ID:
            username_str = f"@{user.username}" if user.username else "без username"
            profile_link = f"tg://user?id={user.id}"
            await message.bot.send_message(
                ADMIN_ID,
                f"🆕 *Новый пользователь бота!*\n\n"
                f"👤 Имя: [{user.full_name}]({profile_link})\n"
                f"📎 Telegram: {username_str}\n"
                f"🆔 ID: `{user.id}`",
                parse_mode="Markdown"
            )

    # Delete user's message to keep chat clean
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer(
        ONBOARDING_TEXT.format(name=user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_inline_kb()
    )

# ───────────────────────── INLINE-КНОПКИ ГЛАВНОГО МЕНЮ ─────────────────────────

@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await safe_edit_or_send(
        callback,
        ONBOARDING_TEXT.format(name=callback.from_user.first_name),
        reply_markup=get_main_inline_kb()
    )

@router.callback_query(F.data == "menu_materials")
async def inline_materials(callback: CallbackQuery):
    await callback.answer()
    await safe_edit_or_send(
        callback,
        "📚 *Материалы курса*\n\nВыбери модуль, который хочешь изучить 👇",
        reply_markup=get_materials_inline_kb()
    )

@router.callback_query(F.data == "menu_ask")
async def inline_ask(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await safe_edit_or_send(
        callback,
        "🤖 *Режим вопросов активирован!*\n\n"
        "Спрашивай про курс, инструменты или работу с нейросетями. "
        "Я помню весь наш разговор, так что можно задавать вопросы по цепочке.\n\n"
        "_Например:_\n"
        "— «С чего начать работу над мультфильмом?»\n"
        "— «Как составить промпт для Kling Motion?»\n"
        "— «Как исправить деформацию рук на видео?»\n\n"
        "Напиши свой вопрос прямо сейчас ✍️\n"
        "Чтобы выйти — нажми кнопку ниже 👇",
        reply_markup=get_back_btn()
    )
    await state.set_state(StudentState.waiting_for_question)

@router.callback_query(F.data == "menu_about")
async def inline_about(callback: CallbackQuery):
    await callback.answer()
    await safe_edit_or_send(
        callback,
        "🎬 *AIO: AI-видео с нуля до профи*\n\n"
        "Практический курс из *8 индивидуальных занятий* по 2 часа.\n\n"
        "После курса ты самостоятельно умеешь:\n"
        "✅ Создавать постоянных персонажей с нейросетью\n"
        "✅ Оживлять фотографии и персонажей\n"
        "✅ Делать AI-аватары для соцсетей\n"
        "✅ Создавать мультфильмы в разных стилях\n"
        "✅ Снимать реалистичные кино-сцены\n"
        "✅ Монтировать всё в готовый ролик\n\n"
        "🛠 *Инструменты курса:*\n"
        "• ChatGPT\n"
        "• Kling Motion\n"
        "• HeyGen\n"
        "• Seedance 2.5\n"
        "• Видеоредактор\n\n"
        "Всё обучение проходит *с телефона*, без сложных терминов. "
        "Только реальные проекты для соцсетей. 🚀",
        reply_markup=get_back_btn()
    )

@router.callback_query(F.data == "menu_contact")
async def inline_contact(callback: CallbackQuery):
    await callback.answer()
    await safe_edit_or_send(
        callback,
        "✍️ *Написать Кириллу напрямую:*\n\n"
        "➡️ @OrKIIg4781\n\n"
        "Он всегда на связи между занятиями 😊",
        reply_markup=get_back_btn()
    )

@router.callback_query(F.data == "menu_help")
async def inline_help(callback: CallbackQuery):
    await callback.answer()
    await safe_edit_or_send(
        callback,
        "💡 *Как пользоваться ботом?*\n\n"
        "📚 *Материалы* — нажми и выбери нужный модуль. "
        "Там описание урока.\n\n"
        "❓ *Задать вопрос* — нажми и просто напиши вопрос. "
        "Бот помнит весь разговор, можно спрашивать по цепочке:\n"
        "_«Как создать паспорт персонажа?»_\n"
        "_«А референс-лист — это что?»_\n"
        "_«Дай пример промпта для Kling Motion»_\n\n"
        "📖 *О курсе* — описание программы и инструментов.\n\n"
        "✍️ *Написать Кириллу* — ссылка на преподавателя.\n\n"
        "Если бот завис — нажми *🏠 Главное меню* внизу или /start.",
        reply_markup=get_back_btn()
    )

# ───────────────────────── МАТЕРИАЛЫ — МОДУЛИ ─────────────────────────

@router.callback_query(F.data.startswith("mod_"))
async def module_callback(callback: CallbackQuery):
    mod_id = callback.data
    await log_action(callback.from_user.id, f"viewed_module_{mod_id}")

    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    # Show module overview + interactive buttons
    lessons_list = "\n".join(
        f"🔹 {lesson['title']}" for lesson in mod_data["lessons"]
    )
    text = (
        f"📖 *{mod_data['title']}*\n\n"
        f"_{mod_data['description']}_\n\n"
        f"*Уроки:*\n{lessons_list}\n\n"
        f"👇 Выбери, что хочешь открыть:"
    )

    await safe_edit_or_send(
        callback,
        text,
        reply_markup=get_lesson_menu_kb(mod_id)
    )
    await callback.answer()

# ───────────────────────── КНОПКИ ВНУТРИ УРОКА ─────────────────────────

@router.callback_query(F.data.startswith("lesson_record_"))
async def lesson_record(callback: CallbackQuery):
    mod_id = callback.data.replace("lesson_record_", "")
    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    materials = await get_module_materials(mod_id)
    video_id = materials.get("recording_video_id")
    record_url = materials.get("recording_url")

    if video_id:
        await callback.message.answer_video(
            video=video_id,
            caption=f"🎥 *Запись урока — {mod_data['title']}*",
            parse_mode="Markdown",
            reply_markup=get_lesson_menu_kb(mod_id)
        )
        await callback.answer("Запись урока отправлена!")
        return

    if record_url:
        text = f"🎥 *Запись урока — {mod_data['title']}*\n\n🔗 [Смотреть запись урока]({record_url})"
    else:
        text = f"🎥 *{mod_data['title']}*\n\nЗапись урока пока не загружена или появится позже. 📌"

    await safe_edit_or_send(
        callback,
        text,
        reply_markup=get_lesson_menu_kb(mod_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lesson_pres_"))
async def lesson_pres(callback: CallbackQuery):
    mod_id = callback.data.replace("lesson_pres_", "")
    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    materials = await get_module_materials(mod_id)
    pres_file_id = materials.get("presentation_file_id")
    pres_url = materials.get("presentation_url")

    if pres_file_id:
        await callback.message.answer_document(
            document=pres_file_id,
            caption=f"📊 Презентация к модулю: *{mod_data['title']}*",
            parse_mode="Markdown",
            reply_markup=get_lesson_menu_kb(mod_id)
        )
        await callback.answer("Презентация отправлена!")
        return
    elif pres_url:
        text = f"📊 *Презентация — {mod_data['title']}*\n\n🔗 [Открыть презентацию]({pres_url})"
    else:
        text = f"📊 *{mod_data['title']}*\n\nПрезентация к этому уроку пока не загружена. 📌"

    await safe_edit_or_send(
        callback,
        text,
        reply_markup=get_lesson_menu_kb(mod_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lesson_cheat_"))
async def lesson_cheat(callback: CallbackQuery):
    mod_id = callback.data.replace("lesson_cheat_", "")
    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    materials = await get_module_materials(mod_id)
    cheat_file_id = materials.get("cheatsheet_file_id")
    cheat_text = materials.get("cheatsheet_text")
    cheat_url = materials.get("cheatsheet_url")

    if cheat_file_id:
        await callback.message.answer_document(
            document=cheat_file_id,
            caption=f"📌 Шпаргалка к модулю: *{mod_data['title']}*",
            parse_mode="Markdown",
            reply_markup=get_lesson_menu_kb(mod_id)
        )
        await callback.answer("Шпаргалка отправлена!")
        return
    elif cheat_text:
        text = f"📌 *Шпаргалка — {mod_data['title']}*\n\n{cheat_text}"
        if len(text) > 4000:
            text = text[:3990] + "\n\n_...продолжение_"
    elif cheat_url:
        text = f"📌 *Шпаргалка — {mod_data['title']}*\n\n🔗 [Открыть шпаргалку]({cheat_url})"
    else:
        text = f"📌 *{mod_data['title']}*\n\nШпаргалка к этому уроку скоро появится. 📌"

    await safe_edit_or_send(
        callback,
        text,
        reply_markup=get_lesson_menu_kb(mod_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lesson_hw_"))
async def lesson_hw(callback: CallbackQuery):
    mod_id = callback.data.replace("lesson_hw_", "")
    mod_data = COURSE_CURRICULUM.get(mod_id)
    if not mod_data:
        await callback.answer("Модуль не найден.")
        return

    hw_list = []
    for lesson in mod_data["lessons"]:
        if lesson.get("homework"):
            hw_list.append(f"*{lesson['title']}*\n{lesson['homework']}")

    if hw_list:
        text = f"🎯 *Домашнее задание — {mod_data['title']}*\n\n" + "\n\n".join(hw_list)
    else:
        text = f"🎯 *{mod_data['title']}*\n\nДомашнее задание будет добавлено преподавателем после занятия. 📌"

    if len(text) > 4000:
        text = text[:3990] + "\n\n_...продолжение_ 📌"

    await safe_edit_or_send(
        callback,
        text,
        reply_markup=get_lesson_menu_kb(mod_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lesson_ask_"))
async def lesson_ask(callback: CallbackQuery, state: FSMContext):
    mod_id = callback.data.replace("lesson_ask_", "")
    mod_data = COURSE_CURRICULUM.get(mod_id)
    mod_title = mod_data['title'] if mod_data else "урок"

    await state.set_state(StudentState.waiting_for_question)
    await safe_edit_or_send(
        callback,
        f"🤖 *Вопрос по теме: {mod_title}*\n\n"
        f"Задавай любой вопрос по этому уроку — я отвечу с учётом контекста курса.\n\n"
        f"✍️ Напиши свой вопрос прямо сейчас:",
        reply_markup=get_lesson_back_kb(mod_id)
    )
    await callback.answer()

# ───────────────────────── AI-ЧАТ ─────────────────────────

@router.message(F.text == "📚 Материалы")
async def materials_menu(message: Message):
    await log_action(message.from_user.id, "opened_materials")
    try:
        await message.delete()
    except Exception:
        pass
    await message.answer(
        "📚 *Материалы курса*\n\nВыбери модуль, который хочешь изучить 👇",
        parse_mode="Markdown",
        reply_markup=get_materials_inline_kb()
    )

@router.message(StudentState.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    user_question = message.text

    if user_question in MENU_BUTTONS:
        await state.clear()
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(
            ONBOARDING_TEXT.format(name=message.from_user.first_name),
            parse_mode="Markdown",
            reply_markup=get_main_inline_kb()
        )
        return

    processing_msg = await message.answer("🤖 Думаю над ответом...")

    ai_answer = await get_ai_response(user_question, message.from_user.first_name, message.from_user.id)

    if ai_answer.startswith("Произошла ошибка"):
        from config import ADMIN_ID
        if ADMIN_ID:
            await message.bot.send_message(
                ADMIN_ID,
                f"❓ Вопрос от {message.from_user.first_name} (@{message.from_user.username}):\n\n{user_question}"
            )
        await processing_msg.edit_text(
            "Произошла ошибка при обращении к нейросети. Я передал твой вопрос напрямую Кириллу!"
        )
    else:
        await processing_msg.edit_text(ai_answer, parse_mode="Markdown")

    await log_action(message.from_user.id, "received_ai_answer")
