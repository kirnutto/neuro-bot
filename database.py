import aiosqlite
import datetime

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
        await db.commit()

async def add_user(telegram_id: int, username: str, first_name: str = "", role: str = 'student') -> bool:
    """Returns True if this is a brand new user, False if already existed."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if user already exists
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
