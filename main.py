import os
import json
import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from flask import Flask, request
from threading import Thread
import traceback
import re

# ================== 1️⃣ KEEP ALIVE ==================
app = Flask('')

@app.route('/')
def home():
    return "Security BartX Ultimate Shield ONLINE"

@app.route("/dashboard")
def dashboard():
    try:
        # Load config safely
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {
                "security_enabled": True,
                "anti_nuke": True,
                "whitelist_users": [],
                "whitelist_roles": [],
                "rate_limits": {"messages": [5, 5]},
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10},
                "anti_spam": True,
                "anti_links": True,
                "anti_images": True,
                "max_warnings": 3,
                "punishments": {
                    "warn1": "timeout",
                    "warn2": "kick",
                    "warn3": "ban"
                }
            }
            
        return f"""
        <html dir="rtl">
        <head>
            <title>لوحة التحكم الأمنية</title>
            <meta charset="UTF-8">
            <style>
                body {{ background:#0f172a;color:white;font-family:Tahoma,Arial,sans-serif;padding:20px }}
                .container {{ max-width:800px;margin:0 auto }}
                h1 {{ color:#22c55e;border-bottom:2px solid #334155;padding-bottom:10px }}
                .status {{ background:#1e293b;padding:15px;border-radius:10px;margin:15px 0 }}
                .btn {{ padding:12px 20px;margin:10px 5px;background:#22c55e;border:none;color:white;cursor:pointer;border-radius:5px;font-size:16px }}
                .btn:hover {{ background:#16a34a }}
                a {{ color:#60a5fa;text-decoration:none }}
                .box {{ background:#1e293b;padding:20px;border-radius:10px;margin:20px 0 }}
                .toggle {{ display:flex;justify-content:space-between;align-items:center;margin:10px 0 }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ Security BartX Control Panel</h1>
                
                <div class="box">
                    <h2>📊 حالة النظام</h2>
                    <div class="toggle">
                        <span>🔒 Anti-Nuke:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_nuke', True) else '❌ معطل'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🛡️ الحماية:</span>
                        <strong>{'✅ مفعلة' if cfg.get('security_enabled', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🚫 منع السبام:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_spam', True) else '❌ معطل'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🔗 منع الروابط:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_links', True) else '❌ معطل'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🖼️ منع الصور:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_images', True) else '❌ معطل'}</strong>
                    </div>
                    <div class="toggle">
                        <span>👥 أعضاء الوايت ليست:</span>
                        <strong>{len(cfg.get('whitelist_users', []))}</strong>
                    </div>
                    <div class="toggle">
                        <span>🎖️ رتب الوايت ليست:</span>
                        <strong>{len(cfg.get('whitelist_roles', []))}</strong>
                    </div>
                </div>
                
                <div class="box">
                    <h2>🎮 التحكم السريع</h2>
                    <form action="/toggle_nuke" method="post">
                        <button class="btn" type="submit">🔁 تبديل Anti-Nuke</button>
                    </form>
                    <form action="/toggle_security" method="post">
                        <button class="btn" type="submit">⚡ تبديل الحماية</button>
                    </form>
                    <form action="/toggle_spam" method="post">
                        <button class="btn" type="submit">🔄 تبديل منع السبام</button>
                    </form>
                    <form action="/toggle_links" method="post">
                        <button class="btn" type="submit">🔗 تبديل منع الروابط</button>
                    </form>
                    <form action="/backup_now" method="post">
                        <button class="btn" type="submit">💾 إنشاء نسخة احتياطية</button>
                    </form>
                </div>
                
                <div class="box">
                    <h2>⚙️ إعدادات العقوبات</h2>
                    <p>التحذير الأول: <strong>{cfg.get('punishments', {}).get('warn1', 'timeout')}</strong></p>
                    <p>التحذير الثاني: <strong>{cfg.get('punishments', {}).get('warn2', 'kick')}</strong></p>
                    <p>التحذير الثالث: <strong>{cfg.get('punishments', {}).get('warn3', 'ban')}</strong></p>
                    <p>الحد الأقصى للتحذيرات: <strong>{cfg.get('max_warnings', 3)}</strong></p>
                </div>
                
                <p style="text-align:center;margin-top:30px;color:#94a3b8">
                    © 2024 Security BartX Ultimate Shield v4.0
                </p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ في التحميل</h1><p>{str(e)}</p>"

@app.route("/toggle_nuke", methods=['POST'])
def toggle_nuke():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {
                "security_enabled": True,
                "anti_nuke": True,
                "whitelist_users": [],
                "whitelist_roles": [],
                "rate_limits": {"messages": [5, 5]},
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10},
                "anti_spam": True,
                "anti_links": True,
                "anti_images": True,
                "max_warnings": 3,
                "punishments": {
                    "warn1": "timeout",
                    "warn2": "kick",
                    "warn3": "ban"
                }
            }
        
        current_state = cfg.get("anti_nuke", True)
        cfg["anti_nuke"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعل" if cfg["anti_nuke"] else "معطل"
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم التغيير بنجاح</h2>
                <p>Anti-Nuke الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_security", methods=['POST'])
def toggle_security():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {
                "security_enabled": True,
                "anti_nuke": True,
                "whitelist_users": [],
                "whitelist_roles": [],
                "rate_limits": {"messages": [5, 5]},
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10},
                "anti_spam": True,
                "anti_links": True,
                "anti_images": True,
                "max_warnings": 3,
                "punishments": {
                    "warn1": "timeout",
                    "warn2": "kick",
                    "warn3": "ban"
                }
            }
        
        current_state = cfg.get("security_enabled", True)
        cfg["security_enabled"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعلة" if cfg["security_enabled"] else "معطلة"
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم التغيير بنجاح</h2>
                <p>الحماية الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_spam", methods=['POST'])
def toggle_spam():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {
                "security_enabled": True,
                "anti_nuke": True,
                "whitelist_users": [],
                "whitelist_roles": [],
                "rate_limits": {"messages": [5, 5]},
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10},
                "anti_spam": True,
                "anti_links": True,
                "anti_images": True,
                "max_warnings": 3,
                "punishments": {
                    "warn1": "timeout",
                    "warn2": "kick",
                    "warn3": "ban"
                }
            }
        
        current_state = cfg.get("anti_spam", True)
        cfg["anti_spam"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعل" if cfg["anti_spam"] else "معطل"
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم التغيير بنجاح</h2>
                <p>منع السبام الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_links", methods=['POST'])
def toggle_links():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {
                "security_enabled": True,
                "anti_nuke": True,
                "whitelist_users": [],
                "whitelist_roles": [],
                "rate_limits": {"messages": [5, 5]},
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10},
                "anti_spam": True,
                "anti_links": True,
                "anti_images": True,
                "max_warnings": 3,
                "punishments": {
                    "warn1": "timeout",
                    "warn2": "kick",
                    "warn3": "ban"
                }
            }
        
        current_state = cfg.get("anti_links", True)
        cfg["anti_links"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعل" if cfg["anti_links"] else "معطل"
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم التغيير بنجاح</h2>
                <p>منع الروابط الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/backup_now", methods=['POST'])
def backup_now():
    try:
        # Create backup directory if not exists
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        # Create simple backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/backup_{timestamp}.json"
        
        # Save current config
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        
        # Clean old backups (keep only 10)
        if os.path.exists('backups'):
            backups = sorted(os.listdir('backups'))
            if len(backups) > 10:
                for old_backup in backups[:-10]:
                    os.remove(f"backups/{old_backup}")
        
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم إنشاء النسخة الاحتياطية</h2>
                <p>تم حفظ النسخة في: <strong>{backup_path}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    Thread(target=run, daemon=True).start()

# ================== 2️⃣ BOT SETUP ==================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================== 3️⃣ JSON CONFIG ==================
CONFIG_FILE = "security_config.json"
BACKUP_DIR = "backups"
WARNINGS_FILE = "warnings.json"
os.makedirs(BACKUP_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "security_enabled": True,
    "anti_nuke": True,
    "whitelist_users": [],
    "whitelist_roles": [],
    "rate_limits": {
        "messages": [5, 5]
    },
    "backup": {
        "enabled": True,
        "interval_minutes": 30,
        "max_backups": 10
    },
    "anti_spam": True,
    "anti_links": True,
    "anti_images": True,
    "anti_role_edit": True,
    "anti_channel_edit": True,
    "max_warnings": 3,
    "punishments": {
        "warn1": "timeout",
        "warn2": "kick",
        "warn3": "ban"
    }
}

def load_config():
    try:
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG.copy()
        
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في تحميل الإعدادات: {e}")
        return DEFAULT_CONFIG.copy()

def save_config():
    try:
        data = {
            "security_enabled": SECURITY_ENABLED,
            "anti_nuke": ANTI_NUKE_ENABLED,
            "whitelist_users": list(WHITELIST_USERS),
            "whitelist_roles": list(WHITELIST_ROLES),
            "rate_limits": RATE_LIMITS,
            "backup": {
                "enabled": BACKUP_ENABLED,
                "interval_minutes": BACKUP_INTERVAL,
                "max_backups": MAX_BACKUPS
            },
            "anti_spam": ANTI_SPAM_ENABLED,
            "anti_links": ANTI_LINKS_ENABLED,
            "anti_images": ANTI_IMAGES_ENABLED,
            "anti_role_edit": ANTI_ROLE_EDIT_ENABLED,
            "anti_channel_edit": ANTI_CHANNEL_EDIT_ENABLED,
            "max_warnings": MAX_WARNINGS,
            "punishments": PUNISHMENTS
        }
        
        # Create backup before change
        if BACKUP_ENABLED:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{BACKUP_DIR}/before_change_{timestamp}.json"
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    old_config = json.load(f)
                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(old_config, f, indent=4)
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ خطأ في حفظ الإعدادات: {e}")

def load_warnings():
    try:
        if not os.path.exists(WARNINGS_FILE):
            return {}
        with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في تحميل التحذيرات: {e}")
        return {}

def save_warnings(warnings_data):
    try:
        with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(warnings_data, f, indent=4)
    except Exception as e:
        print(f"❌ خطأ في حفظ التحذيرات: {e}")

# Load initial config
config = load_config()

SECURITY_ENABLED = config["security_enabled"]
ANTI_NUKE_ENABLED = config["anti_nuke"]
WHITELIST_USERS = set(config["whitelist_users"])
WHITELIST_ROLES = set(config["whitelist_roles"])
RATE_LIMITS = config["rate_limits"]

BACKUP_ENABLED = config["backup"]["enabled"]
BACKUP_INTERVAL = config["backup"]["interval_minutes"]
MAX_BACKUPS = config["backup"]["max_backups"]

ANTI_SPAM_ENABLED = config.get("anti_spam", True)
ANTI_LINKS_ENABLED = config.get("anti_links", True)
ANTI_IMAGES_ENABLED = config.get("anti_images", True)
ANTI_ROLE_EDIT_ENABLED = config.get("anti_role_edit", True)
ANTI_CHANNEL_EDIT_ENABLED = config.get("anti_channel_edit", True)
MAX_WARNINGS = config.get("max_warnings", 3)
PUNISHMENTS = config.get("punishments", {
    "warn1": "timeout",
    "warn2": "kick",
    "warn3": "ban"
})

# ================== 4️⃣ GLOBAL STATE ==================
rate_cache = {}
nuke_tracker = {}
NUKE_LIMIT = 3
NUKE_WINDOW = 8
spam_tracker = {}
warnings = load_warnings()
voice_connections = {}

# URL patterns for detection
URL_PATTERNS = [
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'discord\.gg/[a-zA-Z0-9]+',
    r'discord\.com/invite/[a-zA-Z0-9]+'
]

# ================== 5️⃣ READY ==================
@bot.event
async def on_ready():
    print(f"🛡️ {bot.user} ONLINE | JSON CONFIG LOADED")
    print(f"📊 عدد السيرفرات: {len(bot.guilds)}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="حماية السيرفر | !الحماية"
        )
    )
    
    # Start backup task if enabled
    if BACKUP_ENABLED:
        auto_backup.start()
        print(f"✅ نظام النسخ الاحتياطي مفعل (كل {BACKUP_INTERVAL} دقيقة)")
    
    print("✅ نظام التحذيرات والعقوبات مفعل")
    print("✅ نظام منع السبام والروابط والصور مفعل")

# ================== 6️⃣ LOG SYSTEM ==================
async def send_to_logs(guild, embed):
    try:
        # Try to find logs channel
        for channel in guild.text_channels:
            if "logs" in channel.name.lower() or "سجلات" in channel.name:
                await channel.send(embed=embed)
                return
        
        # If not found, try to create one
        try:
            logs_channel = await guild.create_text_channel(
                "logs-security",
                reason="قناة سجلات الحماية"
            )
            await logs_channel.send(embed=embed)
        except:
            pass  # No permission to create channel
    except:
        pass  # Ignore logging errors

# ================== 7️⃣ WHITELIST ==================
def is_whitelisted(member):
    if member.id == member.guild.owner_id:
        return True
    if member.id == bot.user.id:
        return True
    if member.id in WHITELIST_USERS:
        return True
    return any(role.id in WHITELIST_ROLES for role in member.roles)

# ================== 8️⃣ WARNING SYSTEM ==================
async def add_warning(member, reason, moderator=None):
    try:
        guild_id = str(member.guild.id)
        user_id = str(member.id)
        
        if guild_id not in warnings:
            warnings[guild_id] = {}
        
        if user_id not in warnings[guild_id]:
            warnings[guild_id][user_id] = []
        
        warning = {
            "timestamp": datetime.datetime.now().isoformat(),
            "reason": reason,
            "moderator": moderator.id if moderator else "النظام",
            "moderator_name": moderator.name if moderator else "النظام التلقائي"
        }
        
        warnings[guild_id][user_id].append(warning)
        
        # Keep only last 10 warnings per user
        if len(warnings[guild_id][user_id]) > 10:
            warnings[guild_id][user_id] = warnings[guild_id][user_id][-10:]
        
        save_warnings(warnings)
        
        # Apply punishment based on warning count
        warning_count = len(warnings[guild_id][user_id])
        await apply_punishment(member, warning_count, reason)
        
        return warning_count
    except Exception as e:
        print(f"❌ خطأ في إضافة تحذير: {e}")
        return 0

async def apply_punishment(member, warning_count, reason):
    try:
        if warning_count == 1 and PUNISHMENTS.get("warn1") == "timeout":
            # Timeout for 1 hour
            await member.timeout(datetime.timedelta(hours=1), reason=f"تحذير أول: {reason}")
            await send_warning_dm(member, 1, reason, "تقييد لمدة ساعة")
            
        elif warning_count == 2 and PUNISHMENTS.get("warn2") == "kick":
            # Kick member
            if member.guild.me.guild_permissions.kick_members:
                await member.kick(reason=f"تحذير ثاني: {reason}")
                await send_warning_dm(member, 2, reason, "طرد من السيرفر")
                
        elif warning_count >= MAX_WARNINGS and PUNISHMENTS.get("warn3") == "ban":
            # Ban member
            if member.guild.me.guild_permissions.ban_members:
                await member.ban(reason=f"تحذير ثالث: {reason}", delete_message_days=1)
                await send_warning_dm(member, 3, reason, "حظر دائم")
        
        # Log the punishment
        embed = discord.Embed(
            title="⚠️ تطبيق عقوبة",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 العضو", value=f"{member.mention} ({member.id})", inline=False)
        embed.add_field(name="📝 السبب", value=reason, inline=False)
        embed.add_field(name="📊 عدد التحذيرات", value=str(warning_count), inline=False)
        embed.add_field(name="⚖️ العقوبة", value=get_punishment_name(warning_count), inline=False)
        
        await send_to_logs(member.guild, embed)
        
    except discord.Forbidden:
        print(f"⛔ لا يوجد صلاحيات لتطبيق العقوبة على {member}")
    except Exception as e:
        print(f"❌ خطأ في تطبيق العقوبة: {e}")

async def send_warning_dm(member, warning_count, reason, punishment):
    try:
        embed = discord.Embed(
            title="⚠️ تحذير أمني",
            description=f"لقد تلقيت تحذيراً في سيرفر **{member.guild.name}**",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="📝 السبب", value=reason, inline=False)
        embed.add_field(name="📊 عدد التحذيرات", value=f"{warning_count}/{MAX_WARNINGS}", inline=False)
        embed.add_field(name="⚖️ العقوبة", value=punishment, inline=False)
        embed.set_footer(text="Security BartX Ultimate Shield")
        
        await member.send(embed=embed)
    except:
        pass  # Can't send DM

def get_punishment_name(warning_count):
    if warning_count == 1:
        return "تقييد مؤقت"
    elif warning_count == 2:
        return "طرد"
    elif warning_count >= 3:
        return "حظر دائم"
    return "تحذير"

# ================== 9️⃣ CONTENT FILTERING ==================
def contains_links(text):
    """Check if text contains URLs"""
    for pattern in URL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def is_spam(user_id, guild_id):
    """Check if user is spamming"""
    now = datetime.datetime.utcnow().timestamp()
    key = f"{guild_id}_{user_id}"
    
    if key not in spam_tracker:
        spam_tracker[key] = []
    
    spam_tracker[key].append(now)
    
    # Keep only messages from last 10 seconds
    spam_tracker[key] = [t for t in spam_tracker[key] if now - t < 10]
    
    # If more than 5 messages in 10 seconds, it's spam
    return len(spam_tracker[key]) > 5

async def handle_violation(member, violation_type, content=None):
    """Handle security violations"""
    if is_whitelisted(member):
        return False
    
    reason_messages = {
        "spam": "إرسال رسائل متكررة بشكل مفرط",
        "links": "إرسال روابط غير مسموح بها",
        "images": "إرسال صور غير مسموح بها",
        "role_edit": "تعديل الرتب بدون صلاحية",
        "channel_edit": "تعديل الرومات بدون صلاحية"
    }
    
    reason = reason_messages.get(violation_type, "انتهاك قواعد السيرفر")
    
    # Delete violating message if possible
    try:
        if content and hasattr(content, 'delete'):
            await content.delete()
    except:
        pass
    
    # Add warning
    warning_count = await add_warning(member, reason)
    
    # Send alert to channel
    alert_embed = discord.Embed(
        title="🚨 انتهاك أمني",
        description=f"{member.mention} قام بانتهاك قواعد السيرفر",
        color=discord.Color.red()
    )
    alert_embed.add_field(name="📝 نوع الانتهاك", value=reason, inline=False)
    alert_embed.add_field(name="📊 عدد التحذيرات", value=f"{warning_count}/{MAX_WARNINGS}", inline=False)
    
    try:
        await member.guild.system_channel.send(embed=alert_embed)
    except:
        pass
    
    return True

# ================== 🔟 MESSAGE FILTERING ==================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Skip if security is disabled or user is whitelisted
    if not SECURITY_ENABLED or is_whitelisted(message.author):
        return
    
    guild_id = message.guild.id
    user_id = message.author.id
    
    # 1. Check for spam
    if ANTI_SPAM_ENABLED and is_spam(user_id, guild_id):
        await handle_violation(message.author, "spam", message)
        return
    
    # 2. Check for links
    if ANTI_LINKS_ENABLED and contains_links(message.content):
        await handle_violation(message.author, "links", message)
        return
    
    # 3. Check for images
    if ANTI_IMAGES_ENABLED and message.attachments:
        # Check if any attachment is an image
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                await handle_violation(message.author, "images", message)
                return
    
    # 4. Check rate limiting
    limit, window = RATE_LIMITS.get("messages", [5, 5])
    if rate_limited(message.author.id, "msg", limit, window):
        try:
            if message.guild.me.guild_permissions.moderate_members:
                await message.author.timeout(
                    datetime.timedelta(minutes=5),
                    reason="تجاوز حد الرسائل"
                )
                embed = discord.Embed(
                    title="⏰ تم تقييد المستخدم",
                    description=f"المستخدم {message.author.mention} تجاوز حد الرسائل المسموح بها",
                    color=discord.Color.orange()
                )
                await send_to_logs(message.guild, embed)
        except:
            pass

# ================== 1️⃣1️⃣ ROLE & CHANNEL PROTECTION ==================
@bot.event
async def on_guild_role_update(before, after):
    """Detect role modifications"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # Check if role was modified
    if (before.name != after.name or 
        before.permissions != after.permissions or
        before.color != after.color or
        before.hoist != after.hoist):
        
        mod = await safe_executor(after.guild, discord.AuditLogAction.role_update, after.id)
        if mod and not is_whitelisted(mod):
            await handle_violation(mod, "role_edit")
            # Revert changes if possible
            try:
                if after.guild.me.guild_permissions.manage_roles:
                    await after.edit(
                        name=before.name,
                        permissions=before.permissions,
                        color=before.color,
                        hoist=before.hoist,
                        reason="استعادة تعديل غير مصرح به"
                    )
            except:
                pass

@bot.event
async def on_guild_channel_update(before, after):
    """Detect channel modifications"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # Check if channel was modified
    if (before.name != after.name or 
        before.position != after.position or
        before.category != after.category):
        
        mod = await safe_executor(after.guild, discord.AuditLogAction.channel_update, after.id)
        if mod and not is_whitelisted(mod):
            await handle_violation(mod, "channel_edit")
            # Revert changes if possible
            try:
                if after.guild.me.guild_permissions.manage_channels:
                    await after.edit(
                        name=before.name,
                        position=before.position,
                        category=before.category,
                        reason="استعادة تعديل غير مصرح به"
                    )
            except:
                pass

# ================== 1️⃣2️⃣ NUKE PROTECTION ==================
async def safe_executor(guild, action, target_id):
    try:
        async for entry in guild.audit_logs(limit=10, action=action):
            if entry.target and getattr(entry.target, 'id', None) == target_id:
                if (datetime.datetime.utcnow() - entry.created_at).total_seconds() < 10:
                    return entry.user
        return None
    except discord.Forbidden:
        print(f"⛔ لا يوجد صلاحية لسجلات التدقيق في {guild.name}")
        return None
    except Exception as e:
        print(f"⚠️ خطأ في سجلات التدقيق: {e}")
        return None

async def handle_nuke(member, reason):
    if is_whitelisted(member):
        return
    
    now = datetime.datetime.utcnow().timestamp()
    uid = member.id
    nuke_tracker.setdefault(uid, [])
    nuke_tracker[uid].append(now)
    nuke_tracker[uid] = [t for t in nuke_tracker[uid] if now - t < NUKE_WINDOW]
    
    if len(nuke_tracker[uid]) >= NUKE_LIMIT:
        try:
            # Remove all roles
            if member.guild.me.guild_permissions.manage_roles:
                await member.edit(roles=[], reason="هجوم تخريبي - إزالة الرتب")
            
            # Ban the user
            if member.guild.me.guild_permissions.ban_members:
                await member.ban(reason=f"هجوم تخريبي: {reason}", delete_message_days=1)
            
            # Create log embed
            embed = discord.Embed(
                title="💣 تم إيقاف هجوم تخريبي",
                description=f"تم حظر المستخدم بسبب نشاط تخريبي",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.add_field(name="👤 المستخدم", value=f"{member.mention}\n{member.id}", inline=True)
            embed.add_field(name="📝 السبب", value=reason, inline=True)
            embed.add_field(name="📊 عدد الأنشطة", value=str(len(nuke_tracker[uid])), inline=True)
            embed.set_footer(text="Security BartX Ultimate Shield")
            
            await send_to_logs(member.guild, embed)
            
            # Reset tracker
            nuke_tracker[uid] = []
            
        except discord.Forbidden:
            print(f"⛔ لا يوجد صلاحيات لاتخاذ إجراء ضد {member}")
        except Exception as e:
            print(f"⚠️ خطأ في معالجة الهجوم: {e}")

@bot.event
async def on_guild_channel_delete(channel):
    if not SECURITY_ENABLED or not ANTI_NUKE_ENABLED:
        return
    
    mod = await safe_executor(channel.guild, discord.AuditLogAction.channel_delete, channel.id)
    if mod:
        await handle_nuke(mod, "حذف قنوات")

@bot.event
async def on_guild_role_delete(role):
    if not SECURITY_ENABLED or not ANTI_NUKE_ENABLED:
        return
    
    mod = await safe_executor(role.guild, discord.AuditLogAction.role_delete, role.id)
    if mod:
        await handle_nuke(mod, "حذف رتب")

# ================== 1️⃣3️⃣ RATE LIMIT ==================
def rate_limited(uid, key, limit, window):
    now = datetime.datetime.utcnow().timestamp()
    cache_key = f"{uid}_{key}"
    
    if cache_key not in rate_cache:
        rate_cache[cache_key] = []
    
    rate_cache[cache_key].append(now)
    
    # Clean old entries
    rate_cache[cache_key] = [t for t in rate_cache[cache_key] if now - t < window]
    
    return len(rate_cache[cache_key]) > limit

# ================== 1️⃣4️⃣ ADMIN COMMANDS ==================
@bot.group()
@commands.has_permissions(administrator=True)
async def الحماية(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ نظام الحماية المتكامل",
            description="أوامر إدارة نظام الحماية الشامل",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="⚙️ إعدادات الحماية",
            value="• `!الحماية تشغيل/إيقاف`\n• `!الحماية الحالة`\n• `!الحماية الإعدادات`",
            inline=False
        )
        embed.add_field(
            name="👥 إدارة التحذيرات",
            value="• `!تحذيرات @عضو`\n• `!إزالة_تحذير @عضو [رقم]`\n• `!مسح_التحذيرات @عضو`",
            inline=False
        )
        embed.add_field(
            name="🎤 أوامر الصوت",
            value="• `!دخول` - دخول الروم الصوتي\n• `!خروج` - خروج من الروم",
            inline=False
        )
        embed.add_field(
            name="🗑️ إدارة المحادثات",
            value="• `!مسح [عدد]`\n• `!اغلاق_الشات`\n• `!فتح_الشات`",
            inline=False
        )
        embed.set_footer(text="Security BartX Ultimate Shield v4.0")
        await ctx.send(embed=embed)

@الحماية.command()
async def الحالة(ctx):
    embed = discord.Embed(
        title="📊 حالة نظام الحماية",
        color=discord.Color.blue()
    )
    embed.add_field(name="🛡️ الحماية", value="✅ مفعل" if SECURITY_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="💣 Anti-Nuke", value="✅ مفعل" if ANTI_NUKE_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🚫 منع السبام", value="✅ مفعل" if ANTI_SPAM_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🔗 منع الروابط", value="✅ مفعل" if ANTI_LINKS_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🖼️ منع الصور", value="✅ مفعل" if ANTI_IMAGES_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="⚖️ عدد التحذيرات", value=str(sum(len(w) for w in warnings.get(str(ctx.guild.id), {}).values())), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="تحذيرات")
@commands.has_permissions(manage_messages=True)
async def show_warnings(ctx, member: discord.Member = None):
    """عرض تحذيرات العضو"""
    if not member:
        member = ctx.author
    
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    user_warnings = warnings.get(guild_id, {}).get(user_id, [])
    
    if not user_warnings:
        embed = discord.Embed(
            title="📝 سجل التحذيرات",
            description=f"{member.mention} ليس لديه أي تحذيرات",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"📝 تحذيرات {member.name}",
        description=f"عدد التحذيرات: **{len(user_warnings)}/{MAX_WARNINGS}**",
        color=discord.Color.orange()
    )
    
    for i, warning in enumerate(user_warnings[-5:], 1):  # Show last 5 warnings
        timestamp = datetime.datetime.fromisoformat(warning["timestamp"]).strftime("%Y-%m-%d %H:%M")
        embed.add_field(
            name=f"تحذير #{i} - {timestamp}",
            value=f"**السبب:** {warning['reason']}\n**المشرف:** {warning['moderator_name']}",
            inline=False
        )
    
    embed.set_footer(text=f"العقوبة التالية: {get_punishment_name(len(user_warnings) + 1)}")
    await ctx.send(embed=embed)

# ================== 1️⃣5️⃣ VOICE COMMANDS ==================
@bot.command(name="دخول", aliases=["join", "connect"])
@commands.has_permissions(manage_channels=True)
async def join_voice(ctx):
    """الدخول إلى الروم الصوتي الحالي"""
    try:
        if ctx.author.voice is None:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون في روم صوتي أولاً",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        voice_channel = ctx.author.voice.channel
        
        if ctx.guild.voice_client is not None:
            if ctx.guild.voice_client.channel == voice_channel:
                embed = discord.Embed(
                    title="ℹ️ معلومة",
                    description="أنا بالفعل متصل في هذا الروم الصوتي",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
                return
            else:
                await ctx.guild.voice_client.move_to(voice_channel)
                embed = discord.Embed(
                    title="✅ تم النقل",
                    description=f"تم الانتقال إلى روم {voice_channel.mention}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                return
        
        voice_client = await voice_channel.connect()
        voice_connections[ctx.guild.id] = voice_client
        
        embed = discord.Embed(
            title="✅ تم الدخول",
            description=f"تم الدخول إلى روم {voice_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الاتصال",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="خروج", aliases=["leave", "disconnect"])
@commands.has_permissions(manage_channels=True)
async def leave_voice(ctx):
    """الخروج من الروم الصوتي"""
    try:
        if ctx.guild.voice_client is None:
            embed = discord.Embed(
                title="❌ خطأ",
                description="أنا لست متصلاً بأي روم صوتي",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.guild.voice_client.disconnect()
        
        if ctx.guild.id in voice_connections:
            del voice_connections[ctx.guild.id]
        
        embed = discord.Embed(
            title="✅ تم الخروج",
            description="تم الخروج من الروم الصوتي بنجاح",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الخروج",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ================== 1️⃣6️⃣ CHAT MANAGEMENT ==================
@bot.command(name="مسح", aliases=["حذف", "clear", "purge"])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    """مسح عدد محدد من الرسائل"""
    try:
        if amount < 1:
            amount = 1
        if amount > 100:
            amount = 100
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        embed = discord.Embed(
            title="🗑️ تم المسح",
            description=f"تم حذف {len(deleted) - 1} رسالة",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)
        
        await asyncio.sleep(3)
        await msg.delete()
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الحذف",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="اغلاق_الشات", aliases=["اقفال", "lock"])
@commands.has_permissions(manage_channels=True)
async def lock_chat(ctx):
    """إغلاق الشات ومنع الكتابة"""
    try:
        channel = ctx.channel
        everyone_role = ctx.guild.default_role
        
        await channel.set_permissions(everyone_role, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 تم إغلاق الشات",
            description=f"تم إغلاق {channel.mention} بنجاح",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الإغلاق",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="فتح_الشات", aliases=["فتح", "unlock"])
@commands.has_permissions(manage_channels=True)
async def unlock_chat(ctx):
    """فتح الشات والسماح بالكتابة"""
    try:
        channel = ctx.channel
        everyone_role = ctx.guild.default_role
        
        await channel.set_permissions(everyone_role, send_messages=True)
        
        embed = discord.Embed(
            title="🔓 تم فتح الشات",
            description=f"تم فتح {channel.mention} بنجاح",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الفتح",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ================== 1️⃣7️⃣ RUN ==================
if __name__ == "__main__":
    try:
        keep_alive()
        print("🌐 خادم الويب يعمل...")
        
        token = os.environ.get("TOKEN")
        if not token:
            print("❌ خطأ: لم يتم العثور على التوكن!")
            print("يرجى تعيين متغير البيئة TOKEN")
            exit(1)
        
        print("🤖 جاري تشغيل البوت...")
        bot.run(token)
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
