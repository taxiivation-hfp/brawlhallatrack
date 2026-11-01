import discord
from discord.ext import commands
from discord.ext import tasks
import logging 
from dotenv import load_dotenv
import os
import aiohttp
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready to track!')
    leaderboard_activity.start()

previous_username_rating = None
changed_username_rating = []

message = None


@tasks.loop(seconds=60)
async def leaderboard_activity():
    global previous_username_rating
    global changed_username_rating
    global message
    activity_message = "No activity"
    changed_username_rating = []
    leaderboard = await scrape_leaderboard()
    username_rating = {}
    for page in leaderboard:
        for player in page['rankings']:
            username_rating[player['players'][0]["id"]] = player['players'][0]["username"], player['rating']

    if message is None:
        channel = bot.get_channel(1566446074262982716)
        message = await channel.send(activity_message)

    if previous_username_rating is not None:
        for id in username_rating:
            if id in previous_username_rating:
                if username_rating[id][1] != previous_username_rating[id][1]:
                    changed_username_rating.append((username_rating[id][0], username_rating[id][1] - previous_username_rating[id][1], username_rating[id][1]))
    
    activity_message = ""
    for player in changed_username_rating:
        activity_message += f"\n{player}"
    if not activity_message:
        activity_message = "No activity"

    await message.edit(content=activity_message)

    previous_username_rating = username_rating

async def scrape_leaderboard():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.brawlhalla.com/v1/leaderboard/ranked", params={"game_mode" : "1v1", "region" : "AUS", "max_results" : 50}) as response:
            print(response.status)
            top50 = await response.json()
        async with session.get("https://api.brawlhalla.com/v1/leaderboard/ranked", params={"game_mode" : "1v1", "region" : "AUS", "max_results" : 50, "page" : 2}) as response:
            print(response.status)
            top51_100 = await response.json()
    return top50, top51_100

def elo_difference():
    pass

# print("dan")
# print(asyncio.run(scrape_leaderboard()))

bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG) 

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if "taxivation" in message.content.lower():
#         await message.channel.send("taxiivation*")

#     await bot.process_commands(message)