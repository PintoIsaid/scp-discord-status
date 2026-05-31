import os
import discord
from discord.ext import tasks
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(minutes=2)
async def update_channel():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://backend.scpslgame.com/api/serverlist.php") as resp:
                data = await resp.json()

        players = "0/40"
        online = False

        for server in data:
            if "199.127.62.78:3000" in str(server):
                online = True
                players = f"{server.get('Players',0)}/{server.get('MaxPlayers',40)}"
                break

        guild = client.guilds[0]
        channel = guild.get_channel(CHANNEL_ID)

        if channel:
            status = "🟢 Online" if online else "🔴 Offline"
            await channel.edit(name=f"{status} | {players}")

    except Exception as e:
        print(e)

@client.event
async def on_ready():
    print(f"Conectado como {client.user}")
    update_channel.start()

client.run(TOKEN)
