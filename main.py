import os
import json
import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from flask import Flask, request
from threading import Thread
import traceback

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
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10}
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ Security BartX Control Panel</h1>
                
                <div class="box">
                    <h2>📊 حالة النظام</h2>
                    <p>🔒 Anti-Nuke: <strong>{'✅ مفعل' if cfg.get('anti_nuke', True) else '❌ معطل'}</strong></p>
                    <p>🛡️ الحماية: <strong>{'✅ مفعلة' if cfg.get('security_enabled', True) else '❌ معطلة'}</strong></p>
                    <p>👥 أعضاء الوايت ليست: <strong>{len(cfg.get('whitelist_users', []))}</strong></p>
                    <p>🎖️ رتب الوايت ليست: <strong>{len(cfg.get('whitelist_roles', []))}</strong></p>
                    <p>💾 النسخ الاحتياطي: <strong>{'✅ مفعل' if cfg.get('backup', {}).get('enabled', True) else '❌ معطل'}</strong></p>
                </div>
                
                <div class="box">
                    <h2>🎮 التحكم السريع</h2>
                    <form action="/toggle_nuke" method="post">
                        <button class="btn" type="submit">🔁 تبديل Anti-Nuke</button>
                    </form>
                    <form action="/toggle_security" method="post">
                        <button class="btn" type="submit">⚡ تبديل الحماية</button>
                    </form>
                    <form action="/backup_now" method="post">
                        <button class="btn" type="submit">💾 إنشاء نسخة احتياطية</button>
                    </form>
                    <form action="/view_logs" method="get">
                        <button class="btn" type="submit">📜 عرض السجلات</button>
                    </form>
                </div>
                
                <div class="box">
                    <h2>📁 إدارة النسخ الاحتياطية</h2>
                    <p>عدد النسخ الاحتياطية: <strong>{len(os.listdir('backups')) if os.path.exists('backups') else 0}</strong></p>
                    <p>آخر تحديث: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p style="text-align:center;margin-top:30px;color:#94a3b8">
                    © 2024 Security BartX Ultimate Shield v2.0
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
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10}
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
                "backup": {"enabled": True, "interval_minutes": 30, "max_backups": 10}
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

@app.route("/view_logs")
def view_logs():
    try:
        backups_dir = "backups"
        if not os.path.exists(backups_dir):
            return "<h1>⚠️ لا توجد نسخ احتياطية</h1>"
        
        backups = sorted(os.listdir(backups_dir), reverse=True)
        html = """
        <html dir="rtl">
        <head><meta charset="UTF-8"><style>
        body { background:#0f172a;color:white;padding:20px;font-family:Tahoma }
        h1 { color:#22c55e }
        .backup-item { background:#1e293b;padding:15px;margin:10px 0;border-radius:5px }
        .btn { background:#22c55e;color:white;padding:8px 15px;border:none;border-radius:3px;margin:5px }
        </style></head>
        <body>
            <h1>📜 النسخ الاحتياطية</h1>
            <a href='/dashboard'><button class="btn">↩️ رجوع</button></a>
            <hr>
        """
        
        for backup in backups[:20]:  # Show last 20 backups
            file_path = os.path.join(backups_dir, backup)
            size = os.path.getsize(file_path) / 1024  # Convert to KB
            html += f"""
            <div class="backup-item">
                <strong>{backup}</strong><br>
                <small>الحجم: {size:.2f} كيلوبايت</small>
            </div>
            """
        
        html += "</body></html>"
        return html
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
            }
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

# ================== 4️⃣ GLOBAL STATE ==================
rate_cache = {}
nuke_tracker = {}
NUKE_LIMIT = 3
NUKE_WINDOW = 8

# Voice connections tracker
voice_connections = {}

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

# ================== 8️⃣ AUDIT LOG SAFE ==================
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

# ================== 9️⃣ NUKE KILLER ==================
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

# ================== 🔟 NUKE EVENTS ==================
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

# ================== 1️⃣1️⃣ RATE LIMIT ==================
def rate_limited(uid, key, limit, window):
    now = datetime.datetime.utcnow().timestamp()
    cache_key = f"{uid}_{key}"
    
    if cache_key not in rate_cache:
        rate_cache[cache_key] = []
    
    rate_cache[cache_key].append(now)
    
    # Clean old entries
    rate_cache[cache_key] = [t for t in rate_cache[cache_key] if now - t < window]
    
    return len(rate_cache[cache_key]) > limit

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Then check rate limiting
    if SECURITY_ENABLED and not is_whitelisted(message.author):
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

# ================== 1️⃣2️⃣ BACKUP / RESTORE ==================
def create_backup(reason="auto"):
    if not BACKUP_ENABLED:
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"backup_{timestamp}_{reason}.json"
    path = os.path.join(BACKUP_DIR, name)
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(load_config(), f, indent=4)
        
        # Clean old backups
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

async def backup_guild(guild, reason="auto"):
    try:
        data = {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "timestamp": datetime.datetime.now().isoformat(),
            "reason": reason,
            "roles": [],
            "channels": []
        }
        
        # Backup roles
        for role in guild.roles:
            if role.is_default():
                continue
            data["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "position": role.position
            })
        
        # Backup channels
        for channel in guild.channels:
            overwrites = {}
            for target, perms in channel.overwrites.items():
                overwrites[str(target.id)] = perms.pair()
            
            data["channels"].append({
                "name": channel.name,
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None,
                "position": channel.position,
                "overwrites": overwrites
            })
        
        # Save backup
        path = f"{BACKUP_DIR}/guild_{guild.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        print(f"✅ تم نسخ سيرفر {guild.name}")
    except Exception as e:
        print(f"❌ فشل نسخ سيرفر {guild.name}: {e}")

async def restore_roles(guild):
    try:
        # Find latest backup for this guild
        backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith(f"guild_{guild.id}_")]
        if not backups:
            return False
        
        latest = sorted(backups)[-1]
        path = os.path.join(BACKUP_DIR, latest)
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Restore roles
        for role_data in sorted(data["roles"], key=lambda r: r["position"]):
            if discord.utils.get(guild.roles, name=role_data["name"]):
                continue
            
            try:
                await guild.create_role(
                    name=role_data["name"],
                    permissions=discord.Permissions(role_data["permissions"]),
                    color=discord.Color(role_data["color"]),
                    hoist=role_data["hoist"],
                    mentionable=role_data["mentionable"],
                    reason="استعادة الرتب من النسخة الاحتياطية"
                )
            except:
                continue
        
        return True
    except Exception as e:
        print(f"❌ فشل استعادة الرتب: {e}")
        return False

def restore_settings_only():
    try:
        backups = [f for f in os.listdir(BACKUP_DIR) if "before_change" in f]
        if not backups:
            return False
        
        latest = sorted(backups)[-1]
        path = os.path.join(BACKUP_DIR, latest)
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        # Reload config
        global config, SECURITY_ENABLED, ANTI_NUKE_ENABLED, WHITELIST_USERS, WHITELIST_ROLES
        global RATE_LIMITS, BACKUP_ENABLED, BACKUP_INTERVAL, MAX_BACKUPS
        
        config = load_config()
        SECURITY_ENABLED = config["security_enabled"]
        ANTI_NUKE_ENABLED = config["anti_nuke"]
        WHITELIST_USERS = set(config["whitelist_users"])
        WHITELIST_ROLES = set(config["whitelist_roles"])
        RATE_LIMITS = config["rate_limits"]
        BACKUP_ENABLED = config["backup"]["enabled"]
        BACKUP_INTERVAL = config["backup"]["interval_minutes"]
        MAX_BACKUPS = config["backup"]["max_backups"]
        
        return True
    except Exception as e:
        print(f"❌ فشل استعادة الإعدادات: {e}")
        return False

# ================== 1️⃣3️⃣ ADMIN PANEL (AR) ==================
@bot.group()
@commands.has_permissions(administrator=True)
async def الحماية(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="🛡️ قائمة أوامر الحماية",
            description="أوامر إدارة نظام الحماية المتكامل",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="⚙️ الإعدادات",
            value="• `!الحماية تشغيل` - تشغيل الحماية\n• `!الحماية إيقاف` - إيقاف الحماية\n• `!الحماية الحالة` - عرض حالة النظام",
            inline=False
        )
        embed.add_field(
            name="👥 الوايت ليست",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`",
            inline=False
        )
        embed.add_field(
            name="💾 النسخ الاحتياطية",
            value="• `!الحماية نسخ_احتياطي`\n• `!الحماية استرجاع_الرتب`\n• `!الحماية استرجاع_الإعدادات`",
            inline=False
        )
        embed.add_field(
            name="🎤 أوامر الصوت",
            value="• `!دخول` - الدخول للروم الصوتي\n• `!خروج` - الخروج من الروم الصوتي",
            inline=False
        )
        embed.add_field(
            name="🗑️ إدارة المحادثات",
            value="• `!مسح [عدد]` - مسح الرسائل\n• `!اغلاق_الشات` - إغلاق الشات\n• `!فتح_الشات` - فتح الشات",
            inline=False
        )
        embed.add_field(
            name="🌐 لوحة التحكم",
            value="يمكنك الوصول للوحة التحكم عبر الرابط:\n`/dashboard`",
            inline=False
        )
        embed.set_footer(text="Security BartX Ultimate Shield v3.0")
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
    embed = discord.Embed(
        title="📊 حالة نظام الحماية",
        color=discord.Color.blue()
    )
    embed.add_field(name="🛡️ الحماية", value="✅ مفعل" if SECURITY_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="💣 Anti-Nuke", value="✅ مفعل" if ANTI_NUKE_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="👥 أعضاء الوايت ليست", value=str(len(WHITELIST_USERS)), inline=True)
    embed.add_field(name="🎖️ رتب الوايت ليست", value=str(len(WHITELIST_ROLES)), inline=True)
    embed.add_field(name="💾 النسخ الاحتياطية", value="✅ مفعل" if BACKUP_ENABLED else "❌ معطل", inline=True)
    embed.add_field(name="⏰ معدل النسخ", value=f"كل {BACKUP_INTERVAL} دقيقة", inline=True)
    embed.set_footer(text=f"عدد النسخ المحفوظة: {len(os.listdir(BACKUP_DIR))}")
    await ctx.send(embed=embed)

@الحماية.group()
async def وايت_ليست(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="👥 إدارة الوايت ليست",
            description="أوامر إدارة القائمة البيضاء",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="الأوامر",
            value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`",
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

@الحماية.command()
async def نسخ_احتياطي(ctx):
    create_backup("manual")
    embed = discord.Embed(
        title="💾 تم إنشاء نسخة احتياطية",
        description="تم حفظ إعدادات النظام الحالية",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def استرجاع_الرتب(ctx):
    ok = await restore_roles(ctx.guild)
    embed = discord.Embed(
        title="♻️ استرجاع الرتب" if ok else "❌ فشل الاسترجاع",
        description="تم استرجاع الرتب من النسخة الاحتياطية" if ok else "لا توجد نسخة احتياطية متاحة",
        color=discord.Color.green() if ok else discord.Color.red()
    )
    await ctx.send(embed=embed)

@الحماية.command()
async def استرجاع_الإعدادات(ctx):
    ok = restore_settings_only()
    embed = discord.Embed(
        title="♻️ استرجاع الإعدادات" if ok else "❌ فشل الاسترجاع",
        description="تم استرجاع إعدادات النظام" if ok else "لا توجد نسخة احتياطية للإعدادات",
        color=discord.Color.green() if ok else discord.Color.red()
    )
    await ctx.send(embed=embed)

# ================== 1️⃣4️⃣ VOICE COMMANDS ==================
@bot.command(name="دخول", aliases=["join", "connect"])
@commands.has_permissions(manage_channels=True)
async def join_voice(ctx):
    """الدخول إلى الروم الصوتي الحالي"""
    try:
        # Check if user is in a voice channel
        if ctx.author.voice is None:
            embed = discord.Embed(
                title="❌ خطأ",
                description="يجب أن تكون في روم صوتي أولاً",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        voice_channel = ctx.author.voice.channel
        
        # Check if bot is already connected
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
                # Move to new channel
                await ctx.guild.voice_client.move_to(voice_channel)
                embed = discord.Embed(
                    title="✅ تم النقل",
                    description=f"تم الانتقال إلى روم {voice_channel.mention}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                return
        
        # Connect to voice channel
        voice_client = await voice_channel.connect()
        voice_connections[ctx.guild.id] = voice_client
        
        embed = discord.Embed(
            title="✅ تم الدخول",
            description=f"تم الدخول إلى روم {voice_channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
    except discord.ClientException as e:
        embed = discord.Embed(
            title="❌ خطأ في الاتصال",
            description=f"لا يمكن الاتصال: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ غير متوقع",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name="خروج", aliases=["leave", "disconnect"])
@commands.has_permissions(manage_channels=True)
async def leave_voice(ctx):
    """الخروج من الروم الصوتي"""
    try:
        # Check if bot is connected
        if ctx.guild.voice_client is None:
            embed = discord.Embed(
                title="❌ خطأ",
                description="أنا لست متصلاً بأي روم صوتي",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Disconnect from voice
        await ctx.guild.voice_client.disconnect()
        
        # Remove from connections tracker
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

# ================== 1️⃣5️⃣ CHAT MANAGEMENT COMMANDS ==================
@bot.command(name="مسح", aliases=["حذف", "clear", "purge"])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 10):
    """مسح عدد محدد من الرسائل"""
    try:
        # Limit amount to prevent abuse
        if amount < 1:
            amount = 1
        if amount > 100:
            amount = 100
        
        # Delete messages
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 for the command message
        
        # Send confirmation (will be deleted after 3 seconds)
        embed = discord.Embed(
            title="🗑️ تم المسح",
            description=f"تم حذف {len(deleted) - 1} رسالة",
            color=discord.Color.green()
        )
        msg = await ctx.send(embed=embed)
        
        # Delete confirmation after 3 seconds
        await asyncio.sleep(3)
        await msg.delete()
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحية مرفوضة",
            description="لا أملك صلاحية حذف الرسائل",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except discord.HTTPException as e:
        embed = discord.Embed(
            title="❌ خطأ في الحذف",
            description=f"حدث خطأ: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ خطأ غير متوقع",
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
        
        # Get @everyone role
        everyone_role = ctx.guild.default_role
        
        # Check current permissions
        current_perms = channel.overwrites_for(everyone_role)
        
        # Update permissions to deny send_messages
        await channel.set_permissions(everyone_role, send_messages=False)
        
        embed = discord.Embed(
            title="🔒 تم إغلاق الشات",
            description=f"تم إغلاق {channel.mention} بنجاح",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        # Log action
        log_embed = discord.Embed(
            title="📝 تم إغلاق قناة",
            description=f"تم إغلاق القناة بواسطة {ctx.author.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        log_embed.add_field(name="القناة", value=channel.mention)
        log_embed.add_field(name="المشرف", value=ctx.author.mention)
        await send_to_logs(ctx.guild, log_embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحية مرفوضة",
            description="لا أملك صلاحية إدارة القناة",
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
async def unlock_chat(ctx):
    """فتح الشات والسماح بالكتابة"""
    try:
        channel = ctx.channel
        
        # Get @everyone role
        everyone_role = ctx.guild.default_role
        
        # Check current permissions
        current_perms = channel.overwrites_for(everyone_role)
        
        # Update permissions to allow send_messages
        await channel.set_permissions(everyone_role, send_messages=True)
        
        embed = discord.Embed(
            title="🔓 تم فتح الشات",
            description=f"تم فتح {channel.mention} بنجاح",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        
        # Log action
        log_embed = discord.Embed(
            title="📝 تم فتح قناة",
            description=f"تم فتح القناة بواسطة {ctx.author.mention}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        log_embed.add_field(name="القناة", value=channel.mention)
        log_embed.add_field(name="المشرف", value=ctx.author.mention)
        await send_to_logs(ctx.guild, log_embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="❌ صلاحية مرفوضة",
            description="لا أملك صلاحية إدارة القناة",
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

# ================== 1️⃣6️⃣ HELPER COMMANDS ==================
@bot.command(name="مساعدة", aliases=["help", "اوامر"])
async def help_command(ctx):
    """عرض جميع الأوامر المتاحة"""
    embed = discord.Embed(
        title="🛡️ Security BartX - جميع الأوامر",
        description="نظام حماية متكامل للسيرفرات",
        color=discord.Color.blue()
    )
    
    # Security Commands
    embed.add_field(
        name="🔒 أوامر الحماية",
        value="• `!الحماية` - قائمة أوامر الحماية\n• `!الحماية تشغيل` - تشغيل النظام\n• `!الحماية إيقاف` - إيقاف النظام\n• `!الحماية الحالة` - عرض الحالة",
        inline=False
    )
    
    # Whitelist Commands
    embed.add_field(
        name="👥 أوامر الوايت ليست",
        value="• `!الحماية وايت_ليست إضافة_عضو @user`\n• `!الحماية وايت_ليست إضافة_رتبة @role`",
        inline=False
    )
    
    # Backup Commands
    embed.add_field(
        name="💾 أوامر النسخ الاحتياطي",
        value="• `!الحماية نسخ_احتياطي`\n• `!الحماية استرجاع_الرتب`\n• `!الحماية استرجاع_الإعدادات`",
        inline=False
    )
    
    # Voice Commands
    embed.add_field(
        name="🎤 أوامر الصوت",
        value="• `!دخول` - الدخول للروم الصوتي\n• `!خروج` - الخروج من الروم الصوتي",
        inline=False
    )
    
    # Chat Management Commands
    embed.add_field(
        name="🗑️ أوامر إدارة المحادثات",
        value="• `!مسح [عدد]` - مسح الرسائل (1-100)\n• `!اغلاق_الشات` - إغلاق الشات\n• `!فتح_الشات` - فتح الشات",
        inline=False
    )
    
    embed.set_footer(text="Security BartX Ultimate Shield v3.0 | جميع الحقوق محفوظة")
    await ctx.send(embed=embed)

# ================== 1️⃣7️⃣ ERROR HANDLING ==================
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
        pass  # Ignore unknown commands
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
        embed = discord.Embed(
            title="❌ خطأ غير متوقع",
            description="حدث خطأ أثناء تنفيذ الأمر",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# ================== 1️⃣8️⃣ RUN ==================
if __name__ == "__main__":
    try:
        # Start web server
        keep_alive()
        print("🌐 خادم الويب يعمل...")
        
        # Get bot token
        token = os.environ.get("TOKEN")
        if not token:
            print("❌ خطأ: لم يتم العثور على التوكن!")
            print("يرجى تعيين متغير البيئة TOKEN")
            exit(1)
        
        # Run bot
        print("🤖 جاري تشغيل البوت...")
        bot.run(token)
        
    except discord.LoginFailure:
        print("❌ خطأ: التوكن غير صالح!")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        traceback.print_exc()
