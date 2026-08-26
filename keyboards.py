from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_student_main_kb():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Материалы"), KeyboardButton(text="❓ Задать вопрос")],
            [KeyboardButton(text="📖 О курсе"), KeyboardButton(text="✍️ Написать Кириллу")],
            [KeyboardButton(text="💡 Помощь"), KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    return kb

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

def get_admin_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Статистика учеников"), KeyboardButton(text="📝 Добавить материал")],
            [KeyboardButton(text="📢 Рассылка"), KeyboardButton(text="📚 Режим ученика")]
        ],
        resize_keyboard=True
    )

from data import COURSE_CURRICULUM

def get_materials_inline_kb():
    # Split into rows of 2
    keys = list(COURSE_CURRICULUM.keys())
    inline_keyboard = []
    for i in range(0, len(keys), 2):
        row = []
        mod1 = keys[i]
        row.append(InlineKeyboardButton(text=f"📚 {COURSE_CURRICULUM[mod1]['title']}", callback_data=mod1))
        
        if i + 1 < len(keys):
            mod2 = keys[i+1]
            row.append(InlineKeyboardButton(text=f"📚 {COURSE_CURRICULUM[mod2]['title']}", callback_data=mod2))
        inline_keyboard.append(row)
        
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
