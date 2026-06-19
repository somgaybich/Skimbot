import logging
import discord
import time

logger = logging.getLogger(__name__)

from scripts.constants import OPGUILD_ID
from scripts.database import init_db, save_message

class SkimBot(discord.Bot):
    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        kwargs.setdefault("intents", discord.Intents.default())
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

bot = SkimBot()

async def sync(bot: SkimBot) -> None:
    """
    Sync application commands with Discord.
    """
    logger.info("Syncing commands")
    await bot.sync_commands(guild_ids=[OPGUILD_ID])