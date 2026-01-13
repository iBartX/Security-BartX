import os
import discord
from discord.ext import commands
import datetime
import logging
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة (لضمان البقاء 24/7) ---
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
# قمنا بإضافة نظام مساعدة مخصص (help_command=None) لنصنع أمر !help_me الخاص بنا
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

BLACKLIST = ["شتيمة1", "كلمة_ممنوعة", "رابط_خبيث"]

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تشغيل نظام الحماية بنجاح: {bot.user.name}')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

# وظيفة البحث عن قناة السجلات (logs-security)
def get_log_channel(guild):
    # يبحث عن القناة بالاسم؛ تأكد أن الاسم في ديسكورد هو logs-security بالضبط
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. محرك الحماية والتنبيهات ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    msg_content = message.content.lower()

    # [أ] فحص الكلمات المحظورة
    for word in BLACKLIST:
        if word in msg_content:
            try:
                await message.delete()
                log_channel = get_log_channel(message.guild)
                if log_channel:
                    embed = discord.Embed(title="🚨 كشف كلمة محظورة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    embed.add_field(name="المخالف:", value=message.author.mention, inline=True)
                    embed.add_field(name="الكلمة المستخدمة:", value=word, inline=True)
                    embed.set_footer(text=f"ID: {message.author.id}")
                    await log_channel.send(embed=embed)
                await message.channel.send(f"⚠️ {message.author.mention}، عذراً، هذه الكلمة غير مسموحة هنا!", delete_after=5)
            except: pass
            return

    # [ب] منع الروابط لغير الإداريين
    if "http" in msg_content:
        if not message.author.guild_permissions.manage_messages:
            try:
                await message.delete()
                log_channel = get_log_channel(message.guild)
                if log_channel:
                    embed = discord.Embed(title="🔗 محاولة نشر رابط", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                    embed.add_field(name="العضو:", value=message.author.mention)
                    await log_channel.send(embed=embed)
                await message.channel.send(f"❌ {message.author.mention}، يمنع نشر الروابط في هذا السيرفر.", delete_after=5)
            except: pass
            return

    await bot.process_commands(message)

# --- 4. الأوامر المخصصة ---

# أمر المساعدة المخصص !help_me
@bot.command()
async def help_me(ctx):
    embed = discord.Embed(
        title="🛡️ قائمة أوامر Security BartX",
        description="أنا بوت حماية متطور أعمل على تأمين سيرفرك 24/7.",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="`!clear [العدد]`", value="لحذف الرسائل (للإداريين فقط).", inline=False)
    embed.add_field(name="`!help_me`", value="عرض هذه القائمة.", inline=False)
    embed.add_field(name="⚙️ نظام الحماية التلقائي", value="أقوم بحذف الكلمات البذيئة والروابط تلقائياً وإرسال سجل إلى قناة `logs-security`.", inline=False)
    embed.set_footer(text=f"طلب بواسطة: {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم تنظيف `{amount}` رسالة بنجاح.", delete_after=3)

# --- 5. التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive() 
    try:
        token = os.environ.get('TOKEN')
        if token:
            bot.run(token)
        else:
            print("Error: TOKEN not found in Environment Variables!")
    except Exception as e:
        print(f"Error: {e}")
