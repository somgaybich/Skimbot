from typing import Optional
import aiosqlite
import logging
from discord import Message

logger = logging.getLogger(__name__)

_db: Optional[aiosqlite.Connection] = None

async def init_db(file: str = "data/data.db"):
    """
    Creates a new database connection.

    :param file: Path from the root to the database file.
    :type file: str
    """
    logger.info("Starting database connection")
    global _db
    if _db is not None:
        logger.warning("Tried to start database connection when there was already one initialized")
        return
    
    _db = await aiosqlite.connect(file)
    await _db.execute("PRAGMA foreign_keys = ON;")
    _db.row_factory = aiosqlite.Row

    await _db.execute(
    """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        user INTEGER,
        channel TEXT)
    """)
    logger.debug("Created messages table")

async def close_db():
    global _db
    if _db is not None:
        await _db.close()
        _db = None

def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

# ------------------------------

async def save_message(message: Message):
    logger.debug(f"Saving message at id '{message.id}'")
    await get_db().execute(
        """
        INSERT INTO messages (
            id, content, user, channel
        )
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        (message.id, message.content, message.author.id, message.channel.name)
    )

async def get_all_messages():
    async with get_db().execute("SELECT * FROM messages") as cursor:
        return await cursor.fetchall()

async def message_count():
    async with get_db().execute(
        "SELECT COUNT(*) FROM messages"
    ) as cursor:
        return await cursor.fetchall()

async def get_messages_channel(channel_id: int):
    async with get_db().execute(
        "SELECT * FROM messages WHERE channel = ?",
        (channel_id,)
    ) as cursor:
        return await cursor.fetchall()

async def message_count_channel(channel_id: int):
    async with get_db().execute(
        "SELECT COUNT(*) FROM messages WHERE channel = ?",
        (channel_id,)
    ) as cursor:
        return await cursor.fetchall()
    
async def get_messages_user(user_id: int):
    async with get_db().execute(
        "SELECT * FROM messages WHERE user = ?",
        (user_id,)
    ) as cursor:
        return await cursor.fetchall()
    
async def message_count_user(user_id: int):
    async with get_db().execute(
        "SELECT COUNT(*) FROM messages WHERE user = ?",
        (user_id,)
    ) as cursor:
        return await cursor.fetchall()
