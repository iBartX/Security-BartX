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

# تخزين السبام والعقوبات
spam_tracker = {}
punishment_history = {} # {user_id: count}

@bot.event
async def on_ready():
    print(f'---')
    print(f'تم تفعيل نظام (Timeout + Kick) للسبام بنجاح')
    print(f'---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. محرك الحماية والعقوبات المتدرجة ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    # استثناء الإداريين من العقوبات
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return

    user_id = message.author.id
    current_time = datetime.datetime.now().timestamp()

    # نظام كشف السبام
    if user_id not in spam_tracker:
        spam_tracker[user_id] = []
    
    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]

    # إذا تجاوز الحد (أكثر من 5 رسائل في 5 ثواني)
    if len(spam_tracker[user_id]) > 5:
        log_chan = get_log_channel(message.guild)
        
        # زيادة سجل العقوبات للعضو
        punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
        
        # العقوبة الأولى: Time Out (10 دقائق)
        if punishment_history[user_id] == 1:
            try:
                duration = datetime.timedelta(minutes=10)
                await message.author.timeout(duration, reason="Spamming (First Warning)")
                await message.channel.send(f"🔇 {message.author.mention} تم إعطاؤك تايم أوت لمدة 10 دقائق بسبب السبام.", delete_after=10)
                
                if log_chan:
                    emb = discord.Embed(title="🔇 عقوبة: تايم أوت", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="المخالف:", value=message.author.mention)
                    emb.add_field(name="السبب:", value="سبام (المرة الأولى)")
                    await log_chan.send(embed=emb)
            except Exception as e: print(f"Error Timeout: {e}")

        # العقوبة الثانية: Kick (طرد)
        elif punishment_history[user_id] >= 2:
            try:
                await message.author.kick(reason="Repeated Spamming")
                await message.channel.send(f"👢 {message.author.mention} تم طردك من السيرفر بسبب تكرار السبام!")
                
                if log_chan:
                    emb = discord.Embed(title="👢 عقوبة: طرد", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
                    emb.add_field(name="المطرود:", value=f"{message.author.name}")
                    emb.add_field(name="السبب:", value="تكرار السبام (المرة الثانية)")
                    await log_chan.send(embed=emb)
                # تصفير السجل بعد الطرد
                punishment_history[user_id] = 0
            except Exception as e: print(f"Error Kick: {e}")
        
        # حذف رسائل السبام في كل الأحوال
        try: await message.channel.purge(limit=5, check=lambda m: m.author == message.author)
        except: pass
        return

    await bot.process_commands(message)

# --- 4. الأوامر الإدارية ---

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
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {len(deleted)-1} رسالة.", delete_after=3)

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ نظام العقوبات المتطور", color=discord.Color.gold())
    emb.add_field(name="🚫 نظام السبام", value="1️⃣ المرة الأولى: تايم أوت (10 د).\n2️⃣ المرة الثانية: طرد (Kick).", inline=False)
    emb.add_field(name="🧹 الإدارة", value="`!clear`, `!lock`, `!unlock`", inline=False)
    await ctx.send(embed=emb)

# --- 5. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    try:
        token = os.environ.get('TOKEN')
        bot.run(token)
    except Exception as e:
        print(f"Error: {e}")
