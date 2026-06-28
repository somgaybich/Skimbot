import discord
from discord import ApplicationContext
from scripts.database import (save_message, get_all_messages, 
                              get_messages_channel, get_messages_user)
from scripts.response import (followup_response, followup_error, 
                              interaction_response)
from scripts.constants import banned_words, banned_channels
import re
from wordfreq import zipf_frequency
from math import log2

import logging
logger = logging.getLogger(__name__)

class CommandCog(discord.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(description="Get help on the bot.")
    @discord.option("item", input_type=int, choices=[
        discord.OptionChoice(name="general", value=0, description="What is skimbot?"),
        discord.OptionChoice(name="scrape", value=1),
        discord.OptionChoice(name="analyze", value=2)
    ])
    async def help(self, ctx: ApplicationContext, item: int):
        match item:
            case 0:
                await interaction_response(
                    interaction=ctx.interaction,
                    title="Skimbot",
                    message="Skimbot allows your members to perform word " \
                    "frequency analysis on their own messages.\nIt does this by " \
                    "collecting the content and some basic data about each " \
                    "message and storing it in a local database (nothing " \
                    "identifying!)\n\nGet started by using /scrape, then anyone" \
                    "can use /analyze to see their stats.",
                    footer="If you're a nerd and you're curious how skimbot " \
                    "works, visit the [repo](https://github.com/somgaybich/Skimbot)"
                )
            case 1:
                await interaction_response(
                    interaction=ctx.interaction,
                    title="Scrape",
                    message="Scrape allows skimbot to collect data about " \
                    "messages sent before it was added to the server. For very " \
                    "large servers with lots of message history, it may take " \
                    "several hours.",
                    footer="Your message data is securely stored in a database " \
                    "that cannot be accessed from the internet."
                )
            case 2:
                await interaction_response(
                    interaction=ctx.interaction,
                    title="Analyze",
                    message="Analyze creates a little profile of your stats. " \
                    "It includes your top channels by message count, and your " \
                    "top words, calculated by how frequently you say them " \
                    "compared to a general sample. More data is coming in the " \
                    "future!",
                    footer="General sample data comes from the " \
                    "[Exquisite Corpus](https://github.com/LuminosoInsight/exquisite-corpus)"
                )

    @discord.slash_command(description="""Load this server's messages into the bot's memory.""")
    @discord.default_permissions(administrator=True)
    async def scrape(self, ctx: ApplicationContext):
        total_count = 0
        try:
            await ctx.interaction.response.defer()
            logger.info(f"Starting scrape in '{ctx.interaction.guild.name}'")
            
            guild = ctx.interaction.guild
            for channel in guild.text_channels:
                print(f"Checking messages for {channel.name}...")
            
                channel_count = 0
                async for message in channel.history(limit=None):
                    await save_message(message)
                    total_count += 1
                    channel_count += 1
                    if channel_count % 100 == 0:
                        print(f"{channel_count} messages scraped")

                print(f"Found {channel_count} messages.")
                print(f"{total_count} messages found in total.")
        
        except Exception as e:
            print(f"Error scraping: {e}")
            raise

        print(f"Retrieved {total_count} messages.")
        await followup_response(
            followup=ctx.followup, 
            title="Scrape complete!",
            message=f"I collected data for {total_count} messages in this server!")
    
    @discord.slash_command(description="""Run analysis on your messages in this server and create a simple report.""")
    async def analyze(self, ctx: ApplicationContext):
        await ctx.interaction.response.defer()
        
        result_str = ""
        try:
            count = 0
            word_freq = {}
            channel_freq = {}
            
            for message in await get_messages_user(
                ctx.author.id, 
                ctx.interaction.guild.id
            ):
                text: str = message['content']
                channel_name: str = message['channel']

                if channel_name in banned_channels:
                    continue
                if "http://" in text or "https://" in text:
                    continue
                
                pattern = r'<[@#&]!??\d+>|<a?:\w+:\d+>|\b\w+\b'
                words = re.findall(pattern, text.lower())

                for word in words:
                    if len(word) <= 1 and word not in ["i", "a"]:
                        continue
                    if word in banned_words:
                        continue
                    if "@" in word or "#" in word or ":" in word:
                        continue

                    if word in word_freq.keys():
                        word_freq[word] += 1
                    else:
                        word_freq[word] = 1

                if channel_name in channel_freq.keys():
                    channel_freq[channel_name] += 1
                else:
                    channel_freq[channel_name] = 1

                count += 1
            
            top_channels = sorted(
                channel_freq,
                key=channel_freq.get,
                reverse=True
            )[0:5]

            data = {}
            length = sum(word_freq.values())
            for word in word_freq:
                expected = 10**(zipf_frequency(word, 'en') - 9)
                observed = word_freq[word] / length
                score = log2(observed / expected)
                data.update({word: score})

            top_words = sorted(
                data,
                key=data.get,
                reverse=True
            )[0:5]

            result_str += "\n**__Your top words:__**\n"
            for word in top_words:
                result_str += f"- **'{word}'**: said {word_freq[word]} times\n"

            result_str += "**__Your top channels:__**\n"
            for channel in top_channels:
                result_str += f"- #{channel}: sent {channel_freq[channel]} messages\n"
        except Exception as e:
            logger.error(f"Failed to analyze messages for '{ctx.author.name}': {e}")
            await followup_error(ctx.followup)

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