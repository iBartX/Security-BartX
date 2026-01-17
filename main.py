import os
import json
import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from flask import Flask, request
from threading import Thread, Lock
import traceback
import re
from collections import defaultdict
import time

# ================== 1️⃣ KEEP ALIVE ==================
app = Flask('')

@app.route('/')
def home():
    return "Security BartX Ultimate Shield ONLINE"

@app.route("/dashboard")
def dashboard():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG.copy()
            
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
                .toggle {{ display:flex;justify-content:space-between;align-items:center;margin:10px 0;padding:8px;background:#0f172a;border-radius:5px }}
                .alert {{ background:#7c2d12;padding:15px;border-radius:10px;margin:20px 0 }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ Security BartX Control Panel</h1>
                
                <div class="alert">
                    <h2>⚠️ نظام الحماية الكامل مفعل</h2>
                    <p>النظام يحمي <strong>جميع جوانب السيرفر</strong> بشكل كامل</p>
                    <p>فقط المالك وأعضاء الوايت ليست يمكنهم التعديل</p>
                </div>
                
                <div class="box">
                    <h2>📊 حالة النظام</h2>
                    <div class="toggle">
                        <span>🛡️ الحماية الشاملة:</span>
                        <strong>{'✅ مفعلة' if cfg.get('security_enabled', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🎖️ حماية الرتب:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_role_edit', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>📁 حماية الرومات:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_channel_edit', True) else '❌ معطلة'}</strong>
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
                </div>
                
                <div class="box">
                    <h2>🎮 التحكم السريع</h2>
                    <form action="/toggle_security" method="post">
                        <button class="btn" type="submit">⚡ تبديل الحماية</button>
                    </form>
                    <form action="/toggle_spam" method="post">
                        <button class="btn" type="submit">🔄 تبديل منع السبام</button>
                    </form>
                    <form action="/backup_now" method="post">
                        <button class="btn" type="submit">💾 إنشاء نسخة احتياطية</button>
                    </form>
                </div>
                
                <div class="box">
                    <h2>⚖️ نظام العقوبات التدريجي</h2>
                    <div class="toggle">
                        <span>المرة الأولى:</span>
                        <strong>⚠️ تحذير فقط</strong>
                    </div>
                    <div class="toggle">
                        <span>المرة الثانية:</span>
                        <strong>⏰ تقييد 10 دقائق</strong>
                    </div>
                    <div class="toggle">
                        <span>المرة الثالثة:</span>
                        <strong>⏰ تقييد 30 دقيقة</strong>
                    </div>
                    <div class="toggle">
                        <span>المرة الرابعة:</span>
                        <strong>⏰ تقييد 60 دقيقة</strong>
                    </div>
                    <div class="toggle">
                        <span>المرة الخامسة:</span>
                        <strong>🚪 طرد</strong>
                    </div>
                    <div class="toggle">
                        <span>المرة السادسة:</span>
                        <strong>🔨 حظر دائم</strong>
                    </div>
                </div>
                
                <p style="text-align:center;margin-top:30px;color:#94a3b8">
                    © 2024 Security BartX Ultimate Shield v8.0
                </p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ في التحميل</h1><p>{str(e)}</p>"

@app.route("/toggle_security", methods=['POST'])
def toggle_security():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG.copy()
        
        current_state = cfg.get("security_enabled", True)
        cfg["security_enabled"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        # تحديث المتغيرات العامة
        reload_config()
        
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
            cfg = DEFAULT_CONFIG.copy()
        
        current_state = cfg.get("anti_spam", True)
        cfg["anti_spam"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        # تحديث المتغيرات العامة
        reload_config()
        
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

@app.route("/backup_now", methods=['POST'])
def backup_now():
    try:
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/backup_{timestamp}.json"
        
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
        
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
LOGS_FILE = "security_logs.json"
os.makedirs(BACKUP_DIR, exist_ok=True)

DEFAULT_CONFIG = {
    "security_enabled": True,
    "anti_nuke": True,
    "whitelist_users": [],
    "whitelist_roles": [],
    "rate_limits": {
        "messages": [5, 10]
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
    "anti_webhook": True,
    "anti_unauthorized_ban": True,
    "max_warnings": 6,
    "punishments": {
        "warn1": "warning",
        "warn2": "timeout_10min",
        "warn3": "timeout_30min",
        "warn4": "timeout_60min",
        "warn5": "kick",
        "warn6": "ban"
    }
}

# ================== 4️⃣ GLOBAL STATE ==================
rate_cache = {}
nuke_tracker = {}
spam_tracker = {}
mention_spam_tracker = {}
emoji_spam_tracker = {}
voice_connections = {}
protected_roles = set()
protected_channels = set()

# File locks for thread safety
config_lock = Lock()
warnings_lock = Lock()
logs_lock = Lock()

# URL patterns
URL_PATTERNS = [
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'discord\.gg/[a-zA-Z0-9]+',
    r'discord\.com/invite/[a-zA-Z0-9]+'
]

# Emoji pattern
EMOJI_PATTERN = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)

# ================== 5️⃣ CONFIG MANAGEMENT ==================
def load_config():
    """تحميل الإعدادات من الملف"""
    with config_lock:
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
    """حفظ الإعدادات إلى الملف"""
    with config_lock:
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
                "anti_webhook": ANTI_WEBHOOK_ENABLED,
                "anti_unauthorized_ban": ANTI_UNAUTHORIZED_BAN_ENABLED,
                "max_warnings": MAX_WARNINGS,
                "punishments": PUNISHMENTS
            }
            
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
            
            print("✅ تم حفظ الإعدادات بنجاح")
        except Exception as e:
            print(f"❌ خطأ في حفظ الإعدادات: {e}")

def reload_config():
    """إعادة تحميل الإعدادات من الملف"""
    global SECURITY_ENABLED, ANTI_NUKE_ENABLED, WHITELIST_USERS, WHITELIST_ROLES
    global RATE_LIMITS, BACKUP_ENABLED, BACKUP_INTERVAL, MAX_BACKUPS
    global ANTI_SPAM_ENABLED, ANTI_LINKS_ENABLED, ANTI_IMAGES_ENABLED
    global ANTI_ROLE_EDIT_ENABLED, ANTI_CHANNEL_EDIT_ENABLED
    global ANTI_WEBHOOK_ENABLED, ANTI_UNAUTHORIZED_BAN_ENABLED
    global MAX_WARNINGS, PUNISHMENTS
    
    with config_lock:
        try:
            if not os.path.exists(CONFIG_FILE):
                # إنشاء الملف إذا لم يكن موجوداً
                with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
                config = DEFAULT_CONFIG.copy()
            else:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            # تحديث جميع المتغيرات العامة
            SECURITY_ENABLED = config.get("security_enabled", True)
            ANTI_NUKE_ENABLED = config.get("anti_nuke", True)
            WHITELIST_USERS = set(config.get("whitelist_users", []))
            WHITELIST_ROLES = set(config.get("whitelist_roles", []))
            RATE_LIMITS = config.get("rate_limits", {"messages": [5, 10]})
            
            backup_cfg = config.get("backup", {})
            BACKUP_ENABLED = backup_cfg.get("enabled", True)
            BACKUP_INTERVAL = backup_cfg.get("interval_minutes", 30)
            MAX_BACKUPS = backup_cfg.get("max_backups", 10)
            
            ANTI_SPAM_ENABLED = config.get("anti_spam", True)
            ANTI_LINKS_ENABLED = config.get("anti_links", True)
            ANTI_IMAGES_ENABLED = config.get("anti_images", True)
            ANTI_ROLE_EDIT_ENABLED = config.get("anti_role_edit", True)
            ANTI_CHANNEL_EDIT_ENABLED = config.get("anti_channel_edit", True)
            ANTI_WEBHOOK_ENABLED = config.get("anti_webhook", True)
            ANTI_UNAUTHORIZED_BAN_ENABLED = config.get("anti_unauthorized_ban", True)
            MAX_WARNINGS = config.get("max_warnings", 6)
            PUNISHMENTS = config.get("punishments", {
                "warn1": "warning",
                "warn2": "timeout_10min",
                "warn3": "timeout_30min",
                "warn4": "timeout_60min",
                "warn5": "kick",
                "warn6": "ban"
            })
            
            print("✅ تم تحديث الإعدادات من الملف")
            return True
        except Exception as e:
            print(f"❌ خطأ في إعادة تحميل الإعدادات: {e}")
            return False

def load_warnings():
    """تحميل التحذيرات من الملف"""
    with warnings_lock:
        try:
            if not os.path.exists(WARNINGS_FILE):
                return {}
            with open(WARNINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل التحذيرات: {e}")
            return {}

def save_warnings(warnings_data):
    """حفظ التحذيرات إلى الملف"""
    with warnings_lock:
        try:
            with open(WARNINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(warnings_data, f, indent=4)
        except Exception as e:
            print(f"❌ خطأ في حفظ التحذيرات: {e}")

def load_logs():
    """تحميل السجلات من الملف"""
    with logs_lock:
        try:
            if not os.path.exists(LOGS_FILE):
                return []
            with open(LOGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ خطأ في تحميل السجلات: {e}")
            return []

def save_logs(logs_data):
    """حفظ السجلات إلى الملف"""
    with logs_lock:
        try:
            # حفظ آخر 1000 سجل فقط
            if len(logs_data) > 1000:
                logs_data = logs_data[-1000:]
            
            with open(LOGS_FILE, "w", encoding="utf-8") as f:
                json.dump(logs_data, f, indent=4)
        except Exception as e:
            print(f"❌ خطأ في حفظ السجلات: {e}")

# Load initial config and variables
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
ANTI_WEBHOOK_ENABLED = config.get("anti_webhook", True)
ANTI_UNAUTHORIZED_BAN_ENABLED = config.get("anti_unauthorized_ban", True)
MAX_WARNINGS = config.get("max_warnings", 6)
PUNISHMENTS = config.get("punishments", {
    "warn1": "warning",
    "warn2": "timeout_10min",
    "warn3": "timeout_30min",
    "warn4": "timeout_60min",
    "warn5": "kick",
    "warn6": "ban"
})

warnings = load_warnings()
security_logs = load_logs()

# ================== 5️⃣ READY & INITIALIZATION ==================
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
    
    # إنشاء قناة اللوقات في كل سيرفر
    for guild in bot.guilds:
        await ensure_logs_channel(guild)
    
    if BACKUP_ENABLED:
        if not auto_backup.is_running():
            auto_backup.start()
            print(f"✅ نظام النسخ الاحتياطي مفعل")
    
    print("✅ نظام الحماية الكامل مفعل")
    print("✅ نظام العقوبات التدريجي مفعل (6 مراحل)")

async def ensure_logs_channel(guild):
    """التأكد من وجود قناة اللوقات"""
    try:
        # البحث عن قناة اللوقات
        logs_channel = discord.utils.get(guild.text_channels, name="logs-security")
        
        if not logs_channel:
            # التحقق من صلاحيات البوت أولاً
            if not guild.me.guild_permissions.manage_channels:
                print(f"⚠️ البوت لا يملك صلاحية إنشاء القنوات في سيرفر: {guild.name}")
                return None
            
            # إنشاء القناة إذا لم توجد
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            try:
                logs_channel = await guild.create_text_channel(
                    "logs-security",
                    overwrites=overwrites,
                    reason="قناة سجلات الحماية"
                )
                
                embed = discord.Embed(
                    title="📢 قناة السجلات جاهزة",
                    description="تم إنشاء قناة السجلات بنجاح\nجميع الأحداث الأمنية ستظهر هنا",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.set_footer(text="Security BartX Ultimate Shield")
                await logs_channel.send(embed=embed)
                
                print(f"✅ تم إنشاء قناة السجلات في سيرفر: {guild.name}")
            except discord.Forbidden:
                print(f"⚠️ البوت لا يملك صلاحيات كافية في سيرفر: {guild.name}")
                return None
            except Exception as e:
                print(f"❌ خطأ في إنشاء قناة السجلات لسيرفر {guild.name}: {e}")
                return None
        
        return logs_channel
    except Exception as e:
        print(f"❌ خطأ في إنشاء قناة السجلات لسيرفر {guild.name}: {e}")
        return None

# ================== 6️⃣ LOG SYSTEM ==================
async def send_to_logs(guild, embed):
    """إرسال سجل إلى قناة اللوقات"""
    try:
        logs_channel = await ensure_logs_channel(guild)
        if logs_channel:
            try:
                await logs_channel.send(embed=embed)
            except discord.Forbidden:
                print(f"⚠️ لا يمكن إرسال الرسائل في قناة السجلات في سيرفر: {guild.name}")
            except Exception as e:
                print(f"❌ خطأ في إرسال السجل: {e}")
            
            # حفظ السجل في الملف
            log_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "guild": guild.name,
                "guild_id": guild.id,
                "title": embed.title if embed.title else "بدون عنوان",
                "description": embed.description if embed.description else "",
                "color": str(embed.color)
            }
            security_logs.append(log_entry)
            save_logs(security_logs)
    except Exception as e:
        print(f"❌ خطأ في إرسال السجل: {e}")

async def log_event(guild, event_type, description, color=discord.Color.blue(), user=None, target=None):
    """تسجيل حدث في السجلات"""
    embed = discord.Embed(
        title=f"📝 {event_type}",
        description=description,
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    
    if user:
        embed.add_field(name="👤 المستخدم", value=f"{user.mention}\n{user.id}", inline=True)
    
    if target:
        if isinstance(target, discord.Role):
            embed.add_field(name="🎖️ الرتبة", value=target.name, inline=True)
        elif isinstance(target, discord.abc.GuildChannel):
            embed.add_field(name="📁 الروم", value=target.name, inline=True)
        elif isinstance(target, discord.Member):
            embed.add_field(name="🎯 الهدف", value=f"{target.mention}\n{target.id}", inline=True)
    
    embed.set_footer(text="Security BartX Ultimate Shield")
    await send_to_logs(guild, embed)

# ================== 7️⃣ WHITELIST SYSTEM ==================
def is_whitelisted(member):
    """فحص إذا كان المستخدم معفي من الحماية"""
    # المالك دائمًا معفي
    if member.id == member.guild.owner_id:
        return True
    
    # البوت نفسه معفي
    if member.id == bot.user.id:
        return True
    
    # المستخدمين في الوايت ليست
    if member.id in WHITELIST_USERS:
        return True
    
    # الرتب في الوايت ليست
    if any(role.id in WHITELIST_ROLES for role in member.roles):
        return True
    
    return False

# ================== 8️⃣ GRADUAL PUNISHMENT SYSTEM ==================
async def add_warning(member, reason):
    """إضافة تحذير وتطبيق العقوبة المناسبة"""
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
            "punishment": "تحذير"
        }
        
        warnings[guild_id][user_id].append(warning)
        save_warnings(warnings)
        
        warning_count = len(warnings[guild_id][user_id])
        await apply_gradual_punishment(member, warning_count, reason)
        
        return warning_count
    except Exception as e:
        print(f"❌ خطأ في إضافة تحذير: {e}")
        return 0

async def apply_gradual_punishment(member, warning_count, reason):
    """تطبيق العقوبة التدريجية"""
    try:
        punishment_messages = {
            1: "⚠️ **التحذير الأول**\nلقد تلقيت تحذيراً بسبب: {reason}\nيرجى الالتزام بقوانين السيرفر.",
            2: "⏰ **التحذير الثاني**\nلقد تلقيت تقييداً لمدة 10 دقائق بسبب: {reason}\nهذا هو التحذير الثاني.",
            3: "⏰ **التحذير الثالث**\nلقد تلقيت تقييداً لمدة 30 دقيقة بسبب: {reason}\nهذا هو التحذير الثالث.",
            4: "⏰ **التحذير الرابع**\nلقد تلقيت تقييداً لمدة 60 دقيقة بسبب: {reason}\n⚠️ **تحذير شديد**: هذه فرصتك الأخيرة قبل الطرد!",
            5: "🚪 **التحذير الخامس**\nلقد تم طردك من السيرفر بسبب: {reason}\n⚠️ **تحذير نهائي**: المرة القادمة ستكون حظراً دائماً!",
            6: "🔨 **التحذير السادس**\nلقد تم حظرك من السيرفر بشكل دائم بسبب: {reason}"
        }
        
        punishment = "تحذير"
        
        if warning_count == 1:
            # تحذير فقط
            punishment = "تحذير"
            
        elif warning_count == 2:
            # تقييد 10 دقائق
            punishment = "تقييد 10 دقائق"
            if member.guild.me.guild_permissions.moderate_members:
                try:
                    await member.timeout(datetime.timedelta(minutes=10), reason=f"التحذير الثاني: {reason}")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن تقييد المستخدم {member.name}: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في تقييد المستخدم: {e}")
            
        elif warning_count == 3:
            # تقييد 30 دقيقة
            punishment = "تقييد 30 دقيقة"
            if member.guild.me.guild_permissions.moderate_members:
                try:
                    await member.timeout(datetime.timedelta(minutes=30), reason=f"التحذير الثالث: {reason}")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن تقييد المستخدم {member.name}: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في تقييد المستخدم: {e}")
            
        elif warning_count == 4:
            # تقييد 60 دقيقة
            punishment = "تقييد 60 دقيقة"
            if member.guild.me.guild_permissions.moderate_members:
                try:
                    await member.timeout(datetime.timedelta(hours=1), reason=f"التحذير الرابع: {reason}")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن تقييد المستخدم {member.name}: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في تقييد المستخدم: {e}")
            
        elif warning_count == 5:
            # طرد
            punishment = "طرد"
            if member.guild.me.guild_permissions.kick_members:
                try:
                    await member.kick(reason=f"التحذير الخامس: {reason}")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن طرد المستخدم {member.name}: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في طرد المستخدم: {e}")
            
        elif warning_count >= 6:
            # حظر دائم
            punishment = "حظر دائم"
            if member.guild.me.guild_permissions.ban_members:
                try:
                    await member.ban(reason=f"التحذير السادس: {reason}", delete_message_days=0)
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن حظر المستخدم {member.name}: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في حظر المستخدم: {e}")
        
        # إرسال رسالة تحذير للمستخدم
        try:
            if warning_count <= 6:
                message = punishment_messages.get(warning_count, "⚠️ لقد تلقيت عقوبة بسبب مخالفة قوانين السيرفر.").format(reason=reason)
                
                embed = discord.Embed(
                    title=f"📨 إشعار من نظام الحماية",
                    description=message,
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="📊 عدد التحذيرات", value=f"{warning_count}/{MAX_WARNINGS}", inline=False)
                embed.set_footer(text=f"سيرفر: {member.guild.name}")
                
                await member.send(embed=embed)
        except:
            pass  # لا يمكن إرسال رسالة خاصة
        
        # تسجيل العقوبة في السجلات
        await log_event(
            member.guild,
            "⚖️ تطبيق عقوبة",
            f"تم تطبيق عقوبة **{punishment}** على {member.mention}",
            discord.Color.orange(),
            user=member
        )
        
        return punishment
        
    except Exception as e:
        print(f"❌ خطأ في تطبيق العقوبة: {e}")
        return None

# ================== 9️⃣ SPAM PROTECTION ==================
def is_message_spam(user_id, guild_id):
    """فحص إذا كانت الرسالة سبام"""
    now = datetime.datetime.utcnow().timestamp()
    key = f"{guild_id}_{user_id}"
    
    if key not in spam_tracker:
        spam_tracker[key] = []
    
    spam_tracker[key].append(now)
    
    # الاحتفاظ بالرسائل في آخر 10 ثواني فقط
    spam_tracker[key] = [t for t in spam_tracker[key] if now - t < 10]
    
    # إذا كان هناك أكثر من 5 رسائل في 10 ثواني، فهذا سبام
    return len(spam_tracker[key]) > 5

def is_mention_spam(message):
    """فحص إذا كانت الرسالة تحتوي على منشن سبام"""
    if len(message.mentions) > 5:
        return True
    
    # فحص تكرار المنشن لنفس الشخص
    if message.mentions:
        mention_counts = {}
        for mention in message.mentions:
            if mention.id in mention_counts:
                mention_counts[mention.id] += 1
            else:
                mention_counts[mention.id] = 1
        
        if any(count > 3 for count in mention_counts.values()):
            return True
    
    return False

def is_emoji_spam(text):
    """فحص إذا كانت الرسالة تحتوي على إيموجي سبام"""
    emojis = EMOJI_PATTERN.findall(text)
    return len(emojis) > 10

# ================== 🔟 CONTENT FILTERING ==================
def contains_links(text):
    """فحص إذا كانت الرسالة تحتوي على روابط"""
    for pattern in URL_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def contains_images(message):
    """فحص إذا كانت الرسالة تحتوي على صور"""
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                return True
    return False

# ================== 1️⃣1️⃣ MESSAGE PROTECTION ==================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    # معالجة الأوامر أولاً
    await bot.process_commands(message)
    
    if not SECURITY_ENABLED or is_whitelisted(message.author):
        return
    
    guild_id = message.guild.id
    user_id = message.author.id
    
    violations = []
    
    # 1. فحص السبام
    if ANTI_SPAM_ENABLED:
        if is_message_spam(user_id, guild_id):
            violations.append("إرسال رسائل متكررة بشكل مفرط (سبام)")
        
        if is_mention_spam(message):
            violations.append("استخدام المنشن بشكل مفرط")
        
        if is_emoji_spam(message.content):
            violations.append("استخدام الإيموجي بشكل مفرط")
    
    # 2. فحص الروابط
    if ANTI_LINKS_ENABLED and contains_links(message.content):
        violations.append("إرسال روابط غير مسموح بها")
    
    # 3. فحص الصور
    if ANTI_IMAGES_ENABLED and contains_images(message):
        violations.append("إرسال صور غير مسموح بها")
    
    # تطبيق العقوبات إذا كان هناك انتهاكات
    if violations:
        try:
            await message.delete()
        except discord.Forbidden:
            print(f"⚠️ لا يمكن حذف رسالة من {message.author.name}: صلاحيات غير كافية")
        except Exception as e:
            print(f"❌ خطأ في حذف الرسالة: {e}")
        
        reason = " | ".join(violations)
        warning_count = await add_warning(message.author, reason)
        
        # تسجيل في السجلات
        await log_event(
            message.guild,
            "🚨 انتهاك محتوى",
            f"{message.author.mention} قام بانتهاك قواعد المحتوى\n**السبب:** {reason}\n**التحذير:** {warning_count}/{MAX_WARNINGS}",
            discord.Color.red(),
            user=message.author
        )

# ================== 1️⃣2️⃣ ROLE PROTECTION ==================
@bot.event
async def on_guild_role_create(role):
    """اكتشاف إنشاء رتب جديدة"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # البحث عن من أنشأ الرتبة
    try:
        async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_create):
            if entry.target and entry.target.id == role.id:
                creator = entry.user
                if not is_whitelisted(creator):
                    # إزالة الرتبة المحدثة أولاً
                    try:
                        await role.delete(reason="إنشاء رتبة بدون صلاحية")
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن حذف الرتبة: صلاحيات غير كافية")
                    
                    # إزالة جميع رتب المنشئ (باستثناء الرتب الأساسية)
                    if role.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = role.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in creator.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await creator.remove_roles(*roles_to_remove, reason="محاولة إنشاء رتبة بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {creator.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(creator, "محاولة إنشاء رتبة بدون صلاحية")
                    
                    await log_event(
                        role.guild,
                        "🚨 إنشاء رتبة",
                        f"{creator.mention} حاول إنشاء رتبة جديدة بدون صلاحية\n**الرتبة:** {role.name}",
                        discord.Color.red(),
                        user=creator,
                        target=role
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف إنشاء الرتب: {e}")

@bot.event
async def on_guild_role_delete(role):
    """اكتشاف حذف رتب"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    try:
        async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_delete):
            if entry.target and entry.target.id == role.id:
                deleter = entry.user
                if not is_whitelisted(deleter):
                    # إزالة جميع رتب المحذف (باستثناء الرتب الأساسية)
                    if role.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = role.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in deleter.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await deleter.remove_roles(*roles_to_remove, reason="محاولة حذف رتبة بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {deleter.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(deleter, "محاولة حذف رتبة بدون صلاحية")
                    
                    await log_event(
                        role.guild,
                        "🚨 حذف رتبة",
                        f"{deleter.mention} حاول حذف رتبة بدون صلاحية\n**الرتبة:** {role.name}",
                        discord.Color.red(),
                        user=deleter,
                        target=role
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف حذف الرتب: {e}")

@bot.event
async def on_guild_role_update(before, after):
    """اكتشاف تعديل الرتب"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    if (before.name == after.name and 
        before.permissions == after.permissions and
        before.color == after.color and
        before.hoist == after.hoist and
        before.mentionable == after.mentionable):
        return
    
    try:
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_update):
            if entry.target and entry.target.id == after.id:
                updater = entry.user
                if not is_whitelisted(updater):
                    # إزالة جميع رتب المعدل (باستثناء الرتب الأساسية)
                    if after.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = after.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in updater.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await updater.remove_roles(*roles_to_remove, reason="محاولة تعديل رتبة بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {updater.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(updater, "محاولة تعديل رتبة بدون صلاحية")
                    
                    # استعادة التعديلات
                    try:
                        await after.edit(
                            name=before.name,
                            permissions=before.permissions,
                            color=before.color,
                            hoist=before.hoist,
                            mentionable=before.mentionable,
                            reason="استعادة تعديل رتبة غير مصرح"
                        )
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن تعديل الرتبة: صلاحيات غير كافية")
                    
                    await log_event(
                        after.guild,
                        "🚨 تعديل رتبة",
                        f"{updater.mention} حاول تعديل رتبة بدون صلاحية\n**الرتبة:** {after.name}",
                        discord.Color.red(),
                        user=updater,
                        target=after
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف تعديل الرتب: {e}")

# ================== 1️⃣3️⃣ CHANNEL PROTECTION ==================
@bot.event
async def on_guild_channel_create(channel):
    """اكتشاف إنشاء رومات جديدة"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    try:
        async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
            if entry.target and entry.target.id == channel.id:
                creator = entry.user
                if not is_whitelisted(creator):
                    # إزالة جميع رتب المنشئ (باستثناء الرتب الأساسية)
                    if channel.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = channel.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in creator.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await creator.remove_roles(*roles_to_remove, reason="محاولة إنشاء روم بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {creator.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(creator, "محاولة إنشاء روم بدون صلاحية")
                    
                    # حذف الروم المحدث
                    try:
                        await channel.delete(reason="إنشاء روم بدون صلاحية")
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن حذف القناة: صلاحيات غير كافية")
                    
                    await log_event(
                        channel.guild,
                        "🚨 إنشاء روم",
                        f"{creator.mention} حاول إنشاء روم جديد بدون صلاحية\n**الروم:** #{channel.name}",
                        discord.Color.red(),
                        user=creator,
                        target=channel
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف إنشاء الرومات: {e}")

@bot.event
async def on_guild_channel_delete(channel):
    """اكتشاف حذف رومات"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    try:
        async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
            if entry.target and entry.target.id == channel.id:
                deleter = entry.user
                if not is_whitelisted(deleter):
                    # إزالة جميع رتب المحذف (باستثناء الرتب الأساسية)
                    if channel.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = channel.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in deleter.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await deleter.remove_roles(*roles_to_remove, reason="محاولة حذف روم بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {deleter.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(deleter, "محاولة حذف روم بدون صلاحية")
                    
                    await log_event(
                        channel.guild,
                        "🚨 حذف روم",
                        f"{deleter.mention} حاول حذف روم بدون صلاحية\n**الروم:** #{channel.name}",
                        discord.Color.red(),
                        user=deleter,
                        target=channel
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف حذف الرومات: {e}")

@bot.event
async def on_guild_channel_update(before, after):
    """اكتشاف تعديل الرومات"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    if (before.name == after.name and 
        before.position == after.position and
        before.category == after.category):
        return
    
    try:
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_update):
            if entry.target and entry.target.id == after.id:
                updater = entry.user
                if not is_whitelisted(updater):
                    # إزالة جميع رتب المعدل (باستثناء الرتب الأساسية)
                    if after.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = after.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in updater.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await updater.remove_roles(*roles_to_remove, reason="محاولة تعديل روم بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {updater.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(updater, "محاولة تعديل روم بدون صلاحية")
                    
                    # استعادة التعديلات
                    try:
                        await after.edit(
                            name=before.name,
                            position=before.position,
                            category=before.category,
                            reason="استعادة تعديل روم غير مصرح"
                        )
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن تعديل القناة: صلاحيات غير كافية")
                    
                    await log_event(
                        after.guild,
                        "🚨 تعديل روم",
                        f"{updater.mention} حاول تعديل روم بدون صلاحية\n**الروم:** #{after.name}",
                        discord.Color.red(),
                        user=updater,
                        target=after
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف تعديل الرومات: {e}")

# ================== 1️⃣4️⃣ ROLE MANAGEMENT PROTECTION ==================
@bot.event
async def on_member_update(before, after):
    """اكتشاف إعطاء أو سحب الرتب"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # التحقق من تغيير الرتب
    if set(before.roles) == set(after.roles):
        return
    
    try:
        async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
            if entry.target and entry.target.id == after.id:
                updater = entry.user
                if not is_whitelisted(updater):
                    # إزالة جميع رتب المعدل (باستثناء الرتب الأساسية)
                    if after.guild.me.guild_permissions.manage_roles:
                        try:
                            # الحصول على الرتب الأساسية (everyone)
                            everyone_role = after.guild.default_role
                            # إزالة جميع الرتب ما عدا الرتبة الأساسية
                            roles_to_remove = [r for r in updater.roles if r != everyone_role and not r.managed]
                            if roles_to_remove:
                                await updater.remove_roles(*roles_to_remove, reason="محاولة إعطاء/سحب رتب بدون صلاحية")
                        except discord.Forbidden:
                            print(f"⚠️ لا يمكن إزالة رتب من {updater.name}: صلاحيات غير كافية")
                    
                    # إضافة تحذير
                    await add_warning(updater, "محاولة إعطاء/سحب رتب بدون صلاحية")
                    
                    # استعادة الرتب الأصلية
                    try:
                        await after.edit(roles=list(before.roles), reason="استعادة رتب غير مصرح بها")
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن تعديل رتب العضو: صلاحيات غير كافية")
                    
                    await log_event(
                        after.guild,
                        "🚨 تعديل رتب عضو",
                        f"{updater.mention} حاول إعطاء/سحب رتب لـ {after.mention} بدون صلاحية",
                        discord.Color.red(),
                        user=updater,
                        target=after
                    )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف تعديل رتب العضو: {e}")

# ================== 1️⃣5️⃣ WEBHOOK PROTECTION ==================
@bot.event
async def on_webhooks_update(channel):
    """اكتشاف إنشاء أو تعديل ويب هوك"""
    if not SECURITY_ENABLED or not ANTI_WEBHOOK_ENABLED:
        return
    
    try:
        async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.webhook_create):
            creator = entry.user
            if not is_whitelisted(creator):
                # حذف الويب هوك
                try:
                    webhooks = await channel.webhooks()
                    for webhook in webhooks:
                        if webhook.user and webhook.user.id == creator.id:
                            await webhook.delete(reason="إنشاء ويب هوك بدون صلاحية")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن إدارة الويب هوك: صلاحيات غير كافية")
                
                # إزالة جميع رتب المنشئ (باستثناء الرتب الأساسية)
                if channel.guild.me.guild_permissions.manage_roles:
                    try:
                        # الحصول على الرتب الأساسية (everyone)
                        everyone_role = channel.guild.default_role
                        # إزالة جميع الرتب ما عدا الرتبة الأساسية
                        roles_to_remove = [r for r in creator.roles if r != everyone_role and not r.managed]
                        if roles_to_remove:
                            await creator.remove_roles(*roles_to_remove, reason="محاولة إنشاء ويب هوك بدون صلاحية")
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن إزالة رتب من {creator.name}: صلاحيات غير كافية")
                
                # إضافة تحذير
                await add_warning(creator, "محاولة إنشاء ويب هوك بدون صلاحية")
                
                await log_event(
                    channel.guild,
                    "🚨 إنشاء ويب هوك",
                    f"{creator.mention} حاول إنشاء ويب هوك بدون صلاحية\n**القناة:** #{channel.name}",
                    discord.Color.red(),
                    user=creator,
                    target=channel
                )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف إنشاء الويب هوك: {e}")

# ================== 1️⃣6️⃣ UNAUTHORIZED BAN PROTECTION ==================
@bot.event
async def on_member_ban(guild, user):
    """اكتشاف حظر غير مصرح به"""
    if not SECURITY_ENABLED or not ANTI_UNAUTHORIZED_BAN_ENABLED:
        return
    
    try:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
            if entry.target and entry.target.id == user.id:
                banner = entry.user
                
                # التحقق إذا كان الحاظر معفي أو لديه صلاحية الباند
                if is_whitelisted(banner) or banner.guild_permissions.ban_members:
                    return
                
                # فك حظر العضو المظلوم
                try:
                    await guild.unban(user, reason="فك حظر غير مصرح به")
                except discord.Forbidden:
                    print(f"⚠️ لا يمكن فك حظر المستخدم: صلاحيات غير كافية")
                except Exception as e:
                    print(f"❌ خطأ في فك الحظر: {e}")
                
                # إزالة جميع رتب الحاظر (باستثناء الرتب الأساسية)
                if guild.me.guild_permissions.manage_roles:
                    try:
                        # الحصول على الرتب الأساسية (everyone)
                        everyone_role = guild.default_role
                        # إزالة جميع الرتب ما عدا الرتبة الأساسية
                        roles_to_remove = [r for r in banner.roles if r != everyone_role and not r.managed]
                        if roles_to_remove:
                            await banner.remove_roles(*roles_to_remove, reason="محاولة حظر عضو بدون صلاحية")
                    except discord.Forbidden:
                        print(f"⚠️ لا يمكن إزالة رتب من {banner.name}: صلاحيات غير كافية")
                
                # إضافة تحذير
                await add_warning(banner, "محاولة حظر عضو بدون صلاحية")
                
                await log_event(
                    guild,
                    "🚨 حظر غير مصرح",
                    f"{banner.mention} حاول حظر {user.mention} بدون صلاحية\nتم فك الحظر تلقائياً",
                    discord.Color.red(),
                    user=banner,
                    target=user
                )
                break
    except discord.Forbidden:
        print(f"⚠️ لا يمكن قراءة سجلات التدقيق: صلاحيات غير كافية")
    except Exception as e:
        print(f"❌ خطأ في اكتشاف الحظر: {e}")

# ================== 1️⃣7️⃣ ADMIN COMMANDS ==================
@bot.group()
@commands.has_permissions(administrator=True)
async def الحماية(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ نظام الحماية الكامل",
            description="أوامر إدارة نظام الحماية المتكامل",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="⚙️ الإعدادات الرئيسية",
            value="• `!الحماية تشغيل` - تشغيل النظام\n• `!الحماية إيقاف` - إيقاف النظام\n• `!الحماية الحالة` - عرض حالة النظام",
            inline=False
        )
        embed.add_field(
            name="👥 إدارة الوايت ليست",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`\n• `!الحماية وايت_ليست القائمة`",
            inline=False
        )
        embed.add_field(
            name="🗑️ إدارة المحادثات",
            value="• `!مسح [عدد]` - مسح الرسائل (1-1000)\n• `!اغلاق_الشات` - إغلاق روم كتابي\n• `!فتح_الشات` - فتح روم كتابي",
            inline=False
        )
        embed.add_field(
            name="🎤 أوامر الصوت",
            value="• `!دخول` - دخول الروم الصوتي\n• `!خروج` - خروج من الروم الصوتي",
            inline=False
        )
        embed.add_field(
            name="📊 ميزات الحماية",
            value="• حماية كاملة للرتب والرومات\n• منع السبام والروابط والصور\n• حماية من الويب هوك\n• حماية من الحظر غير المصرح\n• نظام عقوبات تدريجي (6 مراحل)",
            inline=False
        )
        embed.set_footer(text="Security BartX Ultimate Shield v8.0")
        await ctx.send(embed=embed)

@الحماية.command()
async def تشغيل(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = True
    save_config()
    
    embed = discord.Embed(
        title="✅ تم تشغيل الحماية",
        description="نظام الحماية الآن نشط ويحمي السيرفر",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def إيقاف(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = False
    save_config()
    
    embed = discord.Embed(
        title="⛔ تم إيقاف الحماية",
        description="نظام الحماية الآن معطل",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def الحالة(ctx):
    guild_id = str(ctx.guild.id)
    total_warnings = sum(len(w) for w in warnings.get(guild_id, {}).values())
    
    embed = discord.Embed(
        title="📊 حالة نظام الحماية",
        color=discord.Color.blue()
    )
    embed.add_field(name="🛡️ الحماية", value="✅ مفعل" if SECURITY_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🎖️ حماية الرتب", value="✅ مفعل" if ANTI_ROLE_EDIT_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="📁 حماية الرومات", value="✅ مفعل" if ANTI_CHANNEL_EDIT_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🚫 منع السبام", value="✅ مفعل" if ANTI_SPAM_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🔗 منع الروابط", value="✅ مفعل" if ANTI_LINKS_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🖼️ منع الصور", value="✅ مفعل" if ANTI_IMAGES_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🌐 منع الويب هوك", value="✅ مفعل" if ANTI_WEBHOOK_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="🔨 منع الحظر غير المصرح", value="✅ مفعل" if ANTI_UNAUTHORIZED_BAN_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="⚠️ إجمالي التحذيرات", value=str(total_warnings), inline=True)
    embed.add_field(name="👥 أعضاء الوايت ليست", value=str(len(WHITELIST_USERS)), inline=True)
    embed.add_field(name="🎖️ رتب الوايت ليست", value=str(len(WHITELIST_ROLES)), inline=True)
    embed.add_field(name="⚖️ نظام العقوبات", value="6 مراحل تدريجية", inline=True)
    
    await ctx.send(embed=embed)

@الحماية.group()
async def وايت_ليست(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="👥 إدارة الوايت ليست",
            description="الأعضاء والرتب المعفاة من الحماية",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="الأوامر",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`\n• `!الحماية وايت_ليست القائمة`",
            inline=False
        )
        await ctx.send(embed=embed)

@وايت_ليست.command()
async def إضافة_عضو(ctx, member: discord.Member):
    WHITELIST_USERS.add(member.id)
    save_config()
    
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"تمت إضافة {member.mention} إلى القائمة البيضاء",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def إضافة_رتبة(ctx, role: discord.Role):
    WHITELIST_ROLES.add(role.id)
    save_config()
    
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"تمت إضافة رتبة **{role.name}** إلى القائمة البيضاء",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def القائمة(ctx):
    """عرض قائمة الوايت ليست"""
    embed = discord.Embed(
        title="📋 قائمة الوايت ليست",
        description="الأعضاء والرتب المعفاة من الحماية",
        color=discord.Color.blue()
    )
    
    # الأعضاء
    members_list = []
    for user_id in WHITELIST_USERS:
        member = ctx.guild.get_member(user_id)
        if member:
            members_list.append(f"• {member.mention}")
    
    if members_list:
        embed.add_field(name="👥 الأعضاء المعفيون", value="\n".join(members_list), inline=False)
    else:
        embed.add_field(name="👥 الأعضاء المعفيون", value="لا يوجد أعضاء معفيون", inline=False)
    
    # الرتب
    roles_list = []
    for role_id in WHITELIST_ROLES:
        role = ctx.guild.get_role(role_id)
        if role:
            roles_list.append(f"• {role.name}")
    
    if roles_list:
        embed.add_field(name="🎖️ الرتب المعفاة", value="\n".join(roles_list), inline=False)
    else:
        embed.add_field(name="🎖️ الرتب المعفاة", value="لا يوجد رتب معفاة", inline=False)
    
    await ctx.send(embed=embed)

# ================== 1️⃣8️⃣ CHAT MANAGEMENT COMMANDS ==================
@bot.command(name="مسح", aliases=["حذف", "clear", "purge"])
@commands.has_permissions(manage_messages=True)
async def مسح(ctx, amount: int = 10):
    """مسح عدد محدد من الرسائل (1-1000)"""
    try:
        if amount < 1:
            amount = 1
        if amount > 1000:
            amount = 1000
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        embed = discord.Embed(
            title="🗑️ تم المسح",
            description=f"تم حذف {len(deleted) - 1} رسالة",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)
        
        # تسجيل في السجلات
        await log_event(
            ctx.guild,
            "🧹 مسح محادثة",
            f"{ctx.author.mention} قام بمسح {len(deleted) - 1} رسالة من {ctx.channel.mention}",
            discord.Color.green(),
            user=ctx.author,
            target=ctx.channel
        )
        
        await asyncio.sleep(3)
        await msg.delete()
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحيات غير كافية",
            description="لا أملك صلاحية حذف الرسائل",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الحذف",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="اغلاق_الشات", aliases=["اقفال", "lock"])
@commands.has_permissions(manage_channels=True)
async def اغلاق_الشات(ctx):
    """إغلاق روم كتابي"""
    try:
        if not isinstance(ctx.channel, discord.TextChannel):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر مخصص للرومات الكتابية فقط",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        everyone_role = ctx.guild.default_role
        await ctx.channel.set_permissions(everyone_role, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 تم إغلاق الشات",
            description=f"تم إغلاق {ctx.channel.mention} بنجاح",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        # تسجيل في السجلات
        await log_event(
            ctx.guild,
            "🔒 إغلاق روم",
            f"{ctx.author.mention} قام بإغلاق {ctx.channel.mention}",
            discord.Color.orange(),
            user=ctx.author,
            target=ctx.channel
        )
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحيات غير كافية",
            description="لا أملك صلاحية تعديل القناة",
            color=discord.Color.red()
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
async def فتح_الشات(ctx):
    """فتح روم كتابي"""
    try:
        if not isinstance(ctx.channel, discord.TextChannel):
            embed = discord.Embed(
                title="❌ خطأ",
                description="هذا الأمر مخصص للرومات الكتابية فقط",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        everyone_role = ctx.guild.default_role
        await ctx.channel.set_permissions(everyone_role, send_messages=True)
        
        embed = discord.Embed(
            title="🔓 تم فتح الشات",
            description=f"تم فتح {ctx.channel.mention} بنجاح",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        # تسجيل في السجلات
        await log_event(
            ctx.guild,
            "🔓 فتح روم",
            f"{ctx.author.mention} قام بفتح {ctx.channel.mention}",
            discord.Color.green(),
            user=ctx.author,
            target=ctx.channel
        )
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحيات غير كافية",
            description="لا أملك صلاحية تعديل القناة",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الفتح",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ================== 1️⃣9️⃣ VOICE COMMANDS ==================
@bot.command(name="دخول", aliases=["join", "connect"])
@commands.has_permissions(manage_channels=True)
async def دخول(ctx):
    """دخول البوت إلى الروم الصوتي"""
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
        
        # تسجيل في السجلات
        await log_event(
            ctx.guild,
            "🎤 دخول صوتي",
            f"{ctx.author.mention} طلب دخول البوت إلى {voice_channel.mention}",
            discord.Color.green(),
            user=ctx.author,
            target=voice_channel
        )
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحيات غير كافية",
            description="لا أملك صلاحية الاتصال بالقنوات الصوتية",
            color=discord.Color.red()
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
async def خروج(ctx):
    """خروج البوت من الروم الصوتي"""
    try:
        if ctx.guild.voice_client is None:
            embed = discord.Embed(
                title="❌ خطأ",
                description="أنا لست متصلاً بأي روم صوتي",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        channel_name = ctx.guild.voice_client.channel.name
        await ctx.guild.voice_client.disconnect()
        
        if ctx.guild.id in voice_connections:
            del voice_connections[ctx.guild.id]
        
        embed = discord.Embed(
            title="✅ تم الخروج",
            description=f"تم الخروج من روم {channel_name}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        # تسجيل في السجلات
        await log_event(
            ctx.guild,
            "🎤 خروج صوتي",
            f"{ctx.author.mention} طلب خروج البوت من روم الصوت",
            discord.Color.green(),
            user=ctx.author
        )
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ في الخروج",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ================== 2️⃣0️⃣ HELP COMMAND ==================
@bot.command(name="مساعدة", aliases=["help", "اوامر"])
async def مساعدة(ctx):
    """عرض جميع الأوامر المتاحة"""
    embed = discord.Embed(
        title="🛡️ Security BartX - جميع الأوامر",
        description="نظام حماية متكامل للسيرفرات",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🔒 أوامر الحماية",
        value="• `!الحماية` - قائمة أوامر الحماية\n• `!الحماية تشغيل/إيقاف` - تشغيل/إيقاف النظام\n• `!الحماية الحالة` - عرض حالة النظام\n• `!الحماية وايت_ليست القائمة` - عرض الوايت ليست",
        inline=False
    )
    
    embed.add_field(
        name="👥 أوامر الوايت ليست",
        value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ أوامر إدارة المحادثات",
        value="• `!مسح [عدد]` - مسح الرسائل (1-1000)\n• `!اغلاق_الشات` - إغلاق روم كتابي\n• `!فتح_الشات` - فتح روم كتابي",
        inline=False
    )
    
    embed.add_field(
        name="🎤 أوامر الصوت",
        value="• `!دخول` - دخول الروم الصوتي\n• `!خروج` - خروج من الروم الصوتي",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ ميزات الحماية",
        value="• **حماية كاملة للرتب والرومات**\n• **منع السبام** (تكرار، منشن، إيموجي)\n• **منع الروابط والصور**\n• **منع الويب هوك**\n• **منع الحظر غير المصرح**\n• **نظام عقوبات تدريجي** (6 مراحل)",
        inline=False
    )
    
    embed.set_footer(text="Security BartX Ultimate Shield v8.0")
    await ctx.send(embed=embed)

# ================== 2️⃣1️⃣ BACKUP SYSTEM ==================
def create_backup(reason="auto"):
    if not BACKUP_ENABLED:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{timestamp}_{reason}.json"
    path = os.path.join(BACKUP_DIR, name)
    
    try:
        with config_lock:
            config_data = load_config()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        
        backups = sorted(os.listdir(BACKUP_DIR))
        while len(backups) > MAX_BACKUPS:
            oldest = backups.pop(0)
            os.remove(os.path.join(BACKUP_DIR, oldest))
        
        print(f"✅ تم إنشاء نسخة احتياطية: {name}")
    except Exception as e:
        print(f"❌ فشل إنشاء نسخة احتياطية: {e}")

@tasks.loop(minutes=BACKUP_INTERVAL)
async def auto_backup():
    if BACKUP_ENABLED:
        create_backup("auto")

# ================== 2️⃣2️⃣ ERROR HANDLING ==================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="⛔ صلاحية مرفوضة",
            description="تحتاج إلى صلاحية المدير لاستخدام هذا الأمر",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="⚠️ معطيات ناقصة",
            description=f"يرجى إدخال جميع المعطيات المطلوبة\nاستخدم `!مساعدة` لعرض الأوامر",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ معطيات غير صالحة",
            description="يرجى التحقق من المعطيات المدخلة",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        print(f"❌ خطأ غير معالج: {error}")
        traceback.print_exc()

# ================== 2️⃣3️⃣ RUN ==================
if __name__ == "__main__":
    try:
        keep_alive()
        print("🌐 خادم الويب يعمل...")
        
        # محاولة الحصول على التوكن من مصادر مختلفة
        token = os.environ.get("TOKEN") or os.environ.get("DISCORD_TOKEN")
        
        if not token:
            print("⚠️ لم يتم العثور على التوكن في متغيرات البيئة")
            print("⚙️ جاري التحقق من ملف token.txt...")
            try:
                with open("token.txt", "r") as f:
                    token = f.read().strip()
                print("✅ تم تحميل التوكن من token.txt")
            except FileNotFoundError:
                print("❌ ملف token.txt غير موجود")
            except Exception as e:
                print(f"❌ خطأ في قراءة token.txt: {e}")
        
        if not token:
            print("❌ خطأ: لم يتم العثور على التوكن!")
            print("📝 الرجاء تعيين التوكن بإحدى الطرق التالية:")
            print("   1. متغير بيئة TOKEN أو DISCORD_TOKEN")
            print("   2. ملف token.txt في نفس المجلد")
            exit(1)
        
        print("🤖 جاري تشغيل البوت...")
        print("🛡️ نظام الحماية الكامل مفعل")
        print("📊 نظام العقوبات التدريجي: 6 مراحل")
        print("🚫 يحمي من: السبام، الروابط، الصور، الويب هوك")
        print("🎖️ يحمي: الرتب، الرومات، إعطاء الرتب")
        print("🔨 يحمي من: الحظر غير المصرح")
        print("🌐 لوحة التحكم متاحة على: http://localhost:8080/dashboard")
        bot.run(token)
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
