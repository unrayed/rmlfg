import discord
import json
import os
from discord import app_commands, Interaction
from discord.utils import get
from discord.ext import commands
from aiohttp import web
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

GUILD_ID = 1376261610137456892
NGROK_URL = "https://f96dc8fc15bd.ngrok-free.app"

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))

client = MyClient()

@client.tree.command(name="verify", description="Verify your Steam account", guild=discord.Object(id=GUILD_ID))
async def verify(interaction: Interaction):
    discord_user_id = interaction.user.id
    oauth_url = f"{NGROK_URL}/steam/login?discord_id={discord_user_id}"

    embed = discord.Embed(
        title="Steam Verification",
        description=f"[Click here to verify your Steam account]({oauth_url})",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)

async def assign_role_to_user(discord_user_id: int, rank: str, guild_id: int):
    guild = client.get_guild(guild_id)
    if not guild:
        print("Guild not found")
        return False

    member = guild.get_member(discord_user_id)
    if not member:
        print("Member not found")
        return False

    main_rank = rank.split()[0]
    role = get(guild.roles, name=main_rank)
    if not role:
        print(f"Role {main_rank} not found")
        return False

    try:
        await member.add_roles(role)
        print(f"Assigned role {main_rank} to {member}")
        return True
    except discord.HTTPException as e:
        print(f"Failed to add role: {e}")
        return False

async def handle_assignrole(request):
    data = await request.json()
    discord_id = int(data.get("discord_id"))
    rank = data.get("rank")
    guild_id = int(data.get("guild_id"))

    success = await assign_role_to_user(discord_id, rank, guild_id)
    return web.json_response({"success": success})

# aiohttp web server for receiving webhook from Flask
app = web.Application()
app.router.add_post('/assignrole', handle_assignrole)

if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    loop.run_until_complete(site.start())

    loop.create_task(client.start(BOT_TOKEN))
    loop.run_forever()
