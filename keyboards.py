from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data import COURSE_CURRICULUM

def get_student_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )

def get_main_inline_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Материалы", callback_data="menu_materials"),
                InlineKeyboardButton(text="❓ Задать вопрос", callback_data="menu_ask"),
            ],
            [
                InlineKeyboardButton(text="📖 О курсе", callback_data="menu_about"),
                InlineKeyboardButton(text="✍️ Написать Кириллу", callback_data="menu_contact"),
            ],
            [
                InlineKeyboardButton(text="💡 Помощь", callback_data="menu_help"),
            ],
        ]
    )

def get_back_btn():
    """Single back button to return to main menu."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← Главное меню", callback_data="menu_back")]
        ]
    )

def get_materials_inline_kb():
    keys = list(COURSE_CURRICULUM.keys())
    inline_keyboard = []
    for i in range(0, len(keys), 2):
        row = [InlineKeyboardButton(
            text=f"📚 {COURSE_CURRICULUM[keys[i]]['title']}",
            callback_data=keys[i]
        )]
        if i + 1 < len(keys):
            row.append(InlineKeyboardButton(
                text=f"📚 {COURSE_CURRICULUM[keys[i+1]]['title']}",
                callback_data=keys[i+1]
            ))
        inline_keyboard.append(row)
    # Add back button
    inline_keyboard.append([InlineKeyboardButton(text="← Главное меню", callback_data="menu_back")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def get_module_back_kb():
    """Back button after viewing a module."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← К модулям", callback_data="menu_materials")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="menu_back")],
        ]
    )

def get_lesson_menu_kb(mod_id: str):
    """Interactive buttons inside a lesson."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Конспект урока", callback_data=f"lesson_content_{mod_id}")],
            [InlineKeyboardButton(text="🎯 Домашнее задание", callback_data=f"lesson_hw_{mod_id}")],
            [InlineKeyboardButton(text="🤖 Задать вопрос по теме", callback_data=f"lesson_ask_{mod_id}")],
            [
                InlineKeyboardButton(text="← К модулям", callback_data="menu_materials"),
                InlineKeyboardButton(text="🏠 Меню", callback_data="menu_back"),
            ],
        ]
    )

def get_lesson_back_kb(mod_id: str):
    """Back to lesson menu from content/hw view."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="← Назад к уроку", callback_data=f"mod_{mod_id}")],
            [InlineKeyboardButton(text="← К модулям", callback_data="menu_materials")],
        ]
    )

def get_admin_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика учеников"), KeyboardButton(text="📝 Добавить материал")],
            [KeyboardButton(text="📢 Рассылка"), KeyboardButton(text="📚 Режим ученика")]
        ],
        resize_keyboard=True
    )
