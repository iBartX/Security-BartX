import os
import discord
from discord.ext import commands
import datetime
import logging
from flask import Flask
from threading import Thread
import asyncio

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
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

BLACKLIST = ["شتيمة1", "كلمة_ممنوعة", "رابط_خبيث"]
# نظام تتبع السبام: {user_id: [timestamps]}
spam_tracker = {}

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تفعيل نظام الحماية الشاملة (كلمات + روابط + سبام)')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. محرك الحماية التلقائي (السبام، الكلمات، الروابط) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    user_id = message.author.id
    current_time = datetime.datetime.now().timestamp()

    # [أ] نظام كشف السبام (Spam Protection)
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []
    
    # إضافة وقت الرسالة الحالية وتنظيف الأوقات القديمة (أقدم من 5 ثواني)
    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]

    # إذا أرسل أكثر من 5 رسائل في 5 ثواني
    if len(spam_tracker[user_id]) > 5:
        try:
            await message.delete()
            if len(spam_tracker[user_id]) == 6: # إرسال التحذير مرة واحدة فقط عند تجاوز الحد
                await message.channel.send(f"⚠️ {message.author.mention}، توقف عن السبام! سيتم حذف رسائلك تلقائياً.", delete_after=5)
                log_chan = get_log_channel(message.guild)
                if log_chan:
                    emb = discord.Embed(title="🛡️ كشف سبام", color=discord.Color.dark_red(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="المخالف:", value=message.author.mention)
                    emb.add_field(name="الإجراء:", value="حذف الرسائل تلقائياً")
                    await log_chan.send(embed=emb)
            return
        except: pass

    msg_content = message.content.lower()

    # [ب] فحص الكلمات المحظورة
    for word in BLACKLIST:
        if word in msg_content:
            try:
                await message.delete()
                log_chan = get_log_channel(message.guild)
                if log_chan:
                    emb = discord.Embed(title="🚨 كلمة محظورة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="المخالف:", value=message.author.mention)
                    emb.add_field(name="الكلمة:", value=word)
                    await log_chan.send(embed=emb)
                await message.channel.send(f"⚠️ {message.author.mention}، الكلمات البذيئة ممنوعة!", delete_after=5)
            except: pass
            return

    # [ج] منع الروابط لغير الإداريين
    if "http" in msg_content and not message.author.guild_permissions.manage_messages:
        try:
            await message.delete()
            log_chan = get_log_channel(message.guild)
            if log_chan:
                emb = discord.Embed(title="🔗 رابط غير مسموح", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                emb.add_field(name="العضو:", value=message.author.mention)
                await log_chan.send(embed=emb)
            await message.channel.send(f"❌ {message.author.mention}، الروابط ممنوعة هنا!", delete_after=5)
        except: pass
        return

    await bot.process_commands(message)

# --- 4. أوامر الإدارة ---

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم إغلاق القناة.")
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🔒 إغلاق قناة", description=f"بواسطة: {ctx.author.mention}\nالقناة: {ctx.channel.mention}", color=discord.Color.red())
        await log_chan.send(embed=emb)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح القناة.")
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🔓 فتح قناة", description=f"بواسطة: {ctx.author.mention}\nالقناة: {ctx.channel.mention}", color=discord.Color.green())
        await log_chan.send(embed=emb)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {len(deleted)-1} رسالة.", delete_after=3)
    log_chan = get_log_channel(ctx.guild)
    if log_chan:
        emb = discord.Embed(title="🧹 تنظيف الشات", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
        emb.add_field(name="بواسطة:", value=ctx.author.mention)
        emb.add_field(name="العدد:", value=str(len(deleted)-1))
        await log_chan.send(embed=emb)

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ دليل حماية Security BartX", color=discord.Color.gold())
    emb.add_field(name="🧹 `!clear [العدد]`", value="مسح الرسائل.", inline=False)
    emb.add_field(name="🔒 `!lock` / `!unlock`", value="إغلاق وفتح القناة.", inline=False)
    emb.add_field(name="🚫 نظام السبام", value="تلقائي: 5 رسائل في 5 ثوانٍ تؤدي للحذف والتحذير.", inline=False)
    emb.set_footer(text="نظام الحماية نشط الآن")
    await ctx.send(embed=emb)

# --- 5. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    try:
        token = os.environ.get('TOKEN')
        bot.run(token)
    except Exception as e:
        print(f"Error: {e}")
