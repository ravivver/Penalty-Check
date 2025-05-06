import os
from dotenv import load_dotenv
import discord

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

def setup_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = discord.Client(intents=intents)
    return bot