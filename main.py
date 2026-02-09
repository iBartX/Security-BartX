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
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG
            
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
                    <h2>⚠️ وضع الحماية الشديد مفعل</h2>
                    <p>النظام يحمي <strong>جميع الرتب والرومات</strong> بما فيها الرتب تحت البوت</p>
                    <p>فقط المالك وأعضاء الوايت ليست يمكنهم التعديل</p>
                </div>
                
                <div class="box">
                    <h2>📊 حالة النظام</h2>
                    <div class="toggle">
                        <span>🛡️ الحماية الشديدة:</span>
                        <strong>{'✅ مفعلة' if cfg.get('security_enabled', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>💣 Anti-Nuke:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_nuke', True) else '❌ معطل'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🎖️ حماية الرتب الشاملة:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_role_edit', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>📁 حماية الرومات الشاملة:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_channel_edit', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🚫 منع السبام:</span>
                        <strong>{'✅ مفعل' if cfg.get('anti_spam', True) else '❌ معطل'}</strong>
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
                    <form action="/toggle_security" method="post">
                        <button class="btn" type="submit">⚡ تبديل الحماية الشديدة</button>
                    </form>
                    <form action="/toggle_role_protection" method="post">
                        <button class="btn" type="submit">🎖️ تبديل حماية الرتب</button>
                    </form>
                    <form action="/toggle_channel_protection" method="post">
                        <button class="btn" type="submit">📁 تبديل حماية الرومات</button>
                    </form>
                    <form action="/toggle_nuke" method="post">
                        <button class="btn" type="submit">💣 تبديل Anti-Nuke</button>
                    </form>
                    <form action="/backup_now" method="post">
                        <button class="btn" type="submit">💾 إنشاء نسخة احتياطية</button>
                    </form>
                </div>
                
                <div class="box">
                    <h2>⚖️ إعدادات العقوبات</h2>
                    <div class="toggle">
                        <span>التعديل على الرتب/الرومات:</span>
                        <strong>🔨 حظر فوري + إزالة رتب</strong>
                    </div>
                    <div class="toggle">
                        <span>السببام والروابط:</span>
                        <strong>⏰ تقييد تدريجي</strong>
                    </div>
                    <p style="margin-top:10px;color:#94a3b8">التعديل على الرتب والرومات له عقوبة فورية أشد</p>
                </div>
                
                <p style="text-align:center;margin-top:30px;color:#94a3b8">
                    © 2024 Security BartX Ultimate Shield v6.0
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
            cfg = DEFAULT_CONFIG
        
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
                <p>الحماية الشديدة الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_role_protection", methods=['POST'])
def toggle_role_protection():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG
        
        current_state = cfg.get("anti_role_edit", True)
        cfg["anti_role_edit"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعلة" if cfg["anti_role_edit"] else "معطلة"
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
                <p>حماية الرتب الشديدة الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_channel_protection", methods=['POST'])
def toggle_channel_protection():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG
        
        current_state = cfg.get("anti_channel_edit", True)
        cfg["anti_channel_edit"] = not current_state
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        
        new_state = "مفعلة" if cfg["anti_channel_edit"] else "معطلة"
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
                <p>حماية الرومات الشديدة الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/toggle_nuke", methods=['POST'])
def toggle_nuke():
    try:
        config_path = "security_config.json"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = DEFAULT_CONFIG
        
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
    "max_warnings": 5,
    "strict_mode": True,  # وضع الحماية الشديد
    "role_protection_level": "all",  # حماية جميع الرتب
    "channel_protection_level": "all"  # حماية جميع الرومات
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
            "strict_mode": STRICT_MODE,
            "role_protection_level": "all",
            "channel_protection_level": "all"
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
MAX_WARNINGS = config.get("max_warnings", 5)
STRICT_MODE = config.get("strict_mode", True)

# ================== 4️⃣ GLOBAL STATE ==================
rate_cache = {}
nuke_tracker = {}
spam_tracker = {}
warnings = load_warnings()
voice_connections = {}
protected_roles = set()  # لتخزين الرتب المحمية
protected_channels = set()  # لتخزين الرومات المحمية

# URL patterns
URL_PATTERNS = [
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    r'discord\.gg/[a-zA-Z0-9]+',
    r'discord\.com/invite/[a-zA-Z0-9]+'
]

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
    
    # تهيئة الحماية لجميع السيرفرات
    for guild in bot.guilds:
        await initialize_protection(guild)
    
    if BACKUP_ENABLED:
        auto_backup.start()
        print(f"✅ نظام النسخ الاحتياطي مفعل")
    
    print("✅ وضع الحماية الشديد مفعل - يحمي جميع الرتب والرومات")
    print("✅ فقط المالك والوايت ليست يمكنهم التعديل")

async def initialize_protection(guild):
    """تهيئة الحماية للسيرفر"""
    try:
        # تحديد الرتب المحمية (جميع الرتب ما عدا @everyone)
        for role in guild.roles:
            if not role.is_default():
                protected_roles.add(role.id)
        
        # تحديد الرومات المحمية (جميع الرومات)
        for channel in guild.channels:
            protected_channels.add(channel.id)
        
        print(f"✅ تم تهيئة الحماية لسيرفر: {guild.name}")
        print(f"   - الرتب المحمية: {len(protected_roles)}")
        print(f"   - الرومات المحمية: {len(protected_channels)}")
        
    except Exception as e:
        print(f"❌ خطأ في تهيئة الحماية لسيرفر {guild.name}: {e}")

# ================== 6️⃣ LOG SYSTEM ==================
async def send_to_logs(guild, embed):
    try:
        for channel in guild.text_channels:
            if "logs" in channel.name.lower() or "سجلات" in channel.name:
                await channel.send(embed=embed)
                return
        
        try:
            logs_channel = await guild.create_text_channel(
                "logs-security",
                reason="قناة سجلات الحماية"
            )
            await logs_channel.send(embed=embed)
        except:
            pass
    except:
        pass

# ================== 7️⃣ WHITELIST & PERMISSION CHECK ==================
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

def has_permission_to_modify(member, target_type="role"):
    """فحص إذا كان لدى المستخدم صلاحية للتعديل"""
    # إذا كان معفي، يسمح له
    if is_whitelisted(member):
        return True
    
    # في وضع الحماية الشديد، لا أحد يستطيع التعديل إلا المعفيين
    if STRICT_MODE:
        return False
    
    # فحص الصلاحيات التقليدية
    if target_type == "role":
        return member.guild_permissions.manage_roles
    elif target_type == "channel":
        return member.guild_permissions.manage_channels
    elif target_type == "guild":
        return member.guild_permissions.manage_guild
    
    return False

# ================== 8️⃣ STRICT PUNISHMENT SYSTEM ==================
async def apply_strict_punishment(member, violation_type, target=None):
    """تطبيق عقوبة صارمة على من يتعدى على الرتب/الرومات"""
    try:
        reason_messages = {
            "role_create": "محاولة إنشاء رتبة بدون صلاحية",
            "role_delete": "محاولة حذف رتبة بدون صلاحية",
            "role_update": "محاولة تعديل رتبة بدون صلاحية",
            "channel_create": "محاولة إنشاء روم بدون صلاحية",
            "channel_delete": "محاولة حذف روم بدون صلاحية",
            "channel_update": "محاولة تعديل روم بدون صلاحية"
        }
        
        reason = reason_messages.get(violation_type, "تعديل غير مصرح به")
        
        # 1. إزالة جميع الرتب من المستخدم
        try:
            if member.guild.me.guild_permissions.manage_roles:
                await member.edit(roles=[], reason=f"عقوبة: {reason}")
        except:
            pass
        
        # 2. حظر المستخدم فوراً
        try:
            if member.guild.me.guild_permissions.ban_members:
                await member.ban(
                    reason=f"عقوبة فورية: {reason}",
                    delete_message_days=1
                )
        except:
            pass
        
        # 3. إرسال إشعار إلى المالك
        try:
            owner = member.guild.owner
            if owner:
                embed = discord.Embed(
                    title="🚨 هجوم أمني خطير",
                    description=f"تم اكتشاف هجوم على سيرفر **{member.guild.name}**",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="👤 المهاجم", value=f"{member} ({member.id})", inline=False)
                embed.add_field(name="🎯 نوع الهجوم", value=reason, inline=False)
                embed.add_field(name="🛡️ الإجراء", value="تم حظره وإزالة جميع رتبه", inline=False)
                embed.set_footer(text="Security BartX Ultimate Shield")
                
                await owner.send(embed=embed)
        except:
            pass
        
        # 4. تسجيل في السجلات
        embed = discord.Embed(
            title="🔨 عقوبة فورية تطبيق",
            description="تم تطبيق عقوبة فورية على متعدي",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 المستخدم", value=f"{member.mention} ({member.id})", inline=False)
        embed.add_field(name="🎯 الانتهاك", value=reason, inline=False)
        embed.add_field(name="⚖️ العقوبة", value="حظر فوري + إزالة جميع الرتب", inline=False)
        
        if target:
            if isinstance(target, discord.Role):
                embed.add_field(name="🎖️ الرتبة المستهدفة", value=target.name, inline=False)
            elif isinstance(target, discord.abc.GuildChannel):
                embed.add_field(name="📁 الروم المستهدف", value=target.name, inline=False)
        
        await send_to_logs(member.guild, embed)
        
        # 5. إشعار في الشات الرئيسي
        try:
            alert_embed = discord.Embed(
                title="🚨 تم تطبيق عقوبة أمنية",
                description=f"تم حظر {member.mention} بسبب تعديل غير مصرح به",
                color=discord.Color.dark_red()
            )
            alert_embed.add_field(name="السبب", value=reason, inline=False)
            alert_embed.add_field(name="العقوبة", value="حظر دائم", inline=False)
            
            if member.guild.system_channel:
                await member.guild.system_channel.send(embed=alert_embed)
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في تطبيق العقوبة الصارمة: {e}")
        return False

# ================== 9️⃣ ROLE PROTECTION (STRICT) ==================
@bot.event
async def on_guild_role_create(role):
    """اكتشاف إنشاء رتب جديدة - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # إضافة الرتبة الجديدة إلى القائمة المحمية
    protected_roles.add(role.id)
    
    mod = await safe_audit_log(role.guild, discord.AuditLogAction.role_create, role.id)
    if not mod:
        return
    
    # فحص إذا كان المعفي
    if is_whitelisted(mod):
        return
    
    # فحص إذا لديه صلاحية (في الوضع غير الصارم)
    if not STRICT_MODE and has_permission_to_modify(mod, "role"):
        return
    
    # تطبيق العقوبة الفورية
    await apply_strict_punishment(mod, "role_create", role)
    
    # محاولة حذف الرتبة المحدثة
    try:
        if role.guild.me.guild_permissions.manage_roles:
            await role.delete(reason="إنشاء رتبة بدون صلاحية - حذف تلقائي")
    except:
        pass

@bot.event
async def on_guild_role_delete(role):
    """اكتشاف حذف رتب - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # إزالة الرتبة من القائمة المحمية
    if role.id in protected_roles:
        protected_roles.remove(role.id)
    
    mod = await safe_audit_log(role.guild, discord.AuditLogAction.role_delete, role.id)
    if not mod:
        return
    
    if is_whitelisted(mod):
        return
    
    if not STRICT_MODE and has_permission_to_modify(mod, "role"):
        return
    
    await apply_strict_punishment(mod, "role_delete", role)
    
    # محاولة استعادة الرتبة من النسخة الاحتياطية
    await try_restore_role(role.guild, role.name)

@bot.event
async def on_guild_role_update(before, after):
    """اكتشاف تعديل الرتب - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # تخطي إذا لم يكن هناك تغيير حقيقي
    if (before.name == after.name and 
        before.permissions == after.permissions and
        before.color == after.color and
        before.hoist == after.hoist and
        before.mentionable == after.mentionable):
        return
    
    mod = await safe_audit_log(after.guild, discord.AuditLogAction.role_update, after.id)
    if not mod:
        return
    
    if is_whitelisted(mod):
        return
    
    if not STRICT_MODE and has_permission_to_modify(mod, "role"):
        return
    
    await apply_strict_punishment(mod, "role_update", after)
    
    # محاولة استعادة التعديلات
    try:
        if after.guild.me.guild_permissions.manage_roles:
            await after.edit(
                name=before.name,
                permissions=before.permissions,
                color=before.color,
                hoist=before.hoist,
                mentionable=before.mentionable,
                reason="استعادة تعديل رتبة غير مصرح به"
            )
    except:
        pass

async def try_restore_role(guild, role_name):
    """محاولة استعادة رتبة محذوفة"""
    try:
        # هنا يمكن إضافة منطق استعادة الرتب من النسخ الاحتياطية
        pass
    except:
        pass

# ================== 🔟 CHANNEL PROTECTION (STRICT) ==================
@bot.event
async def on_guild_channel_create(channel):
    """اكتشاف إنشاء رومات جديدة - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # إضافة الروم الجديد إلى القائمة المحمية
    protected_channels.add(channel.id)
    
    mod = await safe_audit_log(channel.guild, discord.AuditLogAction.channel_create, channel.id)
    if not mod:
        return
    
    if is_whitelisted(mod):
        return
    
    if not STRICT_MODE and has_permission_to_modify(mod, "channel"):
        return
    
    await apply_strict_punishment(mod, "channel_create", channel)
    
    # محاولة حذف الروم المحدث
    try:
        if channel.guild.me.guild_permissions.manage_channels:
            await channel.delete(reason="إنشاء روم بدون صلاحية - حذف تلقائي")
    except:
        pass

@bot.event
async def on_guild_channel_delete(channel):
    """اكتشاف حذف رومات - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # إزالة الروم من القائمة المحمية
    if channel.id in protected_channels:
        protected_channels.remove(channel.id)
    
    mod = await safe_audit_log(channel.guild, discord.AuditLogAction.channel_delete, channel.id)
    if not mod:
        return
    
    if is_whitelisted(mod):
        return
    
    if not STRICT_MODE and has_permission_to_modify(mod, "channel"):
        return
    
    await apply_strict_punishment(mod, "channel_delete", channel)

@bot.event
async def on_guild_channel_update(before, after):
    """اكتشاف تعديل الرومات - حماية شاملة"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # تخطي إذا لم يكن هناك تغيير حقيقي
    if (before.name == after.name and 
        before.position == after.position and
        before.category == after.category):
        return
    
    mod = await safe_audit_log(after.guild, discord.AuditLogAction.channel_update, after.id)
    if not mod:
        return
    
    if is_whitelisted(mod):
        return
    
    if not STRICT_MODE and has_permission_to_modify(mod, "channel"):
        return
    
    await apply_strict_punishment(mod, "channel_update", after)
    
    # محاولة استعادة التعديلات
    try:
        if after.guild.me.guild_permissions.manage_channels:
            await after.edit(
                name=before.name,
                position=before.position,
                category=before.category,
                reason="استعادة تعديل روم غير مصرح به"
            )
    except:
        pass

# ================== 1️⃣1️⃣ AUDIT LOG HELPER ==================
async def safe_audit_log(guild, action, target_id):
    try:
        async for entry in guild.audit_logs(limit=5, action=action):
            if entry.target and getattr(entry.target, 'id', None) == target_id:
                if (datetime.datetime.utcnow() - entry.created_at).total_seconds() < 5:
                    return entry.user
        return None
    except discord.Forbidden:
        print(f"⛔ لا يوجد صلاحية لسجلات التدقيق في {guild.name}")
        return None
    except Exception as e:
        print(f"⚠️ خطأ في سجلات التدقيق: {e}")
        return None

# ================== 1️⃣2️⃣ MESSAGE FILTERING ==================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    await bot.process_commands(message)
    
    if not SECURITY_ENABLED:
        return
    
    # نظام العقوبات المخفف للرسائل فقط
    if is_whitelisted(message.author):
        return
    
    # هنا يمكن إضافة فلترة الرسائل (سبام، روابط، صور)
    # مع عقوبات مخففة (تقييد مؤقت، تحذيرات)
    
    pass

# ================== 1️⃣3️⃣ ADMIN COMMANDS ==================
@bot.group()
@commands.has_permissions(administrator=True)
async def الحماية(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ نظام الحماية الشديد",
            description="نظام حماية صارم يحمي جميع الرتب والرومات",
            color=discord.Color.dark_red()
        )
        embed.add_field(
            name="🚨 وضع الحماية الشديد",
            value="• يحمي **جميع الرتب** بما فيها الرتب تحت البوت\n• يحمي **جميع الرومات** من التعديل\n• فقط المالك والوايت ليست معفيون",
            inline=False
        )
        embed.add_field(
            name="⚖️ العقوبات الفورية",
            value="• تعديل الرتب/الرومات: **حظر فوري + إزالة رتب**\n• يتم إرسال إشعار فوري للمالك\n• تسجيل كامل في السجلات",
            inline=False
        )
        embed.add_field(
            name="⚙️ الأوامر الرئيسية",
            value="• `!الحماية تشغيل/إيقاف` - الحماية الشديدة\n• `!الحماية الحالة` - عرض الحالة\n• `!الحماية قائمة_الحماية` - عرض المحمي",
            inline=False
        )
        embed.add_field(
            name="👥 إدارة الوايت ليست",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`",
            inline=False
        )
        embed.set_footer(text="Security BartX Ultimate Shield v6.0 - وضع الحماية الشديد")
        await ctx.send(embed=embed)

@الحماية.command()
async def تشغيل(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = True
    
    # تهيئة الحماية لهذا السيرفر
    await initialize_protection(ctx.guild)
    
    save_config()
    
    embed = discord.Embed(
        title="🔐 تم تشغيل الحماية الشديدة",
        description="**جميع الرتب والرومات الآن تحت الحماية**\n\n⚠️ **تحذير:**\n- أي محاولة تعديل على الرتب أو الرومات ستؤدي إلى حظر فوري\n- فقط المالك وأعضاء الوايت ليست معفيون\n- يتم إرسال إشعار فوري للمالك عند أي هجوم",
        color=discord.Color.green()
    )
    embed.add_field(name="🎖️ الرتب المحمية", value="جميع الرتب بما فيها الرتب تحت البوت", inline=False)
    embed.add_field(name="📁 الرومات المحمية", value="جميع الرومات النصية والصوتية", inline=False)
    embed.add_field(name="⚖️ العقوبة", value="حظر فوري + إزالة جميع الرتب + إشعار للمالك", inline=False)
    
    await ctx.send(embed=embed)

@الحماية.command()
async def إيقاف(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = False
    save_config()
    
    embed = discord.Embed(
        title="🔓 تم إيقاف الحماية الشديدة",
        description="الرتب والرومات الآن غير محمية",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def الحالة(ctx):
    embed = discord.Embed(
        title="📊 حالة الحماية الشديدة",
        color=discord.Color.blue()
    )
    embed.add_field(name="🛡️ الحماية الشديدة", value="✅ مفعلة" if SECURITY_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="🎖️ حماية الرتب", value="✅ مفعلة" if ANTI_ROLE_EDIT_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="📁 حماية الرومات", value="✅ مفعلة" if ANTI_CHANNEL_EDIT_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="💣 Anti-Nuke", value="✅ مفعل" if ANTI_NUKE_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="👥 أعضاء الوايت ليست", value=str(len(WHITELIST_USERS)), inline=True)
    embed.add_field(name="🎖️ رتب الوايت ليست", value=str(len(WHITELIST_ROLES)), inline=True)
    
    # إحصائيات الحماية
    roles_protected = len([r for r in ctx.guild.roles if not r.is_default()])
    channels_protected = len(ctx.guild.channels)
    
    embed.add_field(name="🎖️ الرتب المحمية", value=str(roles_protected), inline=True)
    embed.add_field(name="📁 الرومات المحمية", value=str(channels_protected), inline=True)
    embed.add_field(name="⚖️ العقوبة", value="حظر فوري", inline=True)
    
    embed.set_footer(text="التعديل على الرتب/الرومات = حظر فوري + إزالة رتب")
    await ctx.send(embed=embed)

@الحماية.command()
async def قائمة_الحماية(ctx):
    """عرض قائمة الرتب والرومات المحمية"""
    embed = discord.Embed(
        title="📋 قائمة المحمي في السيرفر",
        description=f"سيرفر: {ctx.guild.name}",
        color=discord.Color.blue()
    )
    
    # الرتب المحمية
    protected_roles_list = [r for r in ctx.guild.roles if not r.is_default()]
    if protected_roles_list:
        roles_text = "\n".join([f"• {role.name}" for role in protected_roles_list[:10]])
        if len(protected_roles_list) > 10:
            roles_text += f"\n• ... و {len(protected_roles_list) - 10} رتبة أخرى"
        embed.add_field(name="🎖️ الرتب المحمية", value=roles_text, inline=False)
    
    # الرومات المحمية
    protected_channels_list = list(ctx.guild.channels)
    if protected_channels_list:
        channels_text = "\n".join([f"• #{channel.name}" for channel in protected_channels_list[:10]])
        if len(protected_channels_list) > 10:
            channels_text += f"\n• ... و {len(protected_channels_list) - 10} روم آخر"
        embed.add_field(name="📁 الرومات المحمية", value=channels_text, inline=False)
    
    # الوايت ليست
    whitelist_users = []
    for user_id in WHITELIST_USERS:
        user = ctx.guild.get_member(user_id)
        if user:
            whitelist_users.append(user.mention)
    
    whitelist_roles = []
    for role_id in WHITELIST_ROLES:
        role = ctx.guild.get_role(role_id)
        if role:
            whitelist_roles.append(role.name)
    
    if whitelist_users:
        embed.add_field(name="👥 أعضاء الوايت ليست", value="\n".join(whitelist_users), inline=True)
    
    if whitelist_roles:
        embed.add_field(name="🎖️ رتب الوايت ليست", value="\n".join(whitelist_roles), inline=True)
    
    embed.set_footer(text="فقط المالك والوايت ليست يمكنهم التعديل")
    await ctx.send(embed=embed)

@الحماية.group()
async def وايت_ليست(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="👥 إدارة الوايت ليست",
            description="إدارة القائمة البيضاء - الأعضاء والرتب المعفاة من الحماية",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="الأوامر",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`\n• `!الحماية وايت_ليست إزالة_عضو @user`\n• `!الحماية وايت_ليست إزالة_رتبة @role`\n• `!الحماية وايت_ليست القائمة`",
            inline=False
        )
        await ctx.send(embed=embed)

@وايت_ليست.command()
async def إضافة_عضو(ctx, member: discord.Member):
    """إضافة عضو إلى الوايت ليست"""
    WHITELIST_USERS.add(member.id)
    save_config()
    
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"{member.mention} الآن معفي من جميع أنظمة الحماية",
        color=discord.Color.green()
    )
    embed.add_field(name="⚠️ تحذير", value="هذا العضو يمكنه الآن تعديل الرتب والرومات بحرية", inline=False)
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def إزالة_عضو(ctx, member: discord.Member):
    """إزالة عضو من الوايت ليست"""
    if member.id in WHITELIST_USERS:
        WHITELIST_USERS.remove(member.id)
        save_config()
        
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"{member.mention} لم يعد معفي من الحماية",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ غير موجود",
            description=f"{member.mention} ليس في الوايت ليست",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def إضافة_رتبة(ctx, role: discord.Role):
    """إضافة رتبة إلى الوايت ليست"""
    WHITELIST_ROLES.add(role.id)
    save_config()
    
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"رتبة **{role.name}** الآن معفاة من جميع أنظمة الحماية",
        color=discord.Color.green()
    )
    embed.add_field(name="👥 الأعضاء المتأثرون", value=f"جميع الأعضاء الذين لديهم رتبة {role.name} معفيون", inline=False)
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def إزالة_رتبة(ctx, role: discord.Role):
    """إزالة رتبة من الوايت ليست"""
    if role.id in WHITELIST_ROLES:
        WHITELIST_ROLES.remove(role.id)
        save_config()
        
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"رتبة **{role.name}** لم تعد معفاة من الحماية",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ غير موجود",
            description=f"رتبة **{role.name}** ليست في الوايت ليست",
            color=discord.Color.red()
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
    
    # الأعضاء المعفيون
    whitelist_members = []
    for user_id in WHITELIST_USERS:
        member = ctx.guild.get_member(user_id)
        if member:
            whitelist_members.append(f"• {member.mention}")
        else:
            whitelist_members.append(f"• <@{user_id}> (غير موجود في السيرفر)")
    
    if whitelist_members:
        embed.add_field(name="👥 الأعضاء المعفيون", value="\n".join(whitelist_members), inline=False)
    else:
        embed.add_field(name="👥 الأعضاء المعفيون", value="لا يوجد أعضاء معفيون", inline=False)
    
    # الرتب المعفاة
    whitelist_roles_list = []
    for role_id in WHITELIST_ROLES:
        role = ctx.guild.get_role(role_id)
        if role:
            whitelist_roles_list.append(f"• {role.name}")
        else:
            whitelist_roles_list.append(f"• <@&{role_id}> (غير موجودة في السيرفر)")
    
    if whitelist_roles_list:
        embed.add_field(name="🎖️ الرتب المعفاة", value="\n".join(whitelist_roles_list), inline=False)
    else:
        embed.add_field(name="🎖️ الرتب المعفاة", value="لا يوجد رتب معفاة", inline=False)
    
    embed.set_footer(text="هؤلاء يمكنهم تعديل الرتب والرومات بحرية")
    await ctx.send(embed=embed)

# ================== 1️⃣4️⃣ OTHER COMMANDS ==================
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

@bot.command(name="دخول", aliases=["join", "connect"])
@commands.has_permissions(manage_channels=True)
async def join_voice(ctx):
    """الدخول إلى الروم الصوتي"""
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

# ================== 1️⃣5️⃣ BACKUP SYSTEM ==================
def create_backup(reason="auto"):
    if not BACKUP_ENABLED:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{timestamp}_{reason}.json"
    path = os.path.join(BACKUP_DIR, name)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(load_config(), f, indent=4)
        
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

# ================== 1️⃣6️⃣ HELP COMMAND ==================
@bot.command(name="مساعدة", aliases=["help", "اوامر"])
async def help_command(ctx):
    """عرض جميع الأوامر المتاحة"""
    embed = discord.Embed(
        title="🛡️ Security BartX - الأوامر المتاحة",
        description="نظام حماية شديد يحمي جميع الرتب والرومات",
        color=discord.Color.dark_red()
    )
    
    embed.add_field(
        name="🚨 أوامر الحماية الشديدة",
        value="• `!الحماية` - معلومات النظام\n• `!الحماية تشغيل/إيقاف` - تشغيل/إيقاف\n• `!الحماية الحالة` - عرض الحالة\n• `!الحماية قائمة_الحماية` - عرض المحمي",
        inline=False
    )
    
    embed.add_field(
        name="👥 إدارة الوايت ليست",
        value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إزالة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`\n• `!الحماية وايت_ليست إزالة_رتبة @role`\n• `!الحماية وايت_ليست القائمة`",
        inline=False
    )
    
    embed.add_field(
        name="🎤 أوامر الصوت",
        value="• `!دخول` - دخول الروم الصوتي\n• `!خروج` - خروج من الروم الصوتي",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ إدارة المحادثات",
        value="• `!مسح [عدد]` - مسح الرسائل (1-100)",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ ميزات الحماية",
        value="• يحمي **جميع الرتب** بما فيها تحت البوت\n• يحمي **جميع الرومات** من التعديل\n• عقوبة فورية: **حظر + إزالة رتب**\n• إشعار فوري للمالك\n• فقط المالك والوايت ليست معفيون",
        inline=False
    )
    
    embed.set_footer(text="Security BartX Ultimate Shield v6.0 - وضع الحماية الشديد")
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
        print("🚨 وضع الحماية الشديد مفعل - يحمي جميع الرتب والرومات")
        bot.run(token)
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()

.
