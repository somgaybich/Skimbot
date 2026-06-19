import discord
from discord import ApplicationContext

import logging
logger = logging.getLogger(__name__)

class CommandCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    #FIXME: Remove in prod
    async def cog_check(self, ctx: ApplicationContext) -> bool:
        return ctx.interaction.user.id == 247164420273209345

def setup(bot: discord.Bot):
    try:
        logger.info("Registering admin cog")
        bot.add_cog(CommandCog(bot))
        logger.info("Registered admin cog")
    except Exception as e:
        logger.critical(f"Failed to register admin cog: {e}")
        bot.close()
        raise