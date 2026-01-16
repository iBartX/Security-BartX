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
from collections import defaultdict

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
                    <h2>🚨 وضع الحماية المباشر مفعل</h2>
                    <p>النظام يراقب <strong>جميع التغييرات مباشرة</strong> بدون استخدام Audit Logs</p>
                    <p>يكتشف ويوقف أي تعديل على الرتب والرومات فوراً</p>
                </div>
                
                <div class="box">
                    <h2>📊 حالة النظام</h2>
                    <div class="toggle">
                        <span>🛡️ الحماية المباشرة:</span>
                        <strong>{'✅ مفعلة' if cfg.get('security_enabled', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>🎖️ مراقبة الرتب:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_role_edit', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>📁 مراقبة الرومات:</span>
                        <strong>{'✅ مفعلة' if cfg.get('anti_channel_edit', True) else '❌ معطلة'}</strong>
                    </div>
                    <div class="toggle">
                        <span>👥 أعضاء الوايت ليست:</span>
                        <strong>{len(cfg.get('whitelist_users', []))}</strong>
                    </div>
                    <div class="toggle">
                        <span>🎖️ رتب الوايت ليست:</span>
                        <strong>{len(cfg.get('whitelist_roles', []))}</strong>
                    </div>
                    <div class="toggle">
                        <span>📊 التعديلات المكتشفة:</span>
                        <strong id="detectedCount">جاري التحميل...</strong>
                    </div>
                </div>
                
                <div class="box">
                    <h2>🎮 التحكم السريع</h2>
                    <form action="/toggle_security" method="post">
                        <button class="btn" type="submit">⚡ تبديل الحماية</button>
                    </form>
                    <form action="/toggle_role_protection" method="post">
                        <button class="btn" type="submit">🎖️ تبديل مراقبة الرتب</button>
                    </form>
                    <form action="/toggle_channel_protection" method="post">
                        <button class="btn" type="submit">📁 تبديل مراقبة الرومات</button>
                    </form>
                    <form action="/force_protect" method="post">
                        <button class="btn" type="submit">🛡️ فرض الحماية الآن</button>
                    </form>
                    <form action="/backup_now" method="post">
                        <button class="btn" type="submit">💾 إنشاء نسخة احتياطية</button>
                    </form>
                </div>
                
                <div class="box">
                    <h2>⚖️ العقوبات الفورية</h2>
                    <div class="toggle">
                        <span>التعديل على الرتب:</span>
                        <strong>🔨 حظر فوري + إزالة رتب</strong>
                    </div>
                    <div class="toggle">
                        <span>التعديل على الرومات:</span>
                        <strong>🔨 حظر فوري + إزالة رتب</strong>
                    </div>
                    <div class="toggle">
                        <span>إنشاء رتب/رومات:</span>
                        <strong>🔨 حظر فوري + حذف الشيء</strong>
                    </div>
                    <p style="margin-top:10px;color:#94a3b8">النظام لا يحتاج إلى صلاحيات Audit Logs</p>
                </div>
                
                <p style="text-align:center;margin-top:30px;color:#94a3b8">
                    © 2024 Security BartX Ultimate Shield v7.0
                </p>
            </div>
            
            <script>
                // تحديث عدد التعديلات المكتشفة
                async function updateStats() {{
                    try {{
                        const response = await fetch('/api/stats');
                        const data = await response.json();
                        document.getElementById('detectedCount').innerText = data.detected_changes || '0';
                    }} catch (error) {{
                        console.error('خطأ في تحديث الإحصائيات:', error);
                    }}
                }}
                
                // تحديث كل 10 ثواني
                setInterval(updateStats, 10000);
                updateStats();
            </script>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ في التحميل</h1><p>{str(e)}</p>"

@app.route("/api/stats")
def api_stats():
    try:
        return {"detected_changes": len(detected_changes)}
    except:
        return {"detected_changes": 0}

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
                <p>الحماية المباشرة الآن: <strong>{new_state}</strong></p>
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
                <p>مراقبة الرتب الآن: <strong>{new_state}</strong></p>
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
                <p>مراقبة الرومات الآن: <strong>{new_state}</strong></p>
                <a href='/dashboard'><button class="btn">↩️ رجوع للوحة التحكم</button></a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"<h1>خطأ</h1><p>{str(e)}</p>"

@app.route("/force_protect", methods=['POST'])
def force_protect():
    try:
        # إعادة تهيئة الحماية لجميع السيرفرات
        for guild in bot.guilds:
            asyncio.run_coroutine_threadsafe(
                initialize_guild_protection(guild),
                bot.loop
            )
        
        return f"""
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body {{ background:#0f172a;color:white;padding:50px;text-align:center;font-family:Tahoma }}
        .success {{ background:#166534;padding:20px;border-radius:10px;margin:20px auto;max-width:500px }}
        .btn {{ background:#22c55e;color:white;padding:10px 20px;border:none;border-radius:5px;margin-top:20px;cursor:pointer }}
        </style></head>
        <body>
            <div class="success">
                <h2>✅ تم فرض الحماية</h2>
                <p>تم إعادة تهيئة الحماية لجميع السيرفرات</p>
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
PROTECTION_FILE = "protection_data.json"
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
    "direct_protection": True,  # الحماية المباشرة بدون Audit Logs
    "auto_restore": True,      # الاستعادة التلقائية
    "instant_ban": True        # الحظر الفوري
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
            "direct_protection": DIRECT_PROTECTION,
            "auto_restore": AUTO_RESTORE,
            "instant_ban": INSTANT_BAN
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

def load_protection_data():
    """تحميل بيانات الحماية المحفوظة"""
    try:
        if not os.path.exists(PROTECTION_FILE):
            return {"roles": {}, "channels": {}, "guilds": {}}
        
        with open(PROTECTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في تحميل بيانات الحماية: {e}")
        return {"roles": {}, "channels": {}, "guilds": {}}

def save_protection_data():
    """حفظ بيانات الحماية"""
    try:
        # جمع بيانات الرتب المحمية
        roles_data = {}
        for guild_id, roles in protected_roles.items():
            roles_data[str(guild_id)] = []
            for role_id in roles:
                try:
                    guild = bot.get_guild(guild_id)
                    if guild:
                        role = guild.get_role(role_id)
                        if role:
                            roles_data[str(guild_id)].append({
                                "id": role_id,
                                "name": role.name,
                                "color": role.color.value,
                                "permissions": role.permissions.value,
                                "position": role.position,
                                "hoist": role.hoist,
                                "mentionable": role.mentionable
                            })
                except:
                    continue
        
        # جمع بيانات الرومات المحمية
        channels_data = {}
        for guild_id, channels in protected_channels.items():
            channels_data[str(guild_id)] = []
            for channel_id in channels:
                try:
                    guild = bot.get_guild(guild_id)
                    if guild:
                        channel = guild.get_channel(channel_id)
                        if channel:
                            channels_data[str(guild_id)].append({
                                "id": channel_id,
                                "name": channel.name,
                                "type": str(channel.type),
                                "position": channel.position,
                                "category_id": channel.category_id
                            })
                except:
                    continue
        
        data = {
            "roles": roles_data,
            "channels": channels_data,
            "last_update": datetime.datetime.now().isoformat()
        }
        
        with open(PROTECTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        print("✅ تم حفظ بيانات الحماية")
    except Exception as e:
        print(f"❌ خطأ في حفظ بيانات الحماية: {e}")

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
DIRECT_PROTECTION = config.get("direct_protection", True)
AUTO_RESTORE = config.get("auto_restore", True)
INSTANT_BAN = config.get("instant_ban", True)

# ================== 4️⃣ GLOBAL STATE ==================
rate_cache = {}
nuke_tracker = {}
spam_tracker = {}
voice_connections = {}
detected_changes = []

# تخزين الحالة الأصلية للرتب والرومات
protected_roles = defaultdict(set)  # {guild_id: {role_ids}}
protected_channels = defaultdict(set)  # {guild_id: {channel_ids}}
role_backups = defaultdict(dict)  # {guild_id: {role_id: role_data}}
channel_backups = defaultdict(dict)  # {guild_id: {channel_id: channel_data}}

# ================== 5️⃣ READY & INITIALIZATION ==================
@bot.event
async def on_ready():
    print(f"🛡️ {bot.user} ONLINE | JSON CONFIG LOADED")
    print(f"📊 عدد السيرفرات: {len(bot.guilds)}")
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="حماية مباشرة | !الحماية"
        )
    )
    
    # تحميل بيانات الحماية المحفوظة
    protection_data = load_protection_data()
    
    # تهيئة الحماية لجميع السيرفرات
    for guild in bot.guilds:
        await initialize_guild_protection(guild, protection_data)
    
    if BACKUP_ENABLED:
        auto_backup.start()
        protection_backup.start()
        print(f"✅ نظام النسخ الاحتياطي مفعل")
    
    print("✅ وضع الحماية المباشر مفعل - لا يحتاج إلى صلاحيات Audit Logs")
    print("✅ النظام يراقب جميع التغييرات مباشرة")

async def initialize_guild_protection(guild, protection_data=None):
    """تهيئة الحماية للسيرفر"""
    try:
        print(f"🔄 تهيئة الحماية لسيرفر: {guild.name}")
        
        # حفظ الحالة الأصلية للرتب
        for role in guild.roles:
            if not role.is_default():  # تخطي رتبة @everyone
                protected_roles[guild.id].add(role.id)
                role_backups[guild.id][role.id] = {
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "position": role.position,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable,
                    "timestamp": datetime.datetime.now().isoformat()
                }
        
        # حفظ الحالة الأصلية للرومات
        for channel in guild.channels:
            protected_channels[guild.id].add(channel.id)
            channel_backups[guild.id][channel.id] = {
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "category_id": channel.category_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        print(f"✅ تم تهيئة الحماية لسيرفر: {guild.name}")
        print(f"   - الرتب المحمية: {len(protected_roles[guild.id])}")
        print(f"   - الرومات المحمية: {len(protected_channels[guild.id])}")
        
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

async def find_suspect(guild, action_type, target_id=None):
    """محاولة العثور على المشتبه به بدون Audit Logs"""
    try:
        # طريقة بسيطة: البحث في الأعضاء النشطين
        for member in guild.members:
            if is_whitelisted(member):
                continue
            
            # فحص إذا كان لدى العضو صلاحيات للتعديل
            if action_type == "role":
                if member.guild_permissions.manage_roles:
                    return member
            elif action_type == "channel":
                if member.guild_permissions.manage_channels:
                    return member
        
        return None
    except:
        return None

# ================== 8️⃣ DIRECT PROTECTION SYSTEM ==================
async def detect_and_respond(guild, change_type, target=None, old_data=None, new_data=None):
    """اكتشاف التغييرات والاستجابة مباشرة"""
    if not SECURITY_ENABLED:
        return
    
    # البحث عن المشتبه به
    suspect = await find_suspect(guild, "role" if "role" in change_type else "channel")
    
    if suspect and not is_whitelisted(suspect):
        await handle_detected_change(guild, suspect, change_type, target, old_data, new_data)

async def handle_detected_change(guild, member, change_type, target=None, old_data=None, new_data=None):
    """معالجة التغيير المكتشف"""
    try:
        # تسجيل التغيير
        change_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "guild": guild.name,
            "guild_id": guild.id,
            "member": f"{member.name}#{member.discriminator}",
            "member_id": member.id,
            "change_type": change_type,
            "target": target.name if target else None,
            "target_id": target.id if target else None
        }
        
        detected_changes.append(change_record)
        if len(detected_changes) > 100:
            detected_changes.pop(0)
        
        reason_messages = {
            "role_create": "إنشاء رتبة جديدة بدون صلاحية",
            "role_delete": "حذف رتبة بدون صلاحية",
            "role_update": "تعديل رتبة بدون صلاحية",
            "channel_create": "إنشاء روم جديد بدون صلاحية",
            "channel_delete": "حذف روم بدون صلاحية",
            "channel_update": "تعديل روم بدون صلاحية"
        }
        
        reason = reason_messages.get(change_type, "تعديل غير مصرح به")
        
        # تطبيق العقوبة الفورية
        await apply_instant_punishment(member, reason, target)
        
        # محاولة الاستعادة التلقائية
        if AUTO_RESTORE:
            await try_auto_restore(guild, change_type, target, old_data)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في معالجة التغيير: {e}")
        return False

async def apply_instant_punishment(member, reason, target=None):
    """تطبيق عقوبة فورية"""
    if not INSTANT_BAN:
        return
    
    try:
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
            # إذا لم نستطع الحظر، نحاول الطرد
            try:
                if member.guild.me.guild_permissions.kick_members:
                    await member.kick(reason=f"عقوبة: {reason}")
            except:
                pass
        
        # 3. إرسال إشعار
        alert_embed = discord.Embed(
            title="🚨 عقوبة فورية تطبيق",
            description=f"تم اكتشاف وتوقيف تعديل غير مصرح به",
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        alert_embed.add_field(name="👤 المتعدي", value=f"{member.mention} ({member.id})", inline=False)
        alert_embed.add_field(name="📝 السبب", value=reason, inline=False)
        
        if target:
            if isinstance(target, discord.Role):
                alert_embed.add_field(name="🎖️ الرتبة", value=target.name, inline=False)
            elif isinstance(target, discord.abc.GuildChannel):
                alert_embed.add_field(name="📁 الروم", value=target.name, inline=False)
        
        alert_embed.add_field(name="⚖️ العقوبة", value="حظر فوري + إزالة جميع الرتب", inline=False)
        
        await send_to_logs(member.guild, alert_embed)
        
        # 4. إشعار للمالك
        try:
            owner = member.guild.owner
            if owner:
                dm_embed = discord.Embed(
                    title="🚨 تنبيه أمني عاجل",
                    description=f"تم اكتشاف هجوم على سيرفرك **{member.guild.name}**",
                    color=discord.Color.dark_red(),
                    timestamp=datetime.datetime.utcnow()
                )
                dm_embed.add_field(name="👤 المهاجم", value=f"{member} ({member.id})", inline=False)
                dm_embed.add_field(name="🎯 الهجوم", value=reason, inline=False)
                dm_embed.add_field(name="🛡️ الإجراء", value="تم حظره وإزالة جميع رتبه", inline=False)
                dm_embed.set_footer(text="Security BartX Ultimate Shield")
                
                await owner.send(embed=dm_embed)
        except:
            pass
        
    except Exception as e:
        print(f"❌ خطأ في تطبيق العقوبة: {e}")

async def try_auto_restore(guild, change_type, target, old_data):
    """محاولة الاستعادة التلقائية"""
    try:
        if change_type == "role_update" and target and old_data:
            if guild.me.guild_permissions.manage_roles:
                await target.edit(
                    name=old_data.get("name", target.name),
                    color=discord.Color(old_data.get("color", target.color.value)),
                    hoist=old_data.get("hoist", target.hoist),
                    mentionable=old_data.get("mentionable", target.mentionable),
                    reason="استعادة تلقائية بعد تعديل غير مصرح"
                )
        
        elif change_type == "channel_update" and target and old_data:
            if guild.me.guild_permissions.manage_channels:
                await target.edit(
                    name=old_data.get("name", target.name),
                    reason="استعادة تلقائية بعد تعديل غير مصرح"
                )
        
        elif change_type == "role_delete":
            # يمكن محاولة إنشاء الرتبة مرة أخرى
            pass
        
        elif change_type == "channel_delete":
            # يمكن محاولة إنشاء الروم مرة أخرى
            pass
            
    except Exception as e:
        print(f"❌ خطأ في الاستعادة التلقائية: {e}")

# ================== 9️⃣ PERIODIC CHECKING ==================
@tasks.loop(minutes=1)
async def periodic_protection_check():
    """فحص دوري للحماية"""
    if not SECURITY_ENABLED:
        return
    
    for guild in bot.guilds:
        try:
            await check_guild_protection(guild)
        except Exception as e:
            print(f"❌ خطأ في الفحص الدوري لسيرفر {guild.name}: {e}")

async def check_guild_protection(guild):
    """فحص حماية السيرفر"""
    try:
        # فحص الرتب
        current_roles = {role.id for role in guild.roles if not role.is_default()}
        protected = protected_roles.get(guild.id, set())
        
        # اكتشاف الرتب المحذوفة
        deleted_roles = protected - current_roles
        for role_id in deleted_roles:
            if role_id in role_backups.get(guild.id, {}):
                await detect_and_respond(guild, "role_delete")
                protected_roles[guild.id].discard(role_id)
        
        # اكتشاف الرتب الجديدة
        new_roles = current_roles - protected
        for role_id in new_roles:
            role = guild.get_role(role_id)
            if role:
                protected_roles[guild.id].add(role_id)
                await detect_and_respond(guild, "role_create", role)
        
        # فحص الرومات
        current_channels = {channel.id for channel in guild.channels}
        protected_ch = protected_channels.get(guild.id, set())
        
        # اكتشاف الرومات المحذوفة
        deleted_channels = protected_ch - current_channels
        for channel_id in deleted_channels:
            await detect_and_respond(guild, "channel_delete")
            protected_channels[guild.id].discard(channel_id)
        
        # اكتشاف الرومات الجديدة
        new_channels = current_channels - protected_ch
        for channel_id in new_channels:
            channel = guild.get_channel(channel_id)
            if channel:
                protected_channels[guild.id].add(channel_id)
                await detect_and_respond(guild, "channel_create", channel)
                
    except Exception as e:
        print(f"❌ خطأ في فحص حماية سيرفر {guild.name}: {e}")

@tasks.loop(minutes=5)
async def protection_backup():
    """نسخ احتياطي دوري لبيانات الحماية"""
    save_protection_data()

# ================== 🔟 EVENT-BASED PROTECTION ==================
@bot.event
async def on_guild_role_create(role):
    """اكتشاف إنشاء رتب جديدة"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # إضافة إلى القائمة المحمية
    protected_roles[role.guild.id].add(role.id)
    
    # تسجيل النسخة الاحتياطية
    role_backups[role.guild.id][role.id] = {
        "name": role.name,
        "color": role.color.value,
        "permissions": role.permissions.value,
        "position": role.position,
        "hoist": role.hoist,
        "mentionable": role.mentionable,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    await detect_and_respond(role.guild, "role_create", role)

@bot.event
async def on_guild_role_delete(role):
    """اكتشاف حذف رتب"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # إزالة من القائمة المحمية
    if role.id in protected_roles.get(role.guild.id, set()):
        protected_roles[role.guild.id].discard(role.id)
    
    await detect_and_respond(role.guild, "role_delete")

@bot.event
async def on_guild_role_update(before, after):
    """اكتشاف تعديل الرتب"""
    if not SECURITY_ENABLED or not ANTI_ROLE_EDIT_ENABLED:
        return
    
    # تخطي إذا لم يكن هناك تغيير حقيقي
    if (before.name == after.name and 
        before.permissions == after.permissions and
        before.color == after.color and
        before.hoist == after.hoist and
        before.mentionable == after.mentionable):
        return
    
    # حفظ البيانات القديمة
    old_data = {
        "name": before.name,
        "color": before.color.value,
        "permissions": before.permissions.value,
        "hoist": before.hoist,
        "mentionable": before.mentionable
    }
    
    await detect_and_respond(after.guild, "role_update", after, old_data)

@bot.event
async def on_guild_channel_create(channel):
    """اكتشاف إنشاء رومات جديدة"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # إضافة إلى القائمة المحمية
    protected_channels[channel.guild.id].add(channel.id)
    
    # تسجيل النسخة الاحتياطية
    channel_backups[channel.guild.id][channel.id] = {
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "category_id": channel.category_id,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    await detect_and_respond(channel.guild, "channel_create", channel)

@bot.event
async def on_guild_channel_delete(channel):
    """اكتشاف حذف رومات"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # إزالة من القائمة المحمية
    if channel.id in protected_channels.get(channel.guild.id, set()):
        protected_channels[channel.guild.id].discard(channel.id)
    
    await detect_and_respond(channel.guild, "channel_delete")

@bot.event
async def on_guild_channel_update(before, after):
    """اكتشاف تعديل الرومات"""
    if not SECURITY_ENABLED or not ANTI_CHANNEL_EDIT_ENABLED:
        return
    
    # تخطي إذا لم يكن هناك تغيير حقيقي
    if before.name == after.name and before.position == after.position:
        return
    
    # حفظ البيانات القديمة
    old_data = {
        "name": before.name,
        "position": before.position,
        "category_id": before.category_id
    }
    
    await detect_and_respond(after.guild, "channel_update", after, old_data)

# ================== 1️⃣1️⃣ ADMIN COMMANDS ==================
@bot.group()
@commands.has_permissions(administrator=True)
async def الحماية(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ نظام الحماية المباشر",
            description="نظام حماية يراقب جميع التغييرات مباشرة بدون Audit Logs",
            color=discord.Color.dark_red()
        )
        embed.add_field(
            name="🚨 كيف يعمل النظام",
            value="• يراقب **جميع التغييرات** في الرتب والرومات مباشرة\n• **لا يحتاج** إلى صلاحيات Audit Logs\n• يكتشف التعديلات **فور حدوثها**\n• يتصرف **تلقائياً** بدون تدخل",
            inline=False
        )
        embed.add_field(
            name="⚖️ العقوبات الفورية",
            value="• **حظر فوري** لأي متعدي\n• **إزالة جميع رتب** المهاجم\n• **إشعار فوري** للمالك\n• **استعادة تلقائية** للتعديلات",
            inline=False
        )
        embed.add_field(
            name="⚙️ الأوامر الرئيسية",
            value="• `!الحماية تشغيل/إيقاف` - تشغيل/إيقاف النظام\n• `!الحماية الحالة` - عرض حالة الحماية\n• `!الحماية التعديلات` - عرض التعديلات المكتشفة\n• `!الحماية تحديث` - إعادة تهيئة الحماية",
            inline=False
        )
        embed.add_field(
            name="👥 إدارة الوايت ليست",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست القائمة`",
            inline=False
        )
        embed.set_footer(text="Security BartX Ultimate Shield v7.0 - الحماية المباشرة")
        await ctx.send(embed=embed)

@الحماية.command()
async def تشغيل(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = True
    
    # تهيئة الحماية
    await initialize_guild_protection(ctx.guild)
    
    # بدء المهام الدورية
    periodic_protection_check.start()
    
    save_config()
    
    embed = discord.Embed(
        title="🔐 تم تشغيل الحماية المباشرة",
        description="**النظام الآن يراقب جميع التغييرات مباشرة**\n\n🎯 **مميزات النظام:**\n- يراقب إنشاء/حذف/تعديل الرتب والرومات\n- لا يحتاج إلى صلاحيات Audit Logs\n- يستجيب فوراً لأي تعديل\n- يطبق عقوبات فورية",
        color=discord.Color.green()
    )
    embed.add_field(name="📊 طريقة العمل", value="المراقبة المباشرة + الفحص الدوري", inline=False)
    embed.add_field(name="⚡ سرعة الاستجابة", value="فورية - خلال ثواني", inline=False)
    embed.add_field(name="🛡️ الحماية", value="جميع الرتب والرومات", inline=False)
    
    await ctx.send(embed=embed)

@الحماية.command()
async def إيقاف(ctx):
    global SECURITY_ENABLED
    SECURITY_ENABLED = False
    
    # إيقاف المهام الدورية
    periodic_protection_check.stop()
    
    save_config()
    
    embed = discord.Embed(
        title="🔓 تم إيقاف الحماية المباشرة",
        description="النظام متوقف عن المراقبة",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def الحالة(ctx):
    embed = discord.Embed(
        title="📊 حالة الحماية المباشرة",
        color=discord.Color.blue()
    )
    embed.add_field(name="🛡️ الحماية المباشرة", value="✅ مفعلة" if SECURITY_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="🎖️ مراقبة الرتب", value="✅ مفعلة" if ANTI_ROLE_EDIT_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="📁 مراقبة الرومات", value="✅ مفعلة" if ANTI_CHANNEL_EDIT_ENABLED else "❌ معطلة", inline=True)
    embed.add_field(name="⚡ الحظر الفوري", value="✅ مفعل" if INSTANT_BAN else "❌ معطل", inline=True)
    embed.add_field(name="🔄 الاستعادة", value="✅ مفعلة" if AUTO_RESTORE else "❌ معطلة", inline=True)
    embed.add_field(name="📊 التعديلات المكتشفة", value=str(len(detected_changes)), inline=True)
    
    # إحصائيات السيرفر
    roles_count = len(protected_roles.get(ctx.guild.id, set()))
    channels_count = len(protected_channels.get(ctx.guild.id, set()))
    
    embed.add_field(name="🎖️ الرتب المراقبة", value=str(roles_count), inline=True)
    embed.add_field(name="📁 الرومات المراقبة", value=str(channels_count), inline=True)
    embed.add_field(name="👥 المعفيون", value=str(len(WHITELIST_USERS) + len(WHITELIST_ROLES)), inline=True)
    
    embed.set_footer(text="النظام يعمل بدون صلاحيات Audit Logs")
    await ctx.send(embed=embed)

@الحماية.command()
async def التعديلات(ctx):
    """عرض التعديلات المكتشفة"""
    if not detected_changes:
        embed = discord.Embed(
            title="✅ لا توجد تعديلات",
            description="لم يتم اكتشاف أي تعديلات غير مصرح بها",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        return
    
    # عرض آخر 5 تعديلات
    recent_changes = detected_changes[-5:]
    
    embed = discord.Embed(
        title="📋 آخر التعديلات المكتشفة",
        description=f"إجمالي التعديلات: {len(detected_changes)}",
        color=discord.Color.orange()
    )
    
    for change in reversed(recent_changes):
        timestamp = datetime.datetime.fromisoformat(change["timestamp"]).strftime("%H:%M")
        embed.add_field(
            name=f"🕒 {timestamp} - {change['change_type']}",
            value=f"**المستخدم:** {change['member']}\n**السيرفر:** {change['guild']}\n**الهدف:** {change['target'] or 'غير معروف'}",
            inline=False
        )
    
    embed.set_footer(text="يعرض آخر 5 تعديلات فقط")
    await ctx.send(embed=embed)

@الحماية.command()
async def تحديث(ctx):
    """إعادة تهيئة الحماية"""
    await initialize_guild_protection(ctx.guild)
    
    embed = discord.Embed(
        title="🔄 تم تحديث الحماية",
        description=f"تم إعادة تهيئة الحماية لسيرفر **{ctx.guild.name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="🎖️ الرتب المراقبة", value=str(len(protected_roles.get(ctx.guild.id, set()))), inline=True)
    embed.add_field(name="📁 الرومات المراقبة", value=str(len(protected_channels.get(ctx.guild.id, set()))), inline=True)
    
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
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إزالة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`\n• `!الحماية وايت_ليست إزالة_رتبة @role`\n• `!الحماية وايت_ليست القائمة`",
            inline=False
        )
        await ctx.send(embed=embed)

@وايت_ليست.command()
async def إضافة_عضو(ctx, member: discord.Member):
    WHITELIST_USERS.add(member.id)
    save_config()
    
    embed = discord.Embed(
        title="✅ تمت الإضافة",
        description=f"{member.mention} الآن معفي من الحماية",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@وايت_ليست.command()
async def إزالة_عضو(ctx, member: discord.Member):
    if member.id in WHITELIST_USERS:
        WHITELIST_USERS.remove(member.id)
        save_config()
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"{member.mention} لم يعد معفي",
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
async def القائمة(ctx):
    """عرض قائمة الوايت ليست"""
    embed = discord.Embed(
        title="📋 قائمة الوايت ليست",
        color=discord.Color.blue()
    )
    
    # الأعضاء
    members_list = []
    for user_id in WHITELIST_USERS:
        member = ctx.guild.get_member(user_id)
        if member:
            members_list.append(f"• {member.mention}")
    
    if members_list:
        embed.add_field(name="👥 الأعضاء", value="\n".join(members_list), inline=False)
    else:
        embed.add_field(name="👥 الأعضاء", value="لا يوجد أعضاء", inline=False)
    
    # الرتب
    roles_list = []
    for role_id in WHITELIST_ROLES:
        role = ctx.guild.get_role(role_id)
        if role:
            roles_list.append(f"• {role.name}")
    
    if roles_list:
        embed.add_field(name="🎖️ الرتب", value="\n".join(roles_list), inline=False)
    else:
        embed.add_field(name="🎖️ الرتب", value="لا يوجد رتب", inline=False)
    
    await ctx.send(embed=embed)

# ================== 1️⃣2️⃣ OTHER COMMANDS ==================
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

# ================== 1️⃣3️⃣ BACKUP SYSTEM ==================
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

# ================== 1️⃣4️⃣ HELP COMMAND ==================
@bot.command(name="مساعدة", aliases=["help", "اوامر"])
async def help_command(ctx):
    """عرض جميع الأوامر المتاحة"""
    embed = discord.Embed(
        title="🛡️ Security BartX - الحماية المباشرة",
        description="نظام حماية يراقب التغييرات مباشرة بدون Audit Logs",
        color=discord.Color.dark_red()
    )
    
    embed.add_field(
        name="🚨 أوامر الحماية",
        value="• `!الحماية` - معلومات النظام\n• `!الحماية تشغيل/إيقاف` - تشغيل/إيقاف\n• `!الحماية الحالة` - عرض الحالة\n• `!الحماية التعديلات` - التعديلات المكتشفة\n• `!الحماية تحديث` - تحديث الحماية",
        inline=False
    )
    
    embed.add_field(
        name="👥 إدارة الوايت ليست",
        value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إزالة_عضو @user`\n• `!الحماية وايت_ليست القائمة`",
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
        value="• **مراقبة مباشرة** بدون Audit Logs\n• **اكتشاف فوري** للتعديلات\n• **حظر فوري** للمتعدين\n• **استعادة تلقائية**\n• **إشعارات للمالك**",
        inline=False
    )
    
    embed.set_footer(text="Security BartX Ultimate Shield v7.0 - يعمل بدون صلاحيات Audit Logs")
    await ctx.send(embed=embed)

# ================== 1️⃣5️⃣ RUN ==================
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
        print("🚨 وضع الحماية المباشر مفعل - لا يحتاج إلى Audit Logs")
        print("✅ النظام يراقب التغييرات مباشرة")
        bot.run(token)
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
