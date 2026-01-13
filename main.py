import os
import discord
from discord.ext import commands
import datetime
import logging
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة ---
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
bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1460594108824555562 
BLACKLIST = ["شتيمة1", "كلمة_ممنوعة", "رابط_خبيث"]

@bot.event
async def on_ready():
    print(f'تم تشغيل نظام الحماية بنجاح: {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    msg_content = message.content.lower()

    for word in BLACKLIST:
        if word in msg_content:
            try:
                await message.delete()
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    embed = discord.Embed(title="🚨 حذف تلقائي", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    embed.add_field(name="العضو:", value=message.author.mention)
                    embed.add_field(name="الكلمة:", value=word)
                    await log_channel.send(embed=embed)
                await message.channel.send(f"⚠️ {message.author.mention}، يمنع استخدام كلمات محظورة!", delete_after=5)
            except: pass
            return

    if "http" in msg_content:
        if not message.author.guild_permissions.manage_messages:
            try:
                await message.delete()
                await message.channel.send(f"❌ {message.author.mention}، نشر الروابط ممنوع!", delete_after=5)
            except: pass
            return

    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم تنظيف الشات.", delete_after=3)

# --- 3. التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive() 
    try:
        token = os.environ.get('TOKEN')
        if token:
            bot.run(token)
        else:
            print("Error: TOKEN not found!")
    except Exception as e:
        print(f"Error: {e}")
