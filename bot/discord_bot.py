import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def send_to_discord(sale):
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    steam_image_base = "https://steamcommunity.com/economy/image/"

    if channel:
        embed = discord.Embed(
            title=f"🛒 New: {sale.get('marketHashName', 'Unknown skin')}",
            description=f"Price: {sale.get('salePrice', 'Unknown')} {sale.get('currency', '')}",
            color=discord.Color.green()
        )
        image_url = steam_image_base + sale.get('image', '')
        embed.set_thumbnail(url=image_url)
        embed.add_field(name="Exterior", value=sale.get('exterior', 'Unknown'), inline=True)
        embed.add_field(name="Wear", value=sale.get('wear', 'Unknown'), inline=True)
        embed.add_field(name="Pattern", value=sale.get('pattern', 'Unknown'), inline=True)
        embed.add_field(name="Stattrak", value=sale.get('stattrak', 'Unknown'), inline=True)
        embed.add_field(name="Inspect", value=f"[Picture]({image_url})", inline=True)
        embed.add_field(name="Link", value=f"[Show skin](https://skinport.com/item/{sale.get('url', '')})", inline=True)
        
        await channel.send(embed=embed)


@bot.event
async def on_ready():
    print(f"✅ Bot ist eingeloggt als {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send('@everyone Pong!')