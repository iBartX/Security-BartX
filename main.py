import os
import discord
from discord.ext import commands
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- 1. نظام الاستضافة لضمان العمل 24/7 ---
app = Flask('')
@app.route('/')
def home(): return "Security BartX Ultimate Shield is ONLINE 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# --- 2. إعدادات البوت والبيانات ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# مخازن بيانات السبام وتاريخ العقوبات
spam_tracker = {}
punishment_history = {}

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"✅ تم تشغيل البوت الشامل: {bot.user.name}")
    print(f"📡 مراقبة السجلات: نشطة 100%")
    print(f"🛡️ حماية الاونر والسيادة: مفعلة")
    print(f"========================================")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="أمن السيرفر | !help_me"))

# دالة إرسال السجلات الموحدة (Embeds)
async def send_to_logs(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs-security')
    if log_channel:
        try:
            await log_channel.send(embed=embed)
        except:
            pass

# --- 3. نظام حماية "السيادة" (منع إنشاء الرومات لغير الاونر) ---
@bot.event
async def on_guild_channel_create(channel):
    await asyncio.sleep(1.5)
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
        mod = entry.user
        if mod.id == channel.guild.owner_id or mod.id == bot.user.id:
            return
        
        # حذف الروم فوراً
        await channel.delete(reason="Anti-Nuke: Sovereignty Protocol (Owner Only)")
        
        # سحب كافة الرتب من الفاعل مهما كان منصبه
        try:
            await mod.edit(roles=[], reason="Anti-Nuke: Attempted Channel Creation without Permission")
        except:
            pass

        emb = discord.Embed(title="🚨 خرق أمني: إنشاء قناة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        emb.add_field(name="الفاعل (المخالف)", value=f"{mod.mention} ({mod.id})", inline=False)
        emb.add_field(name="اسم القناة المحذوفة", value=channel.name, inline=True)
        emb.add_field(name="الإجراء المتخذ", value="تم حذف القناة وسحب كافة الرتب فوراً", inline=True)
        emb.set_footer(text="نظام حماية سيادة صاحب السيرفر")
        await send_to_logs(channel.guild, emb)

# --- 4. سجلات مراقبة الرسائل (حذف وتعديل) ---
@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    emb = discord.Embed(title="🗑️ مراقبة الرسائل: حذف", color=discord.Color.orange(), timestamp=datetime.datetime.utcnow())
    emb.add_field(name="الكاتب", value=message.author.mention, inline=True)
    emb.add_field(name="القناة", value=message.channel.mention, inline=True)
    emb.add_field(name="المحتوى المحذوف", value=message.content or "صورة أو ملف مرفق", inline=False)
    await send_to_logs(message.guild, emb)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    emb = discord.Embed(title="📝 مراقبة الرسائل: تعديل", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    emb.add_field(name="الكاتب", value=before.author.mention, inline=True)
    emb.add_field(name="النص قبل التعديل", value=before.content, inline=False)
    emb.add_field(name="النص بعد التعديل", value=after.content, inline=False)
    await send_to_logs(before.guild, emb)

# --- 5. سجلات مراقبة الرتب والأعضاء (كاملة) ---
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        emb = discord.Embed(title="🎭 سجل تغيير الرتب", color=discord.Color.teal(), timestamp=datetime.datetime.utcnow())
        emb.add_field(name="العضو المعني", value=after.mention)
        
        added = [role.mention for role in after.roles if role not in before.roles]
        removed = [role.mention for role in before.roles if role not in after.roles]
        
        if added: emb.add_field(name="رتب تم منحها ✅", value=", ".join(added), inline=False)
        if removed: emb.add_field(name="رتب تم سحبها ❌", value=", ".join(removed), inline=False)
        await send_to_logs(after.guild, emb)

@bot.event
async def on_guild_role_create(role):
    async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=1):
        mod = entry.user
        emb = discord.Embed(title="✨ سجل الرتب: إنشاء", color=discord.Color.green())
        emb.add_field(name="الرتبة المنشأة", value=role.name)
        emb.add_field(name="بواسطة", value=mod.mention)
        await send_to_logs(role.guild, emb)

# --- 6. حماية Anti-Nuke (بان، ويب هوك، حذف رومات) ---
@bot.event
async def on_member_ban(guild, user):
    await asyncio.sleep(2)
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban, limit=1):
        if entry.target.id == user.id:
            mod = entry.user
            if mod.id == guild.owner_id or mod.id == bot.user.id: return
            try: await mod.edit(roles=[], reason="Anti-Nuke: Ban")
            except: pass
            try: await guild.unban(user)
            except: pass
            emb = discord.Embed(title="🚨 منع بان تخريبي", color=discord.Color.red())
            emb.add_field(name="المشرف", value=mod.mention); emb.add_field(name="الضحية", value=user.name)
            await send_to_logs(guild, emb)

@bot.event
async def on_webhooks_update(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.webhook_create, limit=1):
        mod = entry.user
        if mod.id in [channel.guild.owner_id, bot.user.id]: return
        for wh in await channel.webhooks(): await wh.delete()
        try: await mod.edit(roles=[], reason="Anti-Nuke: Webhook")
        except: pass
        emb = discord.Embed(title="🚫 منع ويب هوك", color=discord.Color.orange())
        emb.add_field(name="الفاعل", value=mod.mention)
        await send_to_logs(channel.guild, emb)

# --- 7. حماية الشات ونظام السبام (10د/30د/طرد) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    # المشرفين مستثنون من حماية الشات فقط لضمان عمل الأوامر
    if not message.author.guild_permissions.manage_messages:
        # منع الروابط والصور لغير الإدارة
        if any(x in message.content.lower() for x in ["http", "discord.gg", "www."]) or message.attachments:
            try: await message.delete()
            except: pass
            return

        # نظام السبام المطور
        uid = message.author.id
        now = datetime.datetime.now().timestamp()
        if uid not in spam_tracker: spam_tracker[uid] = []
        spam_tracker[uid].append(now)
        spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 5]
        
        if len(spam_tracker[uid]) > 5:
            punishment_history[uid] = punishment_history.get(uid, 0) + 1
            lvl = punishment_history[uid]
            
            emb = discord.Embed(title="🔇 سجل العقوبات: سبام", color=discord.Color.dark_grey())
            emb.add_field(name="العضو", value=message.author.mention)

            if lvl == 1:
                try: await message.author.timeout(datetime.timedelta(minutes=10))
                except: pass
                emb.add_field(name="العقوبة", value="تايم أوت 10 دقائق")
            elif lvl == 2:
                try: await message.author.timeout(datetime.timedelta(minutes=30))
                except: pass
                emb.add_field(name="العقوبة", value="تايم أوت 30 دقيقة")
            else:
                try: await message.author.kick(reason="Spam Protection")
                except: pass
                emb.add_field(name="العقوبة", value="طرد نهائي (Kick)")
                punishment_history[uid] = 0

            await send_to_logs(message.guild, emb)
            return

    await bot.process_commands(message)

# --- 8. الأوامر الكاملة (صوت + إدارة + مساعدة) ---
@bot.command()
async def join(ctx):
    if ctx.author.voice: await ctx.author.voice.channel.connect(); await ctx.send("✅ تم الدخول.")
@bot.command()
async def leave(ctx):
    if ctx.voice_client: await ctx.voice_client.disconnect(); await ctx.send("👋 تم الخروج.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False); await ctx.send("🔒")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True); await ctx.send("🔓")

@bot.command()
async def help_me(ctx):
    emb = discord.Embed(title="🛡️ Security BartX Ultimate Help Center", color=discord.Color.gold())
    emb.add_field(name="🎙️ الأوامر الصوتية", value="`!join` | `!leave`", inline=True)
    emb.add_field(name="🧹 الأوامر الإدارية", value="`!clear` | `!lock` | `!unlock`", inline=True)
    emb.add_field(name="🚫 أنظمة الحماية التلقائية", value="• منع الرومات (أونر فقط)\n• منع البان التخريبي\n• منع الويب هوك\n• نظام السبام (10د/30د/طرد)\n• مراقبة شاملة لكل أحداث السيرفر", inline=False)
    emb.set_footer(text="نظام مراقبة السيرفر يعمل بكفاءة كاملة")
    await ctx.send(embed=emb)

# --- 9. التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('TOKEN'))
