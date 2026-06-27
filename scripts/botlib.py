import logging
import discord
import time
from discord.ext import tasks

logger = logging.getLogger(__name__)

from scripts.database import init_db, save_message, get_db

class SkimBot(discord.Bot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        kwargs.setdefault("intents", intents)
        super().__init__(**kwargs)

    async def on_ready(self):
        timer = time.perf_counter()
        await init_db()
        logger.debug(f"Took {(timer / 1000000):.2f}ms to set up commands")
        timer = time.perf_counter()
        self.load_extension("commands")
        await sync(self)
        logger.debug(f"Took {(timer / 1000000):.2f}ms to set up commands")
        logger.info("Setup complete!")
    
    async def on_message(self, message):
        await save_message(message)

    @tasks.loop(minutes=5)
    async def db_commit(self):
        logger.info("Committing database...")
        try:
            await get_db().commit()
            logger.info("Committed all database changes")
        except RuntimeError:
            # This is raised on startup because the initial database commit always fails
            logger.debug("Initial commit failed, this is expected behavior")
        except Exception as e:
            logger.error(f"Unable to commit database: {e}")
            raise

bot = SkimBot()

async def sync(bot: SkimBot) -> None:
    """
    Sync application commands with Discord.
    """
    logger.info("Syncing commands")
    await bot.sync_commands()