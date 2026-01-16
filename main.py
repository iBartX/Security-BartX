import os, discord, datetime, asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread

# --- الاستضافة ---
app = Flask('')
@app.route('/')
def home(): return "Security BartX Ultimate is Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive(): Thread(target=run, daemon=True).start()

# --- الإعدادات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
spam_tracker = {}
punishment_history = {}

async def send_to_logs(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs-security')
    if log_channel: await log_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"--- [ {bot.user.name} جاهز للعمل بكامل الميزات ] ---")

# --- نظام الحماية (Anti-Nuke & Anti-Ban) ---
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(2)
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.target.id == user.id:
            mod = entry.user
            if mod.id in [guild.owner_id, bot.user.id]: return
            try: await mod.edit(roles=[], reason="Anti-Nuke: Unauthorized Ban")
            except: pass
            try: await guild.unban(user, reason="Anti-Nuke: Protection Triggered")
            except: pass
            emb = discord.Embed(title="🛡️ فك بان تلقائي", color=discord.Color.red())
            emb.add_field(name="المخالف:", value=mod.mention); emb.add_field(name="الضحية:", value=user.name)
            await send_to_logs(guild, emb)

@bot.event
async def on_webhooks_update(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
        if entry.user.id in [channel.guild.owner_id, bot.user.id]: return
        for wh in await channel.webhooks(): await wh.delete()
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Webhook")
        except: pass
        emb = discord.Embed(title="🚫 منع ويب هوك", color=discord.Color.orange())
        emb.add_field(name="الفاعل:", value=entry.user.mention)
        await send_to_logs(channel.guild, emb)

# --- حماية الشات والسبام ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    if not message.author.guild_permissions.manage_messages:
        if any(x in message.content.lower() for x in ["http", "discord.gg"]) or message.attachments:
            await message.delete(); return
        
        uid = message.author.id
        now = datetime.datetime.now().timestamp()
        if uid not in spam_tracker: spam_tracker[uid] = []
        spam_tracker[uid].append(now)
        spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]
        
        if len(spam_tracker[uid]) > 5:
            punishment_history[uid] = punishment_history.get(uid, 0) + 1
            lvl = punishment_history[uid]
            if lvl == 1: await message.author.timeout(datetime.timedelta(minutes=10))
            elif lvl == 2: await message.author.timeout(datetime.timedelta(minutes=30))
            elif lvl >= 3: await message.author.kick(); punishment_history[uid] = 0
            return
    await bot.process_commands(message)

# --- الأوامر ---
@bot.command()
async def join(ctx):
    if ctx.author.voice: await ctx.author.voice.channel.connect(); await ctx.send("✅")
@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect(); await ctx.send("👋")
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, n: int = 10): await ctx.channel.purge(limit=n+1)
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send("🔒")
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send("🔓")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
