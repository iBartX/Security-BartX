import os
import discord
from discord.ext import commands
import datetime
import logging
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة (Web Server) ---
app = Flask('')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "Security BartX is Online 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

BLACKLIST = ["شتيمة1", "كلمة_ممنوعة", "رابط_خبيث"]

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تشغيل نظام الحماية والإدارة: {bot.user.name}')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. محرك الحماية التلقائي ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    msg_content = message.content.lower()

    for word in BLACKLIST:
        if word in msg_content:
            try:
                await message.delete()
                log_chan = get_log_channel(message.guild)
                if log_chan:
                    emb = discord.Embed(title="🚨 كشف كلمة محظورة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="المخالف:", value=message.author.mention)
                    emb.add_field(name="الكلمة:", value=word)
                    await log_chan.send(embed=emb)
                await message.channel.send(f"⚠️ {message.author.mention}، يمنع استخدام هذه الكلمات!", delete_after=5)
            except: pass
            return

    if "http" in msg_content and not message.author.guild_permissions.manage_messages:
        try:
            await message.delete()
            log_chan = get_log_channel(message.guild)
            if log_chan:
                emb = discord.Embed(title="🔗 محاولة نشر رابط", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                emb.add_field(name="العضو:", value=message.author.mention)
                await log_chan.send(embed=emb)
            await message.channel.send(f"❌ {message.author.mention}، الروابط ممنوعة!", delete_after=5)
        except: pass
        return

    await bot.process_commands(message)

# --- 4. أوامر الإدارة (فتح، إغلاق، مسح) ---

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """إغلاق الشات"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم إغلاق القناة بنجاح.")
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🔒 تحديث القناة", description=f"قام {ctx.author.mention} بإغلاق {ctx.channel.mention}", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        await log_chan.send(embed=emb)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """فتح الشات"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح القناة بنجاح.")
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🔓 تحديث القناة", description=f"قام {ctx.author.mention} بفتح {ctx.channel.mention}", color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
        await log_chan.send(embed=emb)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    """مسح الرسائل"""
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {len(deleted)-1} رسالة.", delete_after=3)
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🧹 مسح رسائل", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
        emb.add_field(name="بواسطة:", value=ctx.author.mention)
        emb.add_field(name="القناة:", value=ctx.channel.mention)
        emb.add_field(name="العدد:", value=str(len(deleted)-1))
        await log_chan.send(embed=emb)

# --- 5. أمر المساعدة المطور ---
@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ أوامر Security BartX", color=discord.Color.gold(), timestamp=datetime.datetime.utcnow())
    emb.add_field(name="🧹 `!clear [العدد]`", value="لمسح عدد معين من الرسائل.", inline=False)
    emb.add_field(name="🔒 `!lock`", value="لإغلاق الكتابة في القناة الحالية.", inline=True)
    emb.add_field(name="🔓 `!unlock`", value="لفتح الكتابة في القناة الحالية.", inline=True)
    emb.add_field(name="📜 السجلات", value="تأكد من وجود روم باسم `logs-security` لتلقي التقارير.", inline=False)
    emb.set_footer(text=f"طلب بواسطة: {ctx.author.name}")
    await ctx.send(embed=emb)

# --- 6. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    try:
        token = os.environ.get('TOKEN')
        bot.run(token)
    except Exception as e:
        print(f"Error: {e}")
