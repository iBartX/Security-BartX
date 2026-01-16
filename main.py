import os
import discord
from discord.ext import commands
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة 24/7 ---
app = Flask('')
@app.route('/')
def home(): return "Security BartX Ultimate Shield is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

spam_tracker = {}
punishment_history = {} # لتتبع عدد مرات مخالفة الشخص للسبام

@bot.event
async def on_ready():
    print(f'--- [ Security BartX: تم تحديث نظام السبام الشامل ] ---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

async def send_to_logs(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs-security')
    if log_channel:
        await log_channel.send(embed=embed)

# --- 3. نظام Anti-Nuke (ويب هوك، بان، رتب، رومات) ---

@bot.event
async def on_webhooks_update(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
        if entry.user.id in [channel.guild.owner_id, bot.user.id]: return
        webhooks = await channel.webhooks()
        for wh in webhooks: await wh.delete()
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Webhook Creation")
        except: pass
        
        emb = discord.Embed(title="🚫 محاولة إنشاء ويب هوك", color=discord.Color.red())
        emb.add_field(name="الفاعل:", value=entry.user.mention)
        emb.add_field(name="الإجراء:", value="حذف الويب هوك وسحب الرتب")
        await send_to_logs(channel.guild, emb)

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.user.id in [guild.owner_id, bot.user.id]: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Unauthorized Ban")
        except: pass
        try: await guild.unban(user, reason="Anti-Nuke: Protection Triggered")
        except: pass
        
        emb = discord.Embed(title="🛡️ فك بان تلقائي", color=discord.Color.dark_red())
        emb.add_field(name="المشرف:", value=entry.user.mention)
        emb.add_field(name="العضو المظلوم:", value=user.name)
        emb.add_field(name="الإجراء:", value="سحب رتب المشرف وفك البان فوراً")
        await send_to_logs(guild, emb)

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id in [channel.guild.owner_id, bot.user.id]: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Channel Delete")
        except: pass
        emb = discord.Embed(title="📁 حذف قناة", color=discord.Color.orange())
        emb.add_field(name="الفاعل:", value=entry.user.mention)
        emb.add_field(name="القناة:", value=channel.name)
        await send_to_logs(channel.guild, emb)

# --- 4. حماية الشات ونظام السبام المعدل ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    is_admin = message.author.guild_permissions.manage_messages
    user_id = message.author.id

    if not is_admin:
        # منع الروابط والصور
        if any(x in message.content.lower() for x in ["http", "discord.gg", "www."]) or message.attachments:
            await message.delete()
            return

        # نظام السبام المطور
        current_time = datetime.datetime.now().timestamp()
        if user_id not in spam_tracker: spam_tracker[user_id] = []
        spam_tracker[user_id].append(current_time)
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5] # 5 رسائل في 5 ثواني
        
        if len(spam_tracker[user_id]) > 5:
            punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
            count = punishment_history[user_id]
            
            emb = discord.Embed(title="🔇 مخالفة سبام", color=discord.Color.greyple())
            emb.add_field(name="العضو:", value=message.author.mention)

            if count == 1:
                # المرة الأولى: 10 دقائق
                try: await message.author.timeout(datetime.timedelta(minutes=10), reason="Spam (1st time)")
                except: pass
                emb.add_field(name="العقوبة:", value="تايم أوت 10 دقائق")
            
            elif count == 2:
                # المرة الثانية: 30 دقيقة
                try: await message.author.timeout(datetime.timedelta(minutes=30), reason="Spam (2nd time)")
                except: pass
                emb.add_field(name="العقوبة:", value="تايم أوت 30 دقيقة")
            
            elif count >= 3:
                # المرة الثالثة: طرد
                try: await message.author.kick(reason="Spam (3rd time - Final)")
                except: pass
                emb.add_field(name="العقوبة:", value="طرد من السيرفر (Kick)")
                punishment_history[user_id] = 0 # تصفير العداد بعد الطرد
            
            await send_to_logs(message.guild, emb)
            await message.channel.send(f"⚠️ {message.author.mention}، توقف عن السبام! تم اتخاذ الإجراء المناسب.", delete_after=5)
            return

    await bot.process_commands(message)

# --- 5. الأوامر الكاملة (إدارة + صوت) ---

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ أبشر، دخلت الروم الصوتي.")
    else: await ctx.send("❌ ادخل روم صوتي أولاً!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم الخروج.")
    else: await ctx.send("❌ أنا لست في روم صوتي.")

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
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح القناة.")

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ Security BartX Ultimate", color=discord.Color.gold())
    emb.add_field(name="🎙️ صوت", value="`!join`, `!leave`", inline=True)
    emb.add_field(name="🧹 إدارة", value="`!clear`, `!lock`, `!unlock`", inline=True)
    emb.add_field(name="🚫 نظام السبام الجديد", value="1: 10د | 2: 30د | 3: طرد", inline=False)
    await ctx.send(embed=emb)

# --- 6. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
