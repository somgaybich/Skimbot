import discord
from discord import ApplicationContext
from scripts.database import (save_message, get_all_messages, 
                              get_messages_channel, get_messages_user)
from scripts.response import followup_response

import logging
logger = logging.getLogger(__name__)

class CommandCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    #FIXME: Remove in prod
    async def cog_check(self, ctx: ApplicationContext) -> bool:
        return ctx.interaction.user.id == 247164420273209345

    @discord.slash_command(description="""Load this server's messages into the
                            the bot's memory.""")
    @discord.default_permissions(administrator=True)
    async def scrape(self, ctx: ApplicationContext):
        count = 0
        try:
            await ctx.interaction.response.defer()
            logger.info(f"Starting scrape in '{ctx.interaction.guild.name}'")
            guild = ctx.interaction.channel
            async for message in guild.history(limit=None):
                await save_message(message)
                count += 1
                if count % 100 == 0:
                    print(f"{count} messages scraped")
        
        except Exception as e:
            print(f"Error scraping: {e}")
            raise

        print(f"Retrieved {count} messages.")
        await followup_response(
            followup=ctx.followup, 
            title="Scrape complete!",
            message=f"I collected data for {count} messages in this server!")
        
def setup(bot: discord.Bot):
    try:
        logger.info("Registering command cog")
        bot.add_cog(CommandCog(bot))
        logger.info("Registered command cog")
    except Exception as e:
        logger.critical(f"Failed to register admin cog: {e}")
        bot.close()
        raise