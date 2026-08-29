import aiosqlite
import datetime
from data import COURSE_CURRICULUM

DB_NAME = "database.sqlite"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                role TEXT DEFAULT 'student',
                registered_at TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS lesson_materials (
                module_id TEXT PRIMARY KEY,
                recording_video_id TEXT,
                recording_url TEXT,
                presentation_file_id TEXT,
                presentation_url TEXT,
                cheatsheet_file_id TEXT,
                cheatsheet_text TEXT,
                cheatsheet_url TEXT
            )
        ''')
        
        # Populate defaults from data.py for any missing module
        for mod_id, mod_info in COURSE_CURRICULUM.items():
            lesson = mod_info["lessons"][0] if mod_info.get("lessons") else {}
            async with db.execute('SELECT module_id FROM lesson_materials WHERE module_id = ?', (mod_id,)) as cursor:
                exists = await cursor.fetchone()
            if not exists:
                await db.execute('''
                    INSERT INTO lesson_materials (
                        module_id, recording_video_id, recording_url,
                        presentation_file_id, presentation_url,
                        cheatsheet_file_id, cheatsheet_text, cheatsheet_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mod_id,
                    lesson.get("recording_video_id", ""),
                    lesson.get("recording", ""),
                    lesson.get("presentation_file_id", ""),
                    lesson.get("presentation_url", ""),
                    lesson.get("cheatsheet_file_id", ""),
                    lesson.get("cheatsheet_text", ""),
                    lesson.get("cheatsheet_url", "")
                ))
        await db.commit()

async def get_module_materials(mod_id: str) -> dict:
    """Fetch module materials from DB or fallback to defaults."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM lesson_materials WHERE module_id = ?', (mod_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
    
    # Fallback to data.py defaults
    mod_info = COURSE_CURRICULUM.get(mod_id, {})
    lesson = mod_info["lessons"][0] if mod_info.get("lessons") else {}
    return {
        "module_id": mod_id,
        "recording_video_id": lesson.get("recording_video_id", ""),
        "recording_url": lesson.get("recording", ""),
        "presentation_file_id": lesson.get("presentation_file_id", ""),
        "presentation_url": lesson.get("presentation_url", ""),
        "cheatsheet_file_id": lesson.get("cheatsheet_file_id", ""),
        "cheatsheet_text": lesson.get("cheatsheet_text", ""),
        "cheatsheet_url": lesson.get("cheatsheet_url", "")
    }

async def update_module_material(mod_id: str, field: str, value: str):
    """Update a specific material field for a module."""
    allowed_fields = {
        "recording_video_id", "recording_url",
        "presentation_file_id", "presentation_url",
        "cheatsheet_file_id", "cheatsheet_text", "cheatsheet_url"
    }
    if field not in allowed_fields:
        raise ValueError(f"Field {field} is not allowed")
        
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if exists
        async with db.execute('SELECT module_id FROM lesson_materials WHERE module_id = ?', (mod_id,)) as cursor:
            exists = await cursor.fetchone()
            
        if exists:
            await db.execute(f'UPDATE lesson_materials SET {field} = ? WHERE module_id = ?', (value, mod_id))
        else:
            await db.execute(f'INSERT INTO lesson_materials (module_id, {field}) VALUES (?, ?)', (mod_id, value))
        await db.commit()

async def add_user(telegram_id: int, username: str, first_name: str = "", role: str = 'student') -> bool:
    """Returns True if this is a brand new user, False if already existed."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            existing = await cursor.fetchone()
        if existing:
            return False
        await db.execute('''
            INSERT INTO users (telegram_id, username, first_name, role, registered_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, username, first_name, role, datetime.datetime.now()))
        await db.commit()
        return True

async def log_action(telegram_id: int, action: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO action_logs (telegram_id, action, timestamp)
            VALUES (?, ?, ?)
        ''', (telegram_id, action, datetime.datetime.now()))
        await db.commit()

async def get_user_stats(telegram_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT action, timestamp FROM action_logs WHERE telegram_id = ? ORDER BY timestamp DESC LIMIT 10', (telegram_id,)) as cursor:
            return await cursor.fetchall()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT telegram_id, username, role FROM users') as cursor:
            return await cursor.fetchall()
