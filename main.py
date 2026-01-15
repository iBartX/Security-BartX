import os
import discord
from discord.ext import commands
import datetime
import logging
from flask import Flask
from threading import Thread
import asyncio

# --- 1. نظام الاستضافة (Web Server) ---
app = Flask('')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Security BartX Ultimate + Voice is Online!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. إعدادات البوت والقوائم ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

BLACKLIST = ["شتيمة1", "كلمة_ممنوعة", "رابط_خبيث"]
spam_tracker = {}
punishment_history = {} 

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تشغيل النسخة الشاملة (حماية + صوت): {bot.user.name}')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help_me | !join"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. أوامر الروم الصوتي ---

@bot.command()
async def join(ctx):
    """أمر دخول البوت للروم الصوتي"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"✅ تم الانضمام للروم: **{channel.name}**")
    else:
        await ctx.send("⚠️ ادخل روم صوتي أولاً!")

@bot.command()
async def leave(ctx):
    """أمر خروج البوت من الروم الصوتي"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم الخروج.")
    else:
        await ctx.send("❌ لست متصلاً بصوت.")

# --- 4. حماية الشات (سبام، كلمات، روابط) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    # استثناء الإداريين
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_time = datetime.datetime.now().timestamp()

    # [أ] نظام السبام المتطور (تايم أوت ثم طرد)
    if user_id not in spam_tracker: spam_tracker[user_id] = []
    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]

    if len(spam_tracker[user_id]) > 5:
        punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
        log_chan = get_log_channel(message.guild)
        
        if punishment_history[user_id] == 1: # المرة الأولى: تايم أوت
            try:
                await message.author.timeout(datetime.timedelta(minutes=10), reason="Spamming")
                await message.channel.send(f"🔇 {message.author.mention} تايم أوت 10د (سبام).", delete_after=5)
                if log_chan:
                    await log_chan.send(f"🔇 **تايم أوت:** {message.author.mention} بسبب السبام.")
            except: pass
        elif punishment_history[user_id] >= 2: # المرة الثانية: طرد
            try:
                await message.author.kick(reason="Repeated Spamming")
                await message.channel.send(f"👢 طرد {message.author.mention} (تكرار سبام).")
                punishment_history[user_id] = 0
            except: pass
        
        try: await message.channel.purge(limit=5, check=lambda m: m.author == message.author)
        except: pass
        return

    # [ب] الكلمات والروابط
    msg_content = message.content.lower()
    for word in BLACKLIST:
        if word in msg_content:
            await message.delete()
            return
    if "http" in msg_content:
        await message.delete()
        return

    await bot.process_commands(message)

# --- 5. نظام Anti-Nuke (حماية الرومات والرتب) ---

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id == channel.guild.owner_id or entry.user.id == bot.user.id: return
        await entry.user.edit(roles=[], reason="Anti-Nuke: Channel Deleted")
        log_chan = get_log_channel(channel.guild)
        if log_chan:
            await log_chan.send(f"🚫 **تخريب:** {entry.user.mention} حذف روم وتم سحب رتبه.")

@bot.event
async def on_guild_role_update(before, after):
    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
        if entry.user.id == after.guild.owner_id or entry.user.id == bot.user.id: return
        await entry.user.edit(roles=[], reason="Anti-Nuke: Role Modified")
        log_chan = get_log_channel(after.guild)
        if log_chan:
            await log_chan.send(f"🚫 **تخريب:** {entry.user.mention} عدل رتبة وتم سحب رتبه.")

# --- 6. أوامر الإدارة والمساعدة ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        await log_chan.send(f"🧹 {ctx.author.mention} مسح `{len(deleted)-1}` رسالة.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم إغلاق القناة.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح القناة.")

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ لوحة تحكم Security BartX الشاملة", color=discord.Color.gold())
    emb.add_field(name="🎙️ الصوت", value="`!join`, `!leave`", inline=True)
    emb.add_field(name="🛠️ الإدارة", value="`!clear`, `!lock`, `!unlock`", inline=True)
    emb.add_field(name="🚫 الحماية", value="منع السبام (عقوبات متدرجة)، منع الروابط، ومنع الكلمات.", inline=False)
    emb.add_field(name="🛡️ Anti-Nuke", value="حماية الرومات والرتب مفعلة (سحب رتب المخربين).", inline=False)
    emb.set_footer(text="يجب وجود روم logs-security")
    await ctx.send(embed=emb)

# --- 7. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
