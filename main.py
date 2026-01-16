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

# --- 2. إعدادات البوت والقوائم ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

spam_tracker = {}
punishment_history = {}

@bot.event
async def on_ready():
    print(f'--- [ Security BartX: تم تفعيل حماية البان الفوري ] ---')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

def get_log_channel(guild):
    return discord.utils.get(guild.text_channels, name='logs-security')

# --- 3. نظام Anti-Nuke المطور (الويب هوك وفك البان التلقائي) ---

@bot.event
async def on_webhooks_update(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
        if entry.user.id in [channel.guild.owner_id, bot.user.id]: return
        webhooks = await channel.webhooks()
        for wh in webhooks: await wh.delete()
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Webhook Creation")
        except: pass
        log = get_log_channel(channel.guild)
        if log: await log.send(f"⚠️ {entry.user.mention} حاول إنشاء ويب هوك وتم منعه وسحب رتبه.")

@bot.event
async def on_member_ban(guild, user):
    """نظام فك البان التلقائي ومعاقبة المشرف"""
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        mod = entry.user
        # استثناء المالك والبوت من العقاب
        if mod.id in [guild.owner_id, bot.user.id]: return
        
        # 1. معاقبة المشرف بسحب جميع رتبه فوراً
        try: 
            await mod.edit(roles=[], reason="Anti-Nuke: Unauthorized Ban Attempt")
        except Exception as e:
            print(f"Error removing roles: {e}")
            
        # 2. فك البان عن العضو المظلوم فوراً ليعود قادراً على الدخول
        try:
            await guild.unban(user, reason="Anti-Nuke: Automatic Protection Triggered")
        except Exception as e:
            print(f"Error unbanning user: {e}")

        # 3. إرسال تقرير مفصل في روم السجلات
        log_chan = get_log_channel(guild)
        if log_chan:
            emb = discord.Embed(title="🛡️ حماية من البان العشوائي", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
            emb.add_field(name="المشرف المخالف:", value=f"{mod.mention} ({mod.id})", inline=False)
            emb.add_field(name="العضو المستهدف:", value=f"{user.name} ({user.id})", inline=False)
            emb.add_field(name="الإجراء المتخذ:", value="تم سحب رتب المشرف وإلغاء الحظر عن العضو فوراً.", inline=False)
            emb.set_footer(text="نظام حماية BartX")
            await log_chan.send(embed=emb)

# --- 4. حماية الرومات والرتب ---
@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id in [channel.guild.owner_id, bot.user.id]: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Channel Delete")
        except: pass

@bot.event
async def on_guild_role_update(before, after):
    async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update, limit=1):
        if entry.user.id in [after.guild.owner_id, bot.user.id]: return
        try: await entry.user.edit(roles=[], reason="Anti-Nuke: Role Change")
        except: pass

# --- 5. حماية الشات (سبام، روابط، صور) ---
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

        # نظام السبام
        current_time = datetime.datetime.now().timestamp()
        if user_id not in spam_tracker: spam_tracker[user_id] = []
        spam_tracker[user_id].append(current_time)
        spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t < 5]
        
        if len(spam_tracker[user_id]) > 5:
            punishment_history[user_id] = punishment_history.get(user_id, 0) + 1
            if punishment_history[user_id] == 1:
                try: await message.author.timeout(datetime.timedelta(minutes=10))
                except: pass
            elif punishment_history[user_id] >= 2:
                try: await message.author.kick()
                except: pass
            return

    await bot.process_commands(message)

# --- 6. الأوامر (صوت + إدارة) ---
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ متصل.")
    else: await ctx.send("ادخل روم صوتي!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ Security BartX Ultimate Shield", color=discord.Color.blue())
    emb.description = "البوت محمي ضد: البان، الويب هوك، حذف الرومات، تعديل الرتب، الروابط، الصور، والسبام."
    emb.add_field(name="الأوامر", value="`!join`, `!clear`, `!help_me`", inline=False)
    await ctx.send(embed=emb)

# --- 7. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
