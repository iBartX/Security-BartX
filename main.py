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
    return "Security BartX Ultimate is Online!"

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
punishment_history = {} # لتتبع عدد مرات السبام للعقوبات المتدرجة

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تشغيل النسخة الكاملة للبوت: {bot.user.name}')
    print(f'نظام الحماية ضد التخريب (Anti-Nuke) نشط')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. حماية الشات (سبام، كلمات، روابط) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    # استثناء الإداريين من فحص الشات
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_time = datetime.datetime.now().timestamp()

    # [أ] نظام السبام المتطور
    if user_id not in spam_tracker: spam_tracker[user_id] = []
    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]

    if len(spam_tracker[user_id]) > 5:
        punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
        log_chan = get_log_channel(message.guild)
        
        if punishment_history[user_id] == 1: # المرة الأولى: تايم أوت
            try:
                await message.author.timeout(datetime.timedelta(minutes=10), reason="Spamming")
                await message.channel.send(f"🔇 {message.author.mention} تم إسكاتك 10 دقائق بسبب السبام.", delete_after=5)
                if log_chan:
                    emb = discord.Embed(title="🔇 تايم أوت (سبام)", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="العضو:", value=message.author.mention)
                    await log_chan.send(embed=emb)
            except: pass
        elif punishment_history[user_id] >= 2: # المرة الثانية: طرد
            try:
                await message.author.kick(reason="Repeated Spamming")
                await message.channel.send(f"👢 تم طرد {message.author.mention} لتكرار السبام.")
                if log_chan:
                    emb = discord.Embed(title="👢 طرد (تكرار سبام)", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="العضو:", value=message.author.name)
                    await log_chan.send(embed=emb)
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

# --- 4. نظام Anti-Nuke (حماية الرومات والرتب) ---

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id == channel.guild.owner_id or entry.user.id == bot.user.id: return
        await entry.user.edit(roles=[], reason="Anti-Nuke: Channel Deleted")
        log_chan = get_log_channel(channel.guild)
        if log_chan:
            await log_chan.send(f"🚫 **محاولة تخريب:** {entry.user.mention} حذف روم `{channel.name}` وتم سحب رتبه.")

@bot.event
async def on_guild_role_update(before, after):
    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
        if entry.user.id == after.guild.owner_id or entry.user.id == bot.user.id: return
        await entry.user.edit(roles=[], reason="Anti-Nuke: Role Modified")
        log_chan = get_log_channel(after.guild)
        if log_chan:
            await log_chan.send(f"🚫 **محاولة تخريب:** {entry.user.mention} عدل رتبة `{after.name}` وتم سحب رتبه.")

@bot.event
async def on_member_update(before, after):
    if len(before.roles) != len(after.roles):
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
            if entry.user.id == after.guild.owner_id or entry.user.id == bot.user.id: return
            await entry.user.edit(roles=[], reason="Anti-Nuke: Role Tampering")
            log_chan = get_log_channel(after.guild)
            if log_chan:
                await log_chan.send(f"🚫 **تنبيه:** {entry.user.mention} تلاعب بالرتب وتم سحب صلاحياته.")

# --- 5. أوامر الإدارة والمساعدة ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {len(deleted)-1} رسالة.", delete_after=3)
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        await log_chan.send(f"🧹 {ctx.author.mention} قام بمسح `{len(deleted)-1}` رسالة في {ctx.channel.mention}")

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
    emb = discord.Embed(title="🛡️ لوحة تحكم Security BartX", color=discord.Color.gold())
    emb.add_field(name="🛠️ الإدارة", value="`!clear`, `!lock`, `!unlock`", inline=False)
    emb.add_field(name="🚫 الحماية التلقائية", value="منع السبام (Timeout/Kick)، منع الروابط والكلمات البذيئة.", inline=False)
    emb.add_field(name="🛡️ Anti-Nuke", value="حماية الرومات والرتب (سحب رتب تلقائي للمخربين).", inline=False)
    emb.set_footer(text="يجب وجود روم باسم logs-security للسجلات")
    await ctx.send(embed=emb)

# --- 6. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
