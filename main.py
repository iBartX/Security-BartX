import os
import discord
from discord.ext import commands
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة ---
app = Flask('')
@app.route('/')
def home(): return "Security BartX Shield is Online 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# قوائم التتبع
spam_tracker = {}
punishment_history = {}

@bot.event
async def on_ready():
    print(f'--- [ البوت متصل الآن بكامل الميزات ] ---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. أوامر الروم الصوتي ---
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client: await ctx.voice_client.move_to(channel)
        else: await channel.connect()
        await ctx.send(f"✅ أبشر، دخلت روم: **{channel.name}**")
    else:
        await ctx.send("⚠️ ادخل روم صوتي أولاً!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم الخروج.")

# --- 4. محرك الحماية الشامل (on_message) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return

    is_admin = message.author.guild_permissions.manage_messages
    user_id = message.author.id

    if not is_admin:
        # [أ] منع الروابط والصور
        if any(x in message.content.lower() for x in ["http", "discord.gg", "www."]) or message.attachments:
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}، يمنع نشر الروابط أو الصور!", delete_after=5)
                return
            except: pass

        # [ب] نظام السبام المتطور
        current_time = datetime.datetime.now().timestamp()
        if user_id not in spam_tracker: spam_tracker[user_id] = []
        spam_tracker[user_id].append(current_time)
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]

        if len(spam_tracker[user_id]) > 5:
            punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
            if punishment_history[user_id] == 1:
                try: await message.author.timeout(datetime.timedelta(minutes=10), reason="Spamming")
                except: pass
                await message.channel.send(f"🔇 {message.author.mention} تايم أوت 10د بسبب السبام.")
            elif punishment_history[user_id] >= 2:
                try: await message.author.kick(reason="Repeated Spamming")
                except: pass
                await message.channel.send(f"👢 تم طرد {message.author.mention} بسبب تكرار السبام.")
            return

    await bot.process_commands(message)

# --- 5. نظام Anti-Nuke (حماية الرومات والرتب) ---
@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id == channel.guild.owner_id or entry.user.id == bot.user.id: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Channel Deletion")
        except: pass

@bot.event
async def on_guild_role_update(before, after):
    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
        if entry.user.id == after.guild.owner_id or entry.user.id == bot.user.id: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Role Modification")
        except: pass

# --- 6. الأوامر الإدارية ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم إغلاق القناة.")

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ لوحة تحكم Security BartX", color=discord.Color.blue())
    emb.add_field(name="🎙️ الصوت", value="`!join`, `!leave`", inline=True)
    emb.add_field(name="🧹 الإدارة", value="`!clear`, `!lock`", inline=True)
    emb.add_field(name="🚫 الحماية", value="منع الروابط، الصور، والسبام (تلقائي).", inline=False)
    await ctx.send(embed=emb)

# --- 7. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
