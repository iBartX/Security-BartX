import os
import discord
from discord.ext import commands
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة (24/7) ---
app = Flask('')
@app.route('/')
def home(): return "Security BartX Ultimate Shield is ONLINE!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- 2. إعدادات البوت الأساسية ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# مخازن البيانات (السبام والعقوبات)
spam_tracker = {}
punishment_history = {}

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"✅ تم تشغيل البوت الشامل بنجاح: {bot.user.name}")
    print(f"🛡️ جميع أنظمة الحماية والسجلات نشطة")
    print(f"========================================")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

# دالة إرسال السجلات الشاملة لـ logs-security
async def send_to_logs(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs-security')
    if log_channel:
        try: await log_channel.send(embed=embed)
        except: pass

# --- 3. نظام ANTI-BAN (منع البان العشوائي وفك البان) ---
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(2) # انتظار مزامنة سجلات ديسكورد
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.target.id == user.id:
            mod = entry.user
            if mod.id == guild.owner_id or mod.id == bot.user.id: return

            # سحب الرتب من المشرف المخالف
            try: await mod.edit(roles=[], reason="Anti-Nuke: Unauthorized Ban Detect")
            except: pass

            # فك البان عن العضو المظلوم فوراً
            try: await guild.unban(user, reason="Anti-Nuke: Protection System")
            except: pass

            # إرسال سجل للحدث
            emb = discord.Embed(title="🚨 محاولة بان عشوائي", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            emb.add_field(name="المشرف المخالف", value=f"{mod.mention} ({mod.id})", inline=False)
            emb.add_field(name="العضو المظلوم", value=f"{user.name}", inline=False)
            emb.add_field(name="الإجراء", value="تم سحب الرتب وفك البان تلقائياً", inline=False)
            await send_to_logs(guild, emb)

# --- 4. نظام ANTI-WEBHOOK (منع الويب هوك) ---
@bot.event
async def on_webhooks_update(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
        mod = entry.user
        if mod.id == channel.guild.owner_id or mod.id == bot.user.id: return
        
        # حذف الويب هوك فوراً ومعاقبة الفاعل
        for wh in await channel.webhooks(): await wh.delete()
        try: await mod.edit(roles=[], reason="Anti-Nuke: Webhook Creation")
        except: pass

        emb = discord.Embed(title="🚫 منع ويب هوك", color=discord.Color.orange())
        emb.add_field(name="الفاعل", value=mod.mention)
        emb.add_field(name="القناة", value=channel.mention)
        emb.add_field(name="النتيجة", value="حذف الويب هوك وسحب الرتب")
        await send_to_logs(channel.guild, emb)

# --- 5. حماية الرومات والرتب ---
@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        mod = entry.user
        if mod.id == channel.guild.owner_id or mod.id == bot.user.id: return
        try: await mod.edit(roles=[], reason="Anti-Nuke: Channel Delete")
        except: pass
        emb = discord.Embed(title="📁 حذف قناة", color=discord.Color.dark_red())
        emb.add_field(name="الفاعل", value=mod.mention); emb.add_field(name="القناة", value=channel.name)
        await send_to_logs(channel.guild, emb)

@bot.event
async def on_guild_role_update(before, after):
    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
        mod = entry.user
        if mod.id == after.guild.owner_id or mod.id == bot.user.id: return
        try: await mod.edit(roles=[], reason="Anti-Nuke: Role Manipulation")
        except: pass
        emb = discord.Embed(title="🎭 تلاعب بالرتب", color=discord.Color.blue())
        emb.add_field(name="الفاعل", value=mod.mention); emb.add_field(name="الرتبة", value=after.name)
        await send_to_logs(after.guild, emb)

# --- 6. حماية الشات (سبام، روابط، صور) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    # المشرفين مستثنون من قيود الشات
    if message.author.guild_permissions.manage_messages:
        await bot.process_commands(message)
        return

    # منع الروابط والصور
    if any(x in message.content.lower() for x in ["http", "discord.gg", "www."]) or message.attachments:
        try: await message.delete()
        except: pass
        return

    # نظام السبام المتدرج (10د -> 30د -> طرد)
    uid = message.author.id
    now = datetime.datetime.now().timestamp()
    if uid not in spam_tracker: spam_tracker[uid] = []
    spam_tracker[uid].append(now)
    spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]

    if len(spam_tracker[uid]) > 5:
        punishment_history[uid] = punishment_history.get(uid, 0) + 1
        level = punishment_history[uid]
        emb = discord.Embed(title="🔇 مخالفة سبام", color=discord.Color.light_grey())
        emb.add_field(name="العضو", value=message.author.mention)

        if level == 1:
            try: await message.author.timeout(datetime.timedelta(minutes=10))
            except: pass
            emb.add_field(name="العقوبة", value="تايم أوت 10 دقائق")
        elif level == 2:
            try: await message.author.timeout(datetime.timedelta(minutes=30))
            except: pass
            emb.add_field(name="العقوبة", value="تايم أوت 30 دقيقة")
        else:
            try: await message.author.kick(reason="Spam Protection Limit")
            except: pass
            emb.add_field(name="العقوبة", value="طرد نهائي (Kick)")
            punishment_history[uid] = 0 # تصفير بعد الطرد

        await send_to_logs(message.guild, emb)
        return

    await bot.process_commands(message)

# --- 7. الأوامر الصوتية والإدارية و !help_me ---
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ دخلت الروم الصوتي.")
    else: await ctx.send("❌ ادخل روم صوتي أولاً!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 تم الخروج من الروم.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 تم مسح {amount} رسالة.", delete_after=3)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل القناة.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح القناة.")

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ لوحة تحكم Security BartX Ultimate", color=discord.Color.gold())
    emb.add_field(name="🎙️ الصوت", value="`!join`, `!leave`", inline=True)
    emb.add_field(name="🧹 الإدارة", value="`!clear`, `!lock`, `!unlock`", inline=True)
    emb.add_field(name="🚫 الأنظمة التلقائية", value="منع البان وفكه، منع الويب هوك، الروابط، الصور، والسبام (10د/30د/طرد).", inline=False)
    emb.set_footer(text="كل الأنظمة الأمنية تعمل بكفاءة")
    await ctx.send(embed=emb)

# --- 8. تشغيل البوت ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
