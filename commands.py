import discord
from discord import ApplicationContext
from scripts.database import (save_message, get_all_messages, 
                              get_messages_channel, get_messages_user)
from scripts.response import followup_response
from scripts.constants import banned_words, banned_channels
import re
from wordfreq import zipf_frequency

import logging
logger = logging.getLogger(__name__)

class CommandCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    #FIXME: Remove in prod
    async def cog_check(self, ctx: ApplicationContext) -> bool:
        return ctx.interaction.user.id == 247164420273209345

    @discord.slash_command(description="""Load this server's messages into the bot's memory.""")
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
    
    @discord.slash_command(description="""Run analysis on your messages in this server and create a simple report.""")
    async def analyze(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()
        count = 0
        word_freq = {}
        channel_freq = {}
        
        for message in await get_messages_user(ctx.author.id):
            if channel_name in banned_channels:
                continue
            
            count += 1
            
            text: str = message['content']
            channel_name: str = message['channel']
            pattern = r'<[@#&]!??\d+>|<a?:\w+:\d+>|\b\w+\b'
            words = re.findall(pattern, text.lower())

            for word in words:
                if len(word) <= 1 and word not in ["i", "a"]:
                    continue
                if word in banned_words:
                    continue

                if word in word_freq.keys():
                    word_freq[word] += 1
                else:
                    word_freq[word] = 1

            if channel_name in channel_freq.keys():
                channel_freq[channel_name] += 1
            else:
                channel_freq[channel_name] = 1
        
        top_channels = sorted(
            channel_freq,
            key=channel_freq.get,
            reverse=True
        )[0:5]

        data = {}
        length = sum(word_freq.values())
        for word in word_freq:
            freq_general = zipf_frequency(word, 'en')
            freq_dataset = word_freq[word] / length
            diff = freq_dataset - 10**(freq_general - 9)
            data.update({word: diff})

        top_words = sorted(
            data,
            key=data.get,
            reverse=True
        )[0:5]

        result_str = "\n**__Your top words:__**\n"
        for word in top_words:
            result_str += f"- **'{word}'**: said {word_freq[word]} times\n"

        result_str += "**__Your top channels:__**\n"
        for channel in top_channels:
            result_str += f"- #{channel}: sent {channel_freq[channel]} messages\n"

        await followup_response(
            followup=ctx.followup,
            title="Your results",
            message=result_str,
            footer="Top words found by comparison with the Exquisite Corpus."
        )

def setup(bot: discord.Bot):
    try:
        logger.info("Registering command cog")
        bot.add_cog(CommandCog(bot))
        logger.info("Registered command cog")
    except Exception as e:
        logger.critical(f"Failed to register admin cog: {e}")
        bot.close()
        raise