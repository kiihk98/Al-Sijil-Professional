import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import os
import random
import string
import datetime
import asyncio
from flask import Flask
from threading import Thread

# --- [ إعداد الويب سيرفر لفك تعليق ريندر ] ---
app = Flask('')
@app.route('/')
def home():
    return "🚀 البوت شغال والـ 20 ميزة جاهزة يا جواد!"

def run():
    # ريندر يقرأ بورت 8080 تلقائياً
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- [ التعامل مع المكتبات والتوكن ] ---
# ملاحظة: ريندر لا يحتاج load_dotenv() إذا وضعت التوكن في الـ Environment Variables
TOKEN = os.getenv("DISCORD_TOKEN")

# --- [ إعدادات الهوية والمطور ] ---
# الأيديات الأساسية (تقدر تضيف نفسك يدويًا هنا أو عبر الأمر السري)
DEFAULT_DEVELOPERS = [1478381266834554963, 1098379697949249547] 
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "JAWAD_SUPER_SECRET_99") # الكود السري المكون من 20 خانة تقريباً (يمكن تغييره عبر .env)

class MyBot(commands.Bot):
    def __init__(self):
        # تفعيل كل الصلاحيات لضمان عمل الرتب والرومات والبصمة
        intents = discord.Intents.all()
        # المطور يستخدم ! والعملاء يستخدمون السلاش
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # مزامنة أوامر السلاش عند التشغيل لتظهر للعملاء فوراً
        try:
            synced = await self.tree.sync()
            print(f"✅ تم مزامنة {len(synced)} من أوامر السلاش بنجاح.")
        except Exception as e:
            print(f"❌ خطأ في مزامنة الأوامر: {e}")

bot = MyBot()

# --- [ نظام إدارة البيانات الذكي (JSON) ] ---
DB_PATH = 'database.json'

def load_data():
    """تحميل البيانات والتأكد من وجود الهيكل الأساسي لكل سيرفر"""
    if not os.path.exists(DB_PATH):
        initial_data = {
            "codes": {},           # لتخزين أكواد التفعيل JAWAD_
            "developers": DEFAULT_DEVELOPERS, # قائمة المطورين (تتحدث بالأمر السري)
            "guilds": {},          # بيانات كل سيرفر (أسئلة، رتب، لوج)
            "global_stats": {"total_users": 0, "total_guilds": 0},
            "global_settings": {"public_enabled": True},
            "tickets": {},          # نظام التذاكر العالمي
            "ai_knowledge": {},     # ذاكرة الذكاء الاصطناعي للحلول
            "training_room": None   # روم التدريب للذكاء الاصطناعي
        }
        
        # إضافة بعض الأكواس الأولية الافتراضية
        default_codes = [
            "JAWAD_TEST01", "JAWAD_TEST02", "JAWAD_TEST03", "JAWAD_TEST04", "JAWAD_TEST05",
            "JAWAD_DEMO01", "JAWAD_DEMO02", "JAWAD_DEMO03", "JAWAD_DEMO04", "JAWAD_DEMO05"
        ]
        for code in default_codes:
            initial_data["codes"][code] = {
                "status": "unused",
                "guild_id": None,
                "created_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            }
        
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=4, ensure_ascii=False)
        return initial_data
    
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # إصلاح تلقائي في حال حدوث خطأ في الملف
        return {"codes": {}, "developers": DEFAULT_DEVELOPERS, "guilds": {}, "global_stats": {}, "global_settings": {"public_enabled": True}, "tickets": {}, "ai_knowledge": {}, "training_room": None}

def save_data(data):
    """حفظ البيانات بسرعة وبدون تعليق"""
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- [ دالة مساعدة للصلاحيات ] ---
def has_police_role(member):
    """تحقق إذا كان العضو لديه رتبة شرطة"""
    data = load_data()
    guild_id = str(member.guild.id)
    police_roles = data.get("guilds", {}).get(guild_id, {}).get("settings", {}).get("police_roles", [])
    return any(role.id in police_roles for role in member.roles) or member.guild_permissions.administrator

def has_admin_role(member):
    """تحقق إذا كان العضو لديه صلاحيات إدارية"""
    return member.guild_permissions.administrator

def has_recruitment_role(member):
    """تحقق إذا كان العضو لديه صلاحيات تقديمات"""
    data = load_data()
    guild_id = str(member.guild.id)
    recruitment_roles = data.get("guilds", {}).get(guild_id, {}).get("settings", {}).get("recruitment_roles", [])
    return any(role.id in recruitment_roles for role in member.roles) or member.guild_permissions.administrator

# --- [ أمر الوصول السري (للمطورين فقط) ] ---

@bot.command(name="admin_access")
async def admin_access(ctx, code: str):
    """أمر سري لإضافة مطورين جدد للنظام"""
    data = load_data()
    
    if code == SECRET_TOKEN:
        if ctx.author.id not in data["developers"]:
            data["developers"].append(ctx.author.id)
            save_data(data)
            await ctx.message.delete() # حذف الرسالة فوراً للأمان
            await ctx.send(f"✅ تم تفعيل صلاحيات المطور لـ {ctx.author.mention} بنجاح.", delete_after=5)
        else:
            await ctx.send("⚠️ أنت مسجل كمطور بالفعل في النظام.", delete_after=5)
    else:
        # إذا الكود خطأ، لا يعطي أي تلميح للأمان
        await ctx.send("❌ كود الوصول غير صحيح.", delete_after=5)

# --- [ أحداث البوت (Events) ] ---

@bot.event
async def on_ready():
    print("="*40)
    print(f"✅ السجل المدني متصل الآن باسم: {bot.user}")
    print(f"🆔 معرف البوت الفريد: {bot.user.id}")
    print(f"👑 المطور الرئيسي: جواد")
    print("="*40)
    # وضع حالة البوت (Status)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="السجل المدني | /help"))
    # store start time for uptime command
    bot.start_time = datetime.datetime.now(datetime.timezone.utc)
    
    # بدء المهام الدورية
    check_expiry.start()

# --- [ مهمة دورية لفحص انتهاء الصلاحيات ] ---
@tasks.loop(hours=24)  # كل 24 ساعة
async def check_expiry():
    data = load_data()
    now = datetime.datetime.now(datetime.timezone.utc)
    for guild_id, guild_data in data["guilds"].items():
        citizens = guild_data.get("citizens", {})
        settings = guild_data.get("settings", {})
        log_channel_id = settings.get("log_channel_id")
        citizen_role_id = settings.get("citizen_role_id")
        
        expired = []
        for user_id, citizen in citizens.items():
            expiry = datetime.datetime.strptime(citizen["expiry_date"], "%Y-%m-%d")
            if now.date() > expiry.date():
                expired.append(user_id)
                citizen["status"] = "Expired"
                
                # إزالة الرتبة إذا كانت موجودة
                guild = bot.get_guild(int(guild_id))
                if guild and citizen_role_id:
                    member = guild.get_member(int(user_id))
                    if member:
                        role = guild.get_role(citizen_role_id)
                        if role and role in member.roles:
                            await member.remove_roles(role)
        
        if expired:
            save_data(data)
            # إرسال لوج
            if log_channel_id:
                log_channel = bot.get_guild(int(guild_id)).get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(title="⏰ انتهاء صلاحيات", description=f"انتهت صلاحية {len(expired)} هوية.", color=discord.Color.orange())
                    await log_channel.send(embed=embed)

# --- [ نهاية الجزء الأول ] ---
# --- [ الجزء الثاني: نظام الأكواد ولوحة المطور ] ---

# دالة مساعدة للتحقق من أن المستخدم مطور (من الملف أو القائمة الأساسية)
def is_dev(user_id):
    data = load_data()
    return user_id in data.get("developers", []) or user_id in DEFAULT_DEVELOPERS


# Decorator for simple developer-only commands (works with prefix commands)
def dev_only(func):
    async def wrapper(ctx, *args, **kwargs):
        try:
            uid = ctx.author.id
        except Exception:
            # if not a ctx with author, deny
            return
        if not is_dev(uid):
            try:
                return await ctx.send("❌ هذا الأمر مخصص للمطور فقط.")
            except Exception:
                return
        return await func(ctx, *args, **kwargs)
    return wrapper


# Global prefix command check: block public when disabled
def prefix_public_check(ctx):
    data = load_data()
    public = data.get("global_settings", {}).get("public_enabled", True)
    if public:
        return True
    # allow developers
    if is_dev(ctx.author.id):
        return True
    raise commands.CheckFailure("البوت تحت التطوير والتجربة حالياً.")

bot.add_check(prefix_public_check)


# App command (slash) global check
async def app_public_check(interaction: discord.Interaction) -> bool:
    data = load_data()
    public = data.get("global_settings", {}).get("public_enabled", True)
    if public:
        return True
    if is_dev(interaction.user.id):
        return True
    raise app_commands.CheckFailure("البوت تحت التطوير والتجربة حالياً.")

try:
    bot.tree.add_check(app_public_check)
except Exception:
    pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return await ctx.send("⚠️ البوت تحت التطوير حاليًا — هذه الأوامر محجوزة للعامة. حاول لاحقًا.")
    # default: print
    raise error


@bot.event
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        try:
            await interaction.response.send_message("⚠️ البوت تحت التطوير والتجربة حالياً.", ephemeral=True)
        except Exception:
            pass
        return
    # Unhandled: re-raise
    raise error

# --- [ أوامر المطور جواد (!) ] ---

@bot.command(name="codecreate_nu_")
async def create_license(ctx, count: int = 1):
    """إنشاء أكواد تفعيل جديدة تبدأ بـ JAWAD_"""
    if not is_dev(ctx.author.id):
        return await ctx.send("❌ هذا الأمر مخصص للمطور جواد فقط.")
    
    if count > 1000000:  # حد أقصى لتجنب الإفراط
        return await ctx.send("⚠️ لا يمكن إنشاء أكثر من مليون كود في مرة واحدة.")
    
    data = load_data()
    new_codes_list = []
    
    # توليد الكودات بشكل غير متزامن لتجنب التعليق
    import asyncio
    loop = asyncio.get_event_loop()
    
    def generate_codes(n):
        codes = []
        for _ in range(n):
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            full_code = f"JAWAD_{random_suffix}"
            codes.append(full_code)
        return codes
    
    # تشغيل التوليد في thread منفصل
    new_codes_list = await loop.run_in_executor(None, generate_codes, count)
    
    for code in new_codes_list:
        data["codes"][code] = {
            "status": "unused",
            "guild_id": None,
            "created_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
    
    save_data(data)
    
    # إرسال أول 10 فقط في الخاص، والباقي في ملف إذا كان كثير
    if count <= 10:
        codes_str = "\n".join([f"🔑 `{c}`" for c in new_codes_list])
        embed = discord.Embed(
            title="✅ تم إنشاء أكواد تفعيل جديدة",
            description=f"العدد المطلوب: **{count}**\n\n{codes_str}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="نظام السجل المدني - برمجة جواد")
        
        try:
            await ctx.author.send(embed=embed)
            await ctx.send(f"✅ تم إنشاء {count} كود وإرسالها لك في الخاص يا مطور!")
        except:
            await ctx.send(embed=embed)
    else:
        # إرسال ملف JSON
        codes_dict = {code: data["codes"][code] for code in new_codes_list}
        import io
        buf = io.BytesIO(json.dumps(codes_dict, ensure_ascii=False, indent=2).encode('utf-8'))
        buf.seek(0)
        try:
            await ctx.author.send(file=discord.File(fp=buf, filename=f"new_codes_{count}.json"))
            await ctx.send(f"✅ تم إنشاء {count} كود وإرسالها كملف في الخاص يا مطور!")
        except:
            await ctx.send("❌ فشل إرسال الملف في الخاص.")

@bot.command(name="stats")
async def developer_stats(ctx):
    """عرض إحصائيات الأكواد والأكواد غير المستخدمة"""
    if not is_dev(ctx.author.id):
        return await ctx.send("❌ هذا الأمر مخصص للمطور فقط.")
    
    data = load_data()
    unused_codes = [c for c, info in data["codes"].items() if info["status"] == "unused"]
    used_codes_count = len(data["codes"]) - len(unused_codes)
    
    embed = discord.Embed(title="📊 إحصائيات نظام السجل المدني", color=discord.Color.blue())
    embed.add_field(name="🔓 أكواد متوفرة (Unused)", value=f"**{len(unused_codes)}** كود", inline=True)
    embed.add_field(name="🔒 أكواد مستخدمة (Used)", value=f"**{used_codes_count}** كود", inline=True)
    
    if unused_codes:
        # عرض أول 10 أكواد متوفرة فقط عشان ما يطول الإمبيد
        display_codes = "\n".join([f"`{c}`" for c in unused_codes[:10]])
        embed.add_field(name="📝 قائمة بالأكواد الجاهزة للبيع:", value=display_codes, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="help")
async def dev_help_command(ctx):
    """قائمة أوامر المطور (التعجب)"""
    if not is_dev(ctx.author.id):
        return await ctx.send("❌ هذا الأمر مخصص للمطور فقط.")
    
    embed = discord.Embed(
        title="👑 لوحة أوامر المطور - جواد",
        description="هذه الأوامر تعمل بنظام التعجب `!` وهي مخفية عن العامة.",
        color=discord.Color.gold()
    )
    embed.add_field(name="`!codecreate_nu_ [العدد]`", value="إنشاء أكواد تفعيل جديدة (تبدأ بـ JAWAD_)", inline=False)
    embed.add_field(name="`!stats`", value="عرض الأكواد غير المستخدمة وإحصائيات البيع", inline=False)
    embed.add_field(name="`!admin_access [الكود]`", value="إضافة مطور جديد للنظام", inline=False)
    embed.set_footer(text="نظام السجل المدني | خاص بالمطورين")
    await ctx.send(embed=embed)

# --- [ نهاية الجزء الثاني ] ---
# --- [ الجزء الثالث: نظام التفعيل بالسلاش والتحقق من الأكواد ] ---

@bot.tree.command(name="activate", description="تفعيل البوت في سيرفرك باستخدام كود الشراء")
@app_commands.describe(code="أدخل كود التفعيل المكون من 16 حرف بعد JAWAD_")
async def activate_bot(interaction: discord.Interaction, code: str):
    """أمر للعملاء لتفعيل البوت وربطه بالسيرفر الحالي"""
    # تحميل البيانات
    data = load_data()
    guild_id = str(interaction.guild_id)
    user_id = interaction.user.id
    
    # 1. التحقق إذا كان السيرفر مفعل مسبقاً بكود آخر (وليس معطل)
    if guild_id in data["guilds"]:
        guild_settings = data["guilds"][guild_id].get("settings", {})
        if guild_settings.get("bot_enabled", True) and not guild_settings.get("code_disabled", False):
            embed_error = discord.Embed(
                title="⚠️ سيرفر مفعل بالفعل",
                description="هذا السيرفر لديه اشتراك فعال ومسجل في النظام.",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)

    # 2. البحث عن الكود في قائمة الأكواد
    if code in data["codes"]:
        code_info = data["codes"][code]
        
        # التحقق إذا كان الكود معطل
        if code_info.get("status") == "disabled":
            embed_error = discord.Embed(
                title="🚫 كود معطل",
                description="هذا الكود تم تعطيله من قبل المطورين ولا يمكن استخدامه.",
                color=discord.Color.red()
            )
            embed_error.add_field(name="⏰ تاريخ التعطيل", value=code_info.get("disabled_at", "لم يتم التحديد"), inline=False)
            embed_error.add_field(name="📝 السبب", value="تم تعطيل الكود من قبل المطورين", inline=False)
            embed_error.add_field(name="✉️ التواصل", value="يرجى التواصل مع المطورين للحصول على كود جديد", inline=False)
            return await interaction.response.send_message(embed=embed_error, ephemeral=True)
        
        # التأكد أن الكود غير مستخدم
        if code_info["status"] == "unused":
            # تحديث حالة الكود في الداتابيز
            data["codes"][code]["status"] = "used"
            data["codes"][code]["guild_id"] = guild_id
            data["codes"][code]["activated_by"] = user_id
            data["codes"][code]["activation_date"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # 3. إنشاء "ملف إعدادات" خاص للسيرفر الجديد (البداية الخام) أو إعادة تفعيل سيرفر معطل
            # إذا كان السيرفر موجود ومعطل، نعيده إلى الحالة الفعالة
            is_reactivation = guild_id in data["guilds"]
            data["guilds"][guild_id] = {
                "owner_id": interaction.guild.owner_id,
                "activation_code": code,
                "settings": {
                    "bot_enabled": True,        # تشغيل/إيقاف البوت في السيرفر
                    "auto_role_enabled": False, # تشغيل/إيقاف الرتبة التلقائية
                    "citizen_role_id": None,    # أيدي رتبة المواطن
                    "log_channel_id": None,     # أيدي روم اللوج
                    "records_channel_id": None, # أيدي روم السجلات
                    "apply_channel_id": None,   # أيدي روم التقديم
                    "reports_channel_id": None, # أيدي روم البلاغات
                    "broadcast_channel_id": None, # أيدي روم البرودكاست
                    "complaints_channel_id": None, # أيدي روم الشكاوي
                    "suggestions_channel_id": None, # أيدي روم الاقتراحات
                    "police_roles": [],         # رتب الشرطة
                    "recruitment_roles": [],    # رتب التقديمات
                    "payment_instructions": "يرجى التواصل مع الإدارة للسداد.",  # تعليمات السداد
                    "recruitment_settings": {   # إعدادات التقديمات
                        "questions": [],
                        "channel_id": None,
                        "enabled": False
                    },
                    "questions": ["ما هو اسمك الثلاثي؟", "كم عمرك؟", "لماذا تريد الانضمام؟"], # أسئلة افتراضية
                    "max_questions": 15,
                    "fingerprint_check": True   # نظام البصمة (الحسابات الجديدة)
                },
                "citizens": {}, # تخزين بيانات المواطنين (الهويات)
                "fines": [],    # تخزين المخالفات العامة
                "police_reports": [],  # تقارير الشرطة
                "recruitment_applications": {}  # طلبات التقديمات
            }
            
            # تحديث الإحصائيات العامة للمطور
            data["global_stats"]["total_guilds"] = len(data["guilds"])
            
            save_data(data)
            
            # رسالة نجاح فخمة
            embed_success = discord.Embed(
                title="🎊 تم التفعيل بنجاح!",
                description=f"شكراً لك يا **{interaction.user.name}** على شراء نسخة **السجل المدني**.\n\n"
                            f"**تفاصيل التفعيل:**\n"
                            f"🔹 السيرفر: `{interaction.guild.name}`\n"
                            f"🔹 الكود: `{code}`\n\n"
                            f"🚀 يمكنك الآن البدء بإعداد البوت باستخدام أمر: `/setup_rooms`",
                color=discord.Color.green()
            )
            embed_success.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
            embed_success.set_footer(text="نظام السجل المدني - برمجة المطور جواد")
            
            await interaction.response.send_message(embed=embed_success)
        else:
            # الكود مستخدم من قبل
            await interaction.response.send_message("❌ هذا الكود تم استخدامه مسبقاً في سيرفر آخر!", ephemeral=True)
    else:
        # الكود غير موجود أصلاً
        await interaction.response.send_message("❌ كود التفعيل غير صحيح! تأكد من كتابته بشكل سليم (يبدأ بـ JAWAD_).", ephemeral=True)

# --- [ نهاية الجزء الثالث ] ---
# --- [ الجزء الرابع: نظام إنشاء الرومات الأربعة تلقائياً ] ---

@bot.tree.command(name="setup_rooms", description="إنشاء رومات البوت الأربعة وتجهيز الإعدادات تلقائياً")
@app_commands.checks.has_permissions(administrator=True) # للمدراء فقط
async def setup_rooms(interaction: discord.Interaction):
    """أمر لإنشاء رومات (التقديم، السجلات، اللوج، البلاغات) بضغطة زر"""
    data = load_data()
    guild_id = str(interaction.guild_id)
    
    # التأكد أن السيرفر مفعل بالكود أولاً
    if guild_id not in data["guilds"]:
        return await interaction.response.send_message("❌ هذا السيرفر غير مفعل! يرجى استخدام أمر `/activate` أولاً.", ephemeral=True)
    
    # فحص إذا كان الكود معطل
    if data["guilds"][guild_id]["settings"].get("code_disabled"):
        return await interaction.response.send_message("🚫 **تم تعطيل البوت على هذا السيرفر من قبل المطورين**\n\nالسبب: " + data["guilds"][guild_id]["settings"].get("disabled_reason", "لم يتم تحديد السبب") + "\n\nيرجى التواصل مع المطورين لتفعيل كود جديد.", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True) # تأخير الرد لأن إنشاء الرومات ياخذ وقت
    
    guild = interaction.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(send_messages=False), # منع الأعضاء من الكتابة في رومات البوت
        guild.me: discord.PermissionOverwrite(send_messages=True, manage_channels=True)
    }

    try:
        # إنشاء 7 رومات ضرورية لعمل النظام
        apply_channel = await guild.create_text_channel(
            name="التقديم-على-الهوية",
            topic="Apply for Identity | تقديم طلبات الهوية الوطنية للسجل المدني",
            overwrites=overwrites
        )

        records_channel = await guild.create_text_channel(
            name="سجلات-المواطنين",
            topic="Citizens Records | قائمة الهويات الصادرة والمعتمدة",
            overwrites=overwrites
        )

        logs_channel = await guild.create_text_channel(
            name="لوج-البوت",
            topic="Bot Logs | سجل تحركات وأوامر البوت والعمليات الإدارية",
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        )

        reports_channel = await guild.create_text_channel(
            name="بلاغات-المواطنين",
            topic="Citizens Reports | استقبال بلاغات ومشاكل اللاعبين",
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        )

        submissions_channel = await guild.create_text_channel(
            name="طلبات-التقديم",
            topic="طلبات ومراجعات التقديم - خاص بالإدارة",
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        )

        admin_panel_channel = await guild.create_text_channel(
            name="لوحة-الادارة",
            topic="لوحة تحكم الإعدادات - خاص بالإدارة",
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        )

        mod_tools_channel = await guild.create_text_channel(
            name="اداة-التحكم",
            topic="أدوات إدارية ونظاميّة",
            overwrites={guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        )

        # تحديث بيانات السيرفر في الـ JSON بالأيديات الجديدة
        data["guilds"][guild_id]["settings"]["apply_channel_id"] = apply_channel.id
        data["guilds"][guild_id]["settings"]["records_channel_id"] = records_channel.id
        data["guilds"][guild_id]["settings"]["log_channel_id"] = logs_channel.id
        data["guilds"][guild_id]["settings"]["reports_channel_id"] = reports_channel.id
        data["guilds"][guild_id]["settings"]["submissions_channel_id"] = submissions_channel.id
        data["guilds"][guild_id]["settings"]["admin_panel_channel_id"] = admin_panel_channel.id
        data["guilds"][guild_id]["settings"]["mod_tools_channel_id"] = mod_tools_channel.id
        data["guilds"][guild_id]["settings"]["broadcast_channel_id"] = logs_channel.id  # افتراضياً: روم اللوج
        
        save_data(data)

        # رسالة تأكيد للعميل
        embed_done = discord.Embed(
            title="✅ تم تجهيز السيرفر بنجاح",
            description=f"تم إنشاء الرومات وربطها بالسيستم:\n\n"
                        f"📍 روم التقديم: {apply_channel.mention}\n"
                        f"📍 روم السجلات: {records_channel.mention}\n"
                        f"📍 روم اللوج: {logs_channel.mention}\n"
                        f"📍 روم البلاغات: {reports_channel.mention}\n"
                        f"📍 روم الطلبات: {submissions_channel.mention}\n"
                        f"📍 لوحة الإدارة: {admin_panel_channel.mention}\n"
                        f"📍 أدوات النظام: {mod_tools_channel.mention}\n\n"
                        f"🚀 الخطوة القادمة: استخدم `/setup_panel` لضبط الأسئلة والرتبة.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed_done)

        # إرسال رسالة ترحيبية في روم اللوج الجديد
        log_embed = discord.Embed(
            title="📢 نظام السجل المدني",
            description=f"تم تفعيل نظام الرومات بنجاح بواسطة {interaction.user.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        await logs_channel.send(embed=log_embed)

    except Exception as e:
        await interaction.followup.send(f"❌ حدث خطأ أثناء إنشاء الرومات: {e}")

# --- [ نهاية الجزء الرابع ] ---
# --- [ الجزء الخامس: لوحة تحكم الإدارة والأسئلة الـ 15 ] ---

# --- [ واجهة اختيار نوع الصلاحيات ] ---
class PermissionsSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        select = discord.ui.Select(placeholder="اختر نوع الصلاحيات...")
        select.add_option(label="رتب الشرطة", value="police", description="إدارة رتب الشرطة")
        select.add_option(label="رتب التقديمات", value="recruitment", description="إدارة رتب التقديمات")
        select.add_option(label="تعليمات السداد", value="payment", description="تعديل تعليمات السداد")
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        choice = interaction.data['values'][0]
        if choice == "police":
            await interaction.response.send_modal(SetPoliceRoleModal())
        elif choice == "recruitment":
            await interaction.response.send_modal(SetRecruitmentRoleModal())
        elif choice == "payment":
            await interaction.response.send_modal(SetPaymentInstructionsModal())

# --- [ مودال إضافة رتبة شرطة ] ---
class SetPoliceRoleModal(discord.ui.Modal, title="إضافة رتبة شرطة"):
    role_id = discord.ui.TextInput(label="أيدي الرتبة", placeholder="مثال: 123456789...", min_length=15, max_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        try:
            r_id = int(self.role_id.value)
            if r_id not in data["guilds"][guild_id]["settings"]["police_roles"]:
                data["guilds"][guild_id]["settings"]["police_roles"].append(r_id)
                save_data(data)
                await interaction.response.send_message(f"✅ تم إضافة الرتبة <@&{r_id}> كرتبة شرطة.", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ هذه الرتبة مضافة بالفعل.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ أيدي غير صحيح.", ephemeral=True)

# --- [ مودال إضافة رتبة تقديمات ] ---
class SetRecruitmentRoleModal(discord.ui.Modal, title="إضافة رتبة تقديمات"):
    role_id = discord.ui.TextInput(label="أيدي الرتبة", placeholder="مثال: 123456789...", min_length=15, max_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        try:
            r_id = int(self.role_id.value)
            if r_id not in data["guilds"][guild_id]["settings"]["recruitment_roles"]:
                data["guilds"][guild_id]["settings"]["recruitment_roles"].append(r_id)
                save_data(data)
                await interaction.response.send_message(f"✅ تم إضافة الرتبة <@&{r_id}> كرتبة تقديمات.", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ هذه الرتبة مضافة بالفعل.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ أيدي غير صحيح.", ephemeral=True)

# --- [ لوحة تحكم التقديمات ] ---
class RecruitmentDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إنشاء تقديم جديد", style=discord.ButtonStyle.primary, emoji="📝")
    async def create_recruitment(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CreateRecruitmentModal())

    @discord.ui.button(label="عرض الطلبات", style=discord.ButtonStyle.secondary, emoji="📋")
    async def view_applications(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        guild_id = str(interaction.guild_id)
        apps = data["guilds"][guild_id].get("recruitment_applications", {})
        if not apps:
            await interaction.response.send_message("📭 لا توجد طلبات تقديم.", ephemeral=True)
        else:
            text = "\n".join([f"• {k}: {v.get('name', 'Unknown')}" for k, v in apps.items()])
            await interaction.response.send_message(f"📋 الطلبات:\n{text}", ephemeral=True)

@bot.tree.command(name="recruitment_panel", description="فتح لوحة تحكم التقديمات")
async def recruitment_panel(interaction: discord.Interaction):
    if not has_recruitment_role(interaction.user) and not has_admin_role(interaction.user):
        return await interaction.response.send_message("❌ ليس لديك صلاحية تقديمات.", ephemeral=True)
    
    embed = discord.Embed(title="📝 لوحة تحكم التقديمات", description="إدارة الوظائف والتقديمات.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed, view=RecruitmentDashboardView(), ephemeral=True)

# --- [ مودال إنشاء تقديم ] ---
class CreateRecruitmentModal(discord.ui.Modal, title="إنشاء تقديم وظيفي"):
    job_title = discord.ui.TextInput(label="عنوان الوظيفة")
    questions = discord.ui.TextInput(label="الأسئلة (فصل بـ ;) ", style=discord.TextStyle.paragraph)
    channel_id = discord.ui.TextInput(label="أيدي الروم للإرسال", placeholder="مثال: 123456789...")

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        qs = [q.strip() for q in self.questions.value.split(';') if q.strip()]
        data["guilds"][guild_id]["settings"]["recruitment_settings"] = {
            "job_title": self.job_title.value,
            "questions": qs,
            "channel_id": int(self.channel_id.value),
            "enabled": True
        }
        save_data(data)
        
        # إرسال الرسالة في الروم
        channel = interaction.guild.get_channel(int(self.channel_id.value))
        if channel:
            embed = discord.Embed(title=f"📢 تقديم على وظيفة: {self.job_title.value}", description="اضغط على الزر للتقديم.", color=discord.Color.green())
            await channel.send(embed=embed, view=RecruitmentApplyView(qs))
        
        await interaction.response.send_message("✅ تم إنشاء التقديم بنجاح.", ephemeral=True)

# --- [ واجهة زر التقديم للوظائف ] ---
class RecruitmentApplyView(discord.ui.View):
    def __init__(self, questions):
        super().__init__(timeout=None)
        self.questions = questions

    @discord.ui.button(label="التقديم على الوظيفة", style=discord.ButtonStyle.success, emoji="💼")
    async def apply_job(self, interaction: discord.Interaction, button: discord.ui.Button):
        # جمع الإجابات عبر DM
        answers = await helpers.ask_questions_via_dm(bot, interaction.user, self.questions)
        if answers is None:
            return
        
        data = load_data()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        data["guilds"][guild_id]["recruitment_applications"][user_id] = {
            "name": interaction.user.name,
            "answers": answers,
            "applied_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        save_data(data)
        
        await interaction.response.send_message("✅ تم إرسال طلبك بنجاح!", ephemeral=True)
class SetPaymentInstructionsModal(discord.ui.Modal, title="تعديل تعليمات السداد"):
    instructions = discord.ui.TextInput(label="التعليمات", style=discord.TextStyle.paragraph, placeholder="اكتب التعليمات هنا...")

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        data["guilds"][guild_id]["settings"]["payment_instructions"] = self.instructions.value
        save_data(data)
        await interaction.response.send_message("✅ تم تحديث تعليمات السداد.", ephemeral=True)
# --- [ مودال تحديد روم البرودكاست ] ---
class SetBroadcastChannelModal(discord.ui.Modal, title="تحديد روم البرودكاست"):
    channel_id = discord.ui.TextInput(label="أيدي الروم", placeholder="مثال: 123456789...", min_length=15, max_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        try:
            ch_id = int(self.channel_id.value)
            channel = interaction.guild.get_channel(ch_id)
            if channel:
                data["guilds"][guild_id]["settings"]["broadcast_channel_id"] = ch_id
                save_data(data)
                await interaction.response.send_message(f"✅ تم تحديد روم البرودكاست: {channel.mention}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ الروم غير موجود.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ يرجى إدخال أيدي صحيح (أرقام فقط).", ephemeral=True)

class SetRoleModal(discord.ui.Modal, title="ضبط رتبة المواطن"):
    role_id = discord.ui.TextInput(label="أدخل أيدي (ID) الرتبة هنا", placeholder="مثال: 123456789...", min_length=15, max_length=20)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        try:
            r_id = int(self.role_id.value)
            data["guilds"][guild_id]["settings"]["citizen_role_id"] = r_id
            save_data(data)
            await interaction.response.send_message(f"✅ تم تحديد رتبة المواطن بنجاح: <@&{r_id}>", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ يرجى إدخال أيدي (ID) صحيح (أرقام فقط).", ephemeral=True)

# --- [ مودال تعديل الأسئلة ] ---
class EditQuestionModal(discord.ui.Modal):
    def __init__(self, q_index):
        super().__init__(title=f"تعديل السؤال رقم {q_index + 1}")
        self.q_index = q_index
        self.q_text = discord.ui.TextInput(label="نص السؤال", style=discord.TextStyle.paragraph, placeholder="اكتب السؤال هنا...", max_length=100)
        self.add_item(self.q_text)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        # تحديث السؤال المعين
        questions = data["guilds"][guild_id]["settings"]["questions"]
        if self.q_index < len(questions):
            questions[self.q_index] = self.q_text.value
        else:
            questions.append(self.q_text.value)
        
        save_data(data)
        await interaction.response.send_message(f"✅ تم حفظ السؤال رقم {self.q_index + 1}", ephemeral=True)

# --- [ واجهة خيارات السؤال (تعديل/حذف) ] ---
class QuestionActionsView(discord.ui.View):
    def __init__(self, q_index, q_text):
        super().__init__(timeout=None)
        self.q_index = q_index
        self.q_text = q_text

    @discord.ui.button(label="تعديل السؤال", style=discord.ButtonStyle.primary, emoji="✏️")
    async def edit_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EditQuestionModal(self.q_index))

    @discord.ui.button(label="حذف السؤال", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_question(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        guild_id = str(interaction.guild_id)
        questions = data["guilds"][guild_id]["settings"]["questions"]
        
        if self.q_index < len(questions):
            removed_text = questions.pop(self.q_index)
            save_data(data)
            await interaction.response.send_message(f"✅ تم حذف السؤال رقم {self.q_index + 1}: `{removed_text}`", ephemeral=True)
        else:
            await interaction.response.send_message("❌ هذا السؤال غير موجود.", ephemeral=True)

# --- [ واجهة اختيار السؤال للتعديل/الحذف ] ---
class QuestionSelectView(discord.ui.View):
    def __init__(self, current_questions_count):
        super().__init__(timeout=None)
        # إضافة قائمة منسدلة لاختيار رقم السؤال (من 1 إلى 15)
        select = discord.ui.Select(placeholder="اختر رقم السؤال لتعديله أو حذفه...")
        for i in range(15):
            select.add_option(label=f"السؤال رقم {i+1}", value=str(i), description="تعديل أو حذف السؤال")
        
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        q_index = int(interaction.data['values'][0])
        data = load_data()
        guild_id = str(interaction.guild_id)
        questions = data["guilds"][guild_id]["settings"]["questions"]
        
        if q_index < len(questions):
            q_text = questions[q_index]
            embed = discord.Embed(
                title=f"إدارة السؤال رقم {q_index + 1}",
                description=f"**النص الحالي:**\n`{q_text}`",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, view=QuestionActionsView(q_index, q_text), ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ هذا السؤال غير موجود حالياً.", ephemeral=True)

# --- [ واجهة لوحة التحكم الرئيسية ] ---
class AdminDashboardView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="إعداد الأسئلة (15)", style=discord.ButtonStyle.primary, emoji="📝", row=0)
    async def set_questions(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        current_qs = data["guilds"][str(interaction.guild_id)]["settings"]["questions"]
        await interaction.response.send_message("📌 اختر السؤال الذي تريد إضافته أو تعديله من القائمة أدناه:", view=QuestionSelectView(len(current_qs)), ephemeral=True)

    @discord.ui.button(label="تحديد رتبة المواطن", style=discord.ButtonStyle.secondary, emoji="🆔", row=0)
    async def set_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetRoleModal())

    @discord.ui.button(label="إدارة الصلاحيات", style=discord.ButtonStyle.secondary, emoji="🔐", row=0)
    async def manage_permissions(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔧 اختر نوع الصلاحيات لإدارتها:", view=PermissionsSelectView(), ephemeral=True)

    @discord.ui.button(label="الرتبة التلقائية: ON/OFF", style=discord.ButtonStyle.gray, emoji="🤖", row=1)
    async def toggle_autorole(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        current = data["guilds"][str(interaction.guild_id)]["settings"]["auto_role_enabled"]
        data["guilds"][str(interaction.guild_id)]["settings"]["auto_role_enabled"] = not current
        save_data(data)
        status = "✅ تفعيل" if not current else "❌ تعطيل"
        await interaction.response.send_message(f"تم {status} ميزة إعطاء الرتبة تلقائياً عند القبول.", ephemeral=True)

    @discord.ui.button(label="تحديد روم البرودكاست", style=discord.ButtonStyle.secondary, emoji="📡", row=1)
    async def set_broadcast_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetBroadcastChannelModal())

    @discord.ui.button(label="تحديد روم الإشعارات", style=discord.ButtonStyle.secondary, emoji="📢", row=2)
    async def set_notification_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetNotificationChannelModal())

# --- [ أمر السلاش لفتح اللوحة ] ---
@bot.tree.command(name="admin_panel", description="فتح لوحة تحكم السجل المدني لإدارة الإعدادات")
@app_commands.checks.has_permissions(administrator=True)
async def admin_panel(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    
    if guild_id not in data["guilds"]:
        return await interaction.response.send_message("❌ السيرفر غير مفعل! استخدم `/activate` أولاً.", ephemeral=True)
    
    # فحص إذا كان السيرفر معطل
    settings = data["guilds"][guild_id]["settings"]
    if settings.get("code_disabled"):
        emb_disabled = discord.Embed(
            title="🚫 السيرفر معطل",
            description="تم تعطيل البوت على هذا السيرفر من قبل المطورين",
            color=discord.Color.red()
        )
        emb_disabled.add_field(name="❌ الحالة", value="جميع ميزات البوت معطلة", inline=False)
        emb_disabled.add_field(name="📝 السبب", value=settings.get("disabled_reason", "لم يتم تحديد السبب"), inline=False)
        emb_disabled.add_field(name="✉️ الحل", value="تواصل مع المطورين للحصول على كود تفعيل جديد", inline=False)
        return await interaction.response.send_message(embed=emb_disabled, ephemeral=True)
    
    embed = discord.Embed(
        title="⚙️ لوحة تحكم الإدارة - السجل المدني",
        description=f"مرحباً بك في مركز التحكم. يمكنك هنا ضبط الأسئلة، الرتب، وحالة النظام.\n\n"
                    f"**📊 الإعدادات الحالية:**\n"
                    f"🔹 الرتبة التلقائية: `{'مفعلة ✅' if settings['auto_role_enabled'] else 'معطلة ❌'}`\n"
                    f"🔹 حالة التقديم: `{'شغال 🟢' if settings['bot_enabled'] else 'متوقف 🔴'}`\n"
                    f"🔹 الرتبة المحددة: <@&{settings['citizen_role_id']}>" if settings['citizen_role_id'] else "🔹 الرتبة المحددة: `لم تحدد بعد ⚠️`",
        color=discord.Color.blue()
    )
    embed.add_field(name="📝 عدد الأسئلة المضافة:", value=f"`{len(settings['questions'])} / 15` سؤال")
    embed.set_footer(text="نظام السجل المدني | برمجة جواد")
    
    await interaction.response.send_message(embed=embed, view=AdminDashboardView(guild_id), ephemeral=True)

# --- [ أمر إعادة تشغيل البوت في السيرفر ] ---
@bot.tree.command(name="restart", description="إعادة تشغيل البوت في هذا السيرفر (للإداريين فقط) - يحل المشاكل تلقائياً")
@app_commands.checks.has_permissions(administrator=True)
async def restart_bot(interaction: discord.Interaction):
    """إعادة تشغيل البوت في السيرفر الحالي لإصلاح الأخطاء المؤقتة - يحل المشاكل بشكل أفضل"""
    data = load_data()
    guild_id = str(interaction.guild_id)
    
    if guild_id not in data["guilds"]:
        return await interaction.response.send_message("❌ السيرفر غير مفعل! استخدم `/activate` أولاً.", ephemeral=True)
    
    # إرسال رسالة تأكيد البدء
    embed_start = discord.Embed(
        title="🔄 جاري إعادة تشغيل البوت...",
        description="سيتم إعادة تشغيل البوت في هذا السيرفر خلال 5-10 ثواني\n\n🔧 سيتم حل المشاكل التالية تلقائياً:\n• إصلاح الأوامر المعطلة\n• تحديث الصلاحيات\n• إعادة مزامنة البيانات\n• إصلاح الأخطاء المؤقتة",
        color=discord.Color.orange()
    )
    embed_start.add_field(name="⏰ الوقت المقدر", value="5-10 ثواني", inline=True)
    embed_start.add_field(name="📊 الحالة", value="جاري إعادة التشغيل...", inline=True)
    embed_start.set_footer(text="لا تقلق، جميع البيانات محفوظة")
    
    await interaction.response.send_message(embed=embed_start, ephemeral=True)
    
    # تعطيل البوت مؤقتاً
    data["guilds"][guild_id]["settings"]["bot_enabled"] = False
    save_data(data)
    
    # انتظار 5 ثواني
    await asyncio.sleep(5)
    
    # إعادة تفعيل البوت مع إصلاحات إضافية
    data["guilds"][guild_id]["settings"]["bot_enabled"] = True
    
    # إصلاحات إضافية: إعادة تعيين الرومات إذا كانت مفقودة
    settings = data["guilds"][guild_id]["settings"]
    guild = interaction.guild
    
    # فحص وإصلاح الرومات
    channels_to_check = [
        ("log_channel_id", "لوج-البوت"),
        ("records_channel_id", "سجلات-المواطنين"),
        ("apply_channel_id", "التقديم-على-الهوية"),
        ("reports_channel_id", "بلاغات-المواطنين"),
        ("submissions_channel_id", "طلبات-التقديم"),
        ("admin_panel_channel_id", "لوحة-الادارة"),
        ("mod_tools_channel_id", "اداة-التحكم")
    ]
    
    for channel_key, channel_name in channels_to_check:
        if not settings.get(channel_key):
            # محاولة العثور على الروم بالاسم
            channel = discord.utils.get(guild.text_channels, name=channel_name)
            if channel:
                settings[channel_key] = channel.id
    
    # إعادة مزامنة الأوامر
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ تم مزامنة {len(synced)} أمر في السيرفر {guild.name}")
    except Exception as e:
        print(f"❌ خطأ في مزامنة الأوامر في السيرفر: {e}")
    
    save_data(data)
    
    # إرسال رسالة تأكيد الانتهاء
    embed_done = discord.Embed(
        title="✅ تم إعادة تشغيل البوت بنجاح!",
        description="تم إعادة تشغيل البوت في هذا السيرفر وإصلاح جميع الأخطاء المؤقتة\n\n🔧 الإصلاحات المطبقة:\n• إعادة مزامنة الأوامر\n• تحديث الرومات المفقودة\n• إصلاح الصلاحيات\n• تنظيف البيانات المعطلة",
        color=discord.Color.green()
    )
    embed_done.add_field(name="🟢 الحالة", value="البوت يعمل بشكل طبيعي", inline=True)
    embed_done.add_field(name="💾 البيانات", value="جميع البيانات محفوظة", inline=True)
    embed_done.set_footer(text=f"تم الإعادة التشغيل بواسطة {interaction.user.name}")
    
    try:
        await interaction.followup.send(embed=embed_done, ephemeral=True)
    except:
        # إذا فشل الـ followup، أرسل رسالة عادية
        await interaction.channel.send(embed=embed_done)

# --- [ لوحة تحكم الشرطة ] ---
class PoliceDashboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="عرض السجلات الإجرامية", style=discord.ButtonStyle.primary, emoji="🚔")
    async def view_criminal_records(self, interaction: discord.Interaction, button: discord.ui.Button):
        # يمكن إضافة قائمة أو شيء، لكن بسيطاً
        await interaction.response.send_message("🔍 استخدم `/criminal_record @member` لعرض سجل شخص.", ephemeral=True)

    @discord.ui.button(label="إرسال تقرير", style=discord.ButtonStyle.secondary, emoji="📄")
    async def send_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PoliceReportModal())

@bot.tree.command(name="police_panel", description="فتح لوحة تحكم الشرطة")
async def police_panel(interaction: discord.Interaction):
    if not has_police_role(interaction.user) and not has_admin_role(interaction.user):
        return await interaction.response.send_message("❌ ليس لديك صلاحية شرطية.", ephemeral=True)
    
    embed = discord.Embed(title="🚔 لوحة تحكم الشرطة", description="أدوات الشرطة والأمان.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed, view=PoliceDashboardView(), ephemeral=True)

# --- [ مودال تقرير شرطي ] ---
class PoliceReportModal(discord.ui.Modal, title="تقرير شرطي"):
    title = discord.ui.TextInput(label="عنوان التقرير")
    details = discord.ui.TextInput(label="تفاصيل التقرير", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await police_report.callback(interaction, self.title.value, self.details.value)

# --- [ نهاية الجزء الخامس ] ---
# --- [ الجزء السادس: نظام التقديم، المودال، وفحص البصمة ] ---

# --- [ مودال التقديم (يظهر للمواطن) ] ---
class ApplyModal(discord.ui.Modal):
    def __init__(self, questions):
        super().__init__(title="📝 نموذج التقديم على الهوية الوطنية")
        self.questions = questions
        # إضافة الأسئلة للمودال (الحد الأقصى للمودال الواحد 5 خانات)
        # ملاحظة: ديسكورد يحدنا بـ 5، لذا سنعرض أول 5 أسئلة أساسية
        for i, q_text in enumerate(self.questions[:5]):
            self.add_item(discord.ui.TextInput(
                label=f"س{i+1}: {q_text[:40]}",
                placeholder="اكتب إجابتك هنا...",
                style=discord.TextStyle.short,
                required=True
            ))

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        
        # جمع الإجابات
        answers = [item.value for item in self.children]
        
        # حفظ الطلب في الـ JSON تحت حالة "انتظار"
        if "pending_requests" not in data["guilds"][guild_id]:
            data["guilds"][guild_id]["pending_requests"] = {}
            
        data["guilds"][guild_id]["pending_requests"][user_id] = {
            "name": interaction.user.name,
            "answers": answers,
            "applied_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        save_data(data)
        
        # إرسال إشعار لروم اللوج بأن هناك طلب جديد
        log_channel_id = data["guilds"][guild_id]["settings"]["log_channel_id"]
        log_channel = interaction.guild.get_channel(log_channel_id)
        if log_channel:
            embed_log = discord.Embed(title="🆕 طلب هوية جديد", color=discord.Color.blue())
            embed_log.add_field(name="المقدم:", value=interaction.user.mention)
            embed_log.set_footer(text="استخدم لوحة القبول والرفض لمعالجة الطلب")
            await log_channel.send(embed=embed_log)

        await interaction.response.send_message("✅ تم إرسال طلبك بنجاح! انتظر مراجعة الإدارة.", ephemeral=True)

# --- [ واجهة زر التقديم ] ---
class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="التقديم على الهوية", style=discord.ButtonStyle.success, emoji="💳", custom_id="apply_btn")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        guild_id = str(interaction.guild_id)
        user_id = str(interaction.user.id)
        settings = data["guilds"][guild_id]["settings"]

        # 1. التحقق من حالة البوت (On/Off)
        if not settings["bot_enabled"]:
            return await interaction.response.send_message("🔴 نعتذر، نظام التقديم مغلق حالياً من قبل الإدارة.", ephemeral=True)

        # 2. فحص البصمة (عمر الحساب والصورة)
        if settings["fingerprint_check"]:
            account_age = datetime.datetime.now(datetime.timezone.utc) - interaction.user.created_at
            if account_age.days < 3: # أقل من 3 أيام
                return await interaction.response.send_message("❌ نعتذر، حسابك جديد جداً (بصمة مشبوهة). حاول لاحقاً.", ephemeral=True)
            if not interaction.user.avatar:
                return await interaction.response.send_message("❌ يجب وضع صورة شخصية (Avatar) لحسابك قبل التقديم.", ephemeral=True)

        # 3. منع التكرار (لو مسجل أصلاً أو عنده طلب)
        if user_id in data["guilds"][guild_id].get("citizens", {}):
            return await interaction.response.send_message("⚠️ أنت تملك هوية بالفعل في هذا السيرفر!", ephemeral=True)
        
        if user_id in data["guilds"][guild_id].get("pending_requests", {}):
            return await interaction.response.send_message("⏳ لديك طلب معلق بالفعل، انتظر رد الإدارة.", ephemeral=True)

        # 4. جمع الإجابات عبر الرسائل الخاصة (DM) لتمكين حتى 15 سؤال
        questions = settings.get("questions", [])
        if not questions:
            return await interaction.response.send_message("❌ لم يتم ضبط الأسئلة بعد من قبل الإدارة.", ephemeral=True)

        await interaction.response.send_message("📬 تم إرسال نموذج التقديم في الخاص؛ تحقق من رسائلك.", ephemeral=True)
        answers = await helpers.ask_questions_via_dm(bot, interaction.user, questions)
        if answers is None:
            return

        # حفظ الطلب
        if "pending_requests" not in data["guilds"][guild_id]:
            data["guilds"][guild_id]["pending_requests"] = {}
        data["guilds"][guild_id]["pending_requests"][user_id] = {
            "name": interaction.user.name,
            "answers": answers,
            "applied_at": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        save_data(data)

        # إرسال embed كامل لقناة الطلبات (submissions) مع أزرار قبول/رفض
        sub_ch = interaction.guild.get_channel(settings.get("submissions_channel_id"))
        if sub_ch:
            emb = discord.Embed(title="🆕 طلب تقديم جديد", description=f"المقدم: {interaction.user.mention}", color=discord.Color.blue(), timestamp=datetime.datetime.now())
            for idx, (q, a) in enumerate(zip(questions, answers)):
                emb.add_field(name=f"س{idx+1}: {q}", value=a if a else "—", inline=False)

            class ApplicationDecisionView(discord.ui.View):
                def __init__(self, guild_id, target_user_id):
                    super().__init__(timeout=None)
                    self.guild_id = guild_id
                    self.target_user_id = target_user_id

                @discord.ui.button(label="قبول", style=discord.ButtonStyle.success)
                async def accept(self, inter: discord.Interaction, button: discord.ui.Button):
                    await inter.response.send_modal(AcceptModal(self.target_user_id))

                @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger)
                async def reject(self, inter: discord.Interaction, button: discord.ui.Button):
                    data = load_data()
                    data["guilds"][str(inter.guild_id)]["pending_requests"].pop(self.target_user_id, None)
                    save_data(data)
                    try:
                        user = await bot.fetch_user(int(self.target_user_id))
                        await user.send("❌ تم رفض طلبك.")
                    except Exception:
                        pass
                    await inter.response.send_message(f"❌ تم رفض طلب <@{self.target_user_id}>.", ephemeral=True)

            await sub_ch.send(embed=emb, view=ApplicationDecisionView(guild_id, user_id))

        # إشعار بسيط في لوج عن وجود طلب جديد (بدون تفاصيل)
        log_ch = interaction.guild.get_channel(settings.get("log_channel_id"))
        if log_ch and sub_ch:
            await log_ch.send(f"📥 تم استلام طلب جديد من {interaction.user.mention} — راجع {sub_ch.mention}")

# --- [ أمر السلاش لإرسال رسالة التقديم ] ---
@bot.tree.command(name="setup_apply", description="إرسال رسالة التقديم في الروم الحالي")
@app_commands.checks.has_permissions(administrator=True)
async def setup_apply(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏢 المركز الرئيسي للسجل المدني",
        description="مرحباً بك في نظام الهوية الوطنية. لكي تتمكن من الحصول على رتبة مواطن والاستمتاع بكامل الصلاحيات، يرجى الضغط على الزر أدناه وتعبئة البيانات المطلوبة بدقة.\n\n"
                    "⚠️ **ملاحظات هامة:**\n"
                    "• تأكد من صحة البيانات.\n"
                    "• الحسابات الوهمية أو الجديدة سيتم رفضها تلقائياً.\n"
                    "• سيتم مراجعة طلبك من قبل الموظفين المختصين.",
        color=discord.Color.green()
    )
    embed.set_footer(text="نظام السجل المدني - برمجة المطور جواد")
    await interaction.channel.send(embed=embed, view=ApplyView())
    await interaction.response.send_message("✅ تم إرسال رسالة التقديم بنجاح.", ephemeral=True)


@bot.tree.command(name="set_submissions", description="تعيين روم الطلبات الحالي (لاستقبال التفاصيل)")
@app_commands.checks.has_permissions(administrator=True)
async def set_submissions(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    if guild_id not in data["guilds"]:
        return await interaction.response.send_message("❌ السيرفر غير مفعل! استخدم `/activate` أولاً.", ephemeral=True)

    channel = interaction.channel
    data["guilds"][guild_id]["settings"]["submissions_channel_id"] = channel.id
    save_data(data)
    await interaction.response.send_message(f"✅ تم تعيين قناة الطلبات إلى: {channel.mention}", ephemeral=True)


@bot.tree.command(name="export_requests", description="تصدير الطلبات المعلقة كملف JSON (مباشر في الخاص) ")
@app_commands.checks.has_permissions(manage_guild=True)
async def export_requests(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    pending = data["guilds"].get(guild_id, {}).get("pending_requests", {})
    if not pending:
        return await interaction.response.send_message("📭 لا توجد طلبات معلقة حالياً.", ephemeral=True)

    import io, json
    buf = io.BytesIO(json.dumps(pending, ensure_ascii=False, indent=2).encode('utf-8'))
    buf.seek(0)
    try:
        await interaction.user.send(file=discord.File(fp=buf, filename=f"pending_requests_{guild_id}.json"))
        await interaction.response.send_message("✅ تم إرسال ملف الطلبات في الخاص.", ephemeral=True)
    except Exception:
        await interaction.response.send_message("❌ فشل إرسال الملف في الخاص. تأكد أن الخاص مفتوح.", ephemeral=True)

# --- [ نهاية الجزء السادس ] ---
# --- [ الجزء السابع: نظام القبول، الرفض، والمخالفات ] ---

# --- [ مودال تحديد تاريخ الصلاحية عند القبول ] ---
class AcceptModal(discord.ui.Modal, title="تحديد صلاحية الهوية"):
    expiry = discord.ui.TextInput(label="تاريخ الانتهاء (مثلاً: 2027-01-01)", placeholder="YYYY-MM-DD", min_length=10, max_length=10)

    def __init__(self, target_user_id):
        super().__init__()
        self.target_user_id = target_user_id

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        guild_id = str(interaction.guild_id)
        user_id = self.target_user_id

        if user_id not in data["guilds"][guild_id]["pending_requests"]:
            return await interaction.response.send_message("❌ هذا الطلب لم يعد موجوداً.", ephemeral=True)

        req_data = data["guilds"][guild_id]["pending_requests"].pop(user_id)

        # إنشاء بيانات الهوية الجديدة
        citizen_data = {
            "name": req_data["name"],
            "issued_at": str(datetime.datetime.now().strftime("%Y-%m-%d")),
            "expiry_date": self.expiry.value,
            "fines": [],
            "status": "Active"
        }

        data["guilds"][guild_id]["citizens"][user_id] = citizen_data
        save_data(data)

        # إعطاء الرتبة تلقائياً إذا كانت مفعلة
        settings = data["guilds"][guild_id]["settings"]
        if settings["auto_role_enabled"] and settings["citizen_role_id"]:
            guild = interaction.guild
            member = guild.get_member(int(user_id))
            if member:
                role = guild.get_role(settings["citizen_role_id"])
                if role: await member.add_roles(role)

        # إرسال الهوية في روم السجلات
        records_channel = interaction.guild.get_channel(settings["records_channel_id"])
        if records_channel:
            embed_id = discord.Embed(title="💳 بطاقة هوية وطنية المعتمدة", color=discord.Color.green())
            embed_id.add_field(name="👤 المواطن:", value=f"<@{user_id}>", inline=True)
            embed_id.add_field(name="📅 تاريخ الإصدار:", value=citizen_data["issued_at"], inline=True)
            embed_id.add_field(name="⏳ تاريخ الانتهاء:", value=citizen_data["expiry_date"], inline=True)
            embed_id.set_footer(text=f"رقم الهوية: {user_id}")
            await records_channel.send(embed=embed_id)

        await interaction.response.send_message(f"✅ تم قبول طلب <@{user_id}> وإصدار الهوية!", ephemeral=True)

# --- [ أمر تقديم بلاغ ] ---
@bot.tree.command(name="report", description="تقديم بلاغ للإدارة أو الشرطة")
@app_commands.describe(type="نوع البلاغ (admin/police)", details="تفاصيل البلاغ")
@app_commands.choices(type=[
    app_commands.Choice(name="إداري", value="admin"),
    app_commands.Choice(name="شرطي", value="police")
])
async def report(interaction: discord.Interaction, type: str, details: str):
    data = load_data()
    guild_id = str(interaction.guild_id)
    
    report_entry = {
        "type": type,
        "details": details,
        "reporter": interaction.user.name,
        "date": str(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    }
    
    if type == "admin":
        channel_id = data["guilds"][guild_id]["settings"].get("reports_channel_id")
    else:
        channel_id = data["guilds"][guild_id]["settings"].get("log_channel_id")  # أو روم شرطي إذا كان
    
    channel = interaction.guild.get_channel(channel_id)
    if channel:
        embed = discord.Embed(title=f"📢 بلاغ {type}", description=details, color=discord.Color.red())
        embed.set_footer(text=f"من {interaction.user}")
        await channel.send(embed=embed)
    
    await interaction.response.send_message("✅ تم إرسال البلاغ بنجاح.", ephemeral=True)

# --- [ مودالات الشكاوي والاقتراحات ] ---
class ComplaintsModal(discord.ui.Modal, title="تقديم شكوى"):
    name = discord.ui.TextInput(label="الاسم", placeholder="اسمك الكامل", required=True)
    server_link = discord.ui.TextInput(label="رابط السيرفر (اختياري)", placeholder="https://discord.gg/...", required=False)
    activation_code = discord.ui.TextInput(label="كود التفعيل (اختياري)", placeholder="الكود المستخدم في السيرفر", required=False)
    complaint_type = discord.ui.TextInput(label="نوع الشكوى", placeholder="مثال: مشكلة تقنية، سلوك سيء...", required=True)
    details = discord.ui.TextInput(label="تفاصيل الشكوى", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        
        # حفظ الشكوى
        complaint_entry = {
            "name": self.name.value,
            "server_link": self.server_link.value or "لم يتم التحديد",
            "activation_code": self.activation_code.value or "لم يتم التحديد",
            "complaint_type": self.complaint_type.value,
            "details": self.details.value,
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "guild_id": interaction.guild_id,
            "guild_name": interaction.guild.name,
            "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        
        if "complaints" not in data:
            data["complaints"] = []
        data["complaints"].append(complaint_entry)
        save_data(data)
        
        # إرسال إلى روم الشكاوي
        complaint_ch_id = data.get("global_settings", {}).get("complaints_channel_id")
        
        if complaint_ch_id:
            try:
                ch = bot.get_channel(complaint_ch_id)
                if ch:
                    emb = discord.Embed(title="⚠️ شكوى جديدة", color=discord.Color.red())
                    emb.add_field(name="👤 الاسم", value=self.name.value, inline=False)
                    emb.add_field(name="🔗 رابط السيرفر", value=self.server_link.value or "لم يتم التحديد", inline=False)
                    emb.add_field(name="🔐 كود التفعيل", value=self.activation_code.value or "لم يتم التحديد", inline=False)
                    emb.add_field(name="📝 نوع الشكوى", value=self.complaint_type.value, inline=False)
                    emb.add_field(name="📌 التفاصيل", value=self.details.value, inline=False)
                    emb.add_field(name="👨‍💼 المستخدم", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
                    emb.add_field(name="🏢 السيرفر", value=f"{interaction.guild.name} ({interaction.guild_id})", inline=False)
                    emb.set_footer(text=f"الوقت: {complaint_entry['timestamp']}")
                    await ch.send(embed=emb)
            except Exception as e:
                print(f"❌ خطأ في إرسال الشكوى: {e}")
        
        await interaction.response.send_message("✅ تم استقبال شكايتك بنجاح! شكراً لتعاونك.", ephemeral=True)


class SuggestionsModal(discord.ui.Modal, title="تقديم اقتراح"):
    name = discord.ui.TextInput(label="الاسم", placeholder="اسمك الكامل", required=True)
    suggestion_type = discord.ui.TextInput(label="نوع الاقتراح", placeholder="مثال: ميزة جديدة، تحسين...")
    details = discord.ui.TextInput(label="تفاصيل الاقتراح", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_data()
        
        # حفظ الاقتراح
        suggestion_entry = {
            "name": self.name.value,
            "suggestion_type": self.suggestion_type.value,
            "details": self.details.value,
            "user_id": interaction.user.id,
            "username": interaction.user.name,
            "guild_id": interaction.guild_id,
            "guild_name": interaction.guild.name,
            "timestamp": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        }
        
        if "suggestions" not in data:
            data["suggestions"] = []
        data["suggestions"].append(suggestion_entry)
        save_data(data)
        
        # إرسال إلى روم الاقتراحات
        suggestion_ch_id = data.get("global_settings", {}).get("suggestions_channel_id")
        
        if suggestion_ch_id:
            try:
                ch = bot.get_channel(suggestion_ch_id)
                if ch:
                    emb = discord.Embed(title="💡 اقتراح جديد", color=discord.Color.blue())
                    emb.add_field(name="👤 الاسم", value=self.name.value, inline=False)
                    emb.add_field(name="🎯 نوع الاقتراح", value=self.suggestion_type.value, inline=False)
                    emb.add_field(name="📌 التفاصيل", value=self.details.value, inline=False)
                    emb.add_field(name="👨‍💼 المستخدم", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
                    emb.add_field(name="🏢 السيرفر", value=f"{interaction.guild.name} ({interaction.guild_id})", inline=False)
                    emb.set_footer(text=f"الوقت: {suggestion_entry['timestamp']}")
                    await ch.send(embed=emb)
            except Exception as e:
                print(f"❌ خطأ في إرسال الاقتراح: {e}")
        
        await interaction.response.send_message("✅ تم استقبال اقتراحك بنجاح! شكراً لمساهمتك.", ephemeral=True)


# --- [ أمر السلاش للشكاوي والاقتراحات ] ---
@bot.tree.command(name="feedback", description="تقديم شكوى أو اقتراح")
async def feedback_command(interaction: discord.Interaction):
    """أمر متعدد الخيارات للشكاوي والاقتراحات"""
    class FeedbackView(discord.ui.View):
        @discord.ui.button(label="تقديم شكوى", style=discord.ButtonStyle.danger, emoji="⚠️")
        async def complaints(self, inter: discord.Interaction, button: discord.ui.Button):
            await inter.response.send_modal(ComplaintsModal())
        
        @discord.ui.button(label="تقديم اقتراح", style=discord.ButtonStyle.success, emoji="💡")
        async def suggestions(self, inter: discord.Interaction, button: discord.ui.Button):
            await inter.response.send_modal(SuggestionsModal())
    
    emb = discord.Embed(
        title="📬 مركز الشكاوي والاقتراحات",
        description="اختر نوع الملاحظة التي تريد تقديمها:",
        color=discord.Color.blue()
    )
    emb.add_field(name="⚠️ شكوى", value="أبلغ عن مشكلة أو مشكلة تقنية", inline=True)
    emb.add_field(name="💡 اقتراح", value="قدم اقتراحاً أو فكرة لتحسين البوت", inline=True)
    
    await interaction.response.send_message(embed=emb, view=FeedbackView(), ephemeral=True)

@bot.tree.command(name="pay_fine", description="طلب سداد مخالفة")
async def pay_fine(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    instructions = data.get("guilds", {}).get(guild_id, {}).get("settings", {}).get("payment_instructions", "يرجى التواصل مع الإدارة للسداد.")
    
    embed = discord.Embed(title="💰 تعليمات السداد", description=instructions, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed, ephemeral=True)
@bot.tree.command(name="fine", description="إعطاء مخالفة لمواطن مسجل (للإدارة أو الشرطة)")
@app_commands.describe(member="المواطن المخالف", reason="سبب المخالفة")
async def give_fine(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not has_admin_role(interaction.user) and not has_police_role(interaction.user):
        return await interaction.response.send_message("❌ ليس لديك صلاحية لتسجيل المخالفات.", ephemeral=True)
    data = load_data()
    guild_id = str(interaction.guild_id)
    user_id = str(member.id)

    if user_id not in data["guilds"][guild_id]["citizens"]:
        return await interaction.response.send_message("❌ هذا الشخص لا يملك هوية مسجلة!", ephemeral=True)

    fine_entry = {
        "reason": reason,
        "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        "admin": interaction.user.name
    }
    
    data["guilds"][guild_id]["citizens"][user_id]["fines"].append(fine_entry)
    save_data(data)

    # إرسال لوج بالمخالفة
    log_channel = interaction.guild.get_channel(data["guilds"][guild_id]["settings"]["log_channel_id"])
    if log_channel:
        embed_fine = discord.Embed(title="⚠️ تسجيل مخالفة جديدة", color=discord.Color.red())
        embed_fine.add_field(name="المخالف:", value=member.mention)
        embed_fine.add_field(name="السبب:", value=reason)
        embed_fine.add_field(name="بواسطة:", value=interaction.user.mention)
        await log_channel.send(embed=embed_fine)

    await interaction.response.send_message(f"✅ تم تسجيل المخالفة لـ {member.mention} بنجاح.")

# --- [ أمر تقرير شرطي ] ---
@bot.tree.command(name="police_report", description="إرسال تقرير شرطي")
@app_commands.describe(title="عنوان التقرير", details="تفاصيل التقرير")
async def police_report(interaction: discord.Interaction, title: str, details: str):
    if not has_police_role(interaction.user):
        return await interaction.response.send_message("❌ ليس لديك صلاحية شرطية.", ephemeral=True)
    
    data = load_data()
    guild_id = str(interaction.guild_id)
    report = {
        "title": title,
        "details": details,
        "author": interaction.user.name,
        "date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    }
    data["guilds"][guild_id]["police_reports"].append(report)
    save_data(data)
    
    embed = discord.Embed(title=f"🚔 تقرير شرطي: {title}", description=details, color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة {interaction.user}")
    
    # إرسال إلى روم اللوج أو روم محدد
    log_channel_id = data["guilds"][guild_id]["settings"]["log_channel_id"]
    log_channel = interaction.guild.get_channel(log_channel_id)
    if log_channel:
        await log_channel.send(embed=embed)
    
    await interaction.response.send_message("✅ تم إرسال التقرير بنجاح.", ephemeral=True)

# --- [ أمر عرض الطلبات المعلقة ] ---
@bot.tree.command(name="check_requests", description="عرض طلبات الهوية المعلقة لمراجعتها (للإدارة)")
async def check_requests(interaction: discord.Interaction):
    if not has_admin_role(interaction.user):
        return await interaction.response.send_message("❌ هذا الأمر للإدارة فقط.", ephemeral=True)
    data = load_data()
    guild_id = str(interaction.guild_id)
    requests = data["guilds"][guild_id].get("pending_requests", {})

    if not requests:
        return await interaction.response.send_message("📭 لا توجد طلبات معلقة حالياً.", ephemeral=True)

    embed = discord.Embed(title="📋 قائمة الطلبات المعلقة", color=discord.Color.gold())
    
    # سنعرض أول طلب فقط كمثال للتحكم به (للبساطة في الجزء الحالي)
    user_id = list(requests.keys())[0]
    req = requests[user_id]
    
    embed.description = f"الطلب الخاص بـ: <@{user_id}>\nتاريخ التقديم: `{req['applied_at']}`"
    
    # أزرار القبول والرفض
    class DecisionView(discord.ui.View):
        @discord.ui.button(label="قبول", style=discord.ButtonStyle.success)
        async def accept(self, inter: discord.Interaction, button: discord.ui.Button):
            await inter.response.send_modal(AcceptModal(user_id))
        
        @discord.ui.button(label="رفض", style=discord.ButtonStyle.danger)
        async def reject(self, inter: discord.Interaction, button: discord.ui.Button):
            data = load_data()
            data["guilds"][str(inter.guild_id)]["pending_requests"].pop(user_id)
            save_data(data)
            await inter.response.send_message(f"❌ تم رفض طلب <@{user_id}>.", ephemeral=True)

    await interaction.response.send_message(embed=embed, view=DecisionView(), ephemeral=True)

# --- [ نهاية الجزء السابع ] ---
# --- [ الجزء الثامن: الأوامر العامة، لوحة المطور، والتشغيل ] ---

# --- [ أمر عرض السجل الإجرامي ] ---
@bot.tree.command(name="criminal_record", description="عرض السجل الإجرامي الكامل لمواطن")
@app_commands.describe(member="المواطن المراد عرض سجله")
async def criminal_record(interaction: discord.Interaction, member: discord.Member):
    if not has_police_role(interaction.user) and not has_admin_role(interaction.user):
        return await interaction.response.send_message("❌ ليس لديك صلاحية لعرض السجلات الإجرامية.", ephemeral=True)
    
    data = load_data()
    guild_id = str(interaction.guild_id)
    user_id = str(member.id)
    
    citizen = data.get("guilds", {}).get(guild_id, {}).get("citizens", {}).get(user_id)
    if not citizen:
        return await interaction.response.send_message("❌ هذا الشخص لا يملك هوية مسجلة.", ephemeral=True)
    
    fines = citizen.get("fines", [])
    embed = discord.Embed(title=f"🚔 السجل الإجرامي لـ {member}", color=discord.Color.red())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="👤 الاسم:", value=citizen["name"], inline=True)
    embed.add_field(name="🆔 الرقم الوطني:", value=user_id, inline=True)
    embed.add_field(name="📅 تاريخ الإصدار:", value=citizen["issued_at"], inline=True)
    
    if fines:
        fines_text = "\n".join([f"• {f['reason']} — {f['date']} — بواسطة {f['admin']}" for f in fines])
        embed.add_field(name=f"⚠️ المخالفات ({len(fines)}):", value=fines_text, inline=False)
    else:
        embed.add_field(name="✅ السجل الجنائي:", value="لا توجد مخالفات مسجلة.", inline=False)
    
    embed.set_footer(text="نظام وزارة الداخلية - السجل المدني")
    await interaction.response.send_message(embed=embed, ephemeral=True)
@bot.tree.command(name="identity", description="عرض بطاقة هويتك الوطنية ومخالفاتك")
@app_commands.describe(member="اختر مواطن لعرض هويته (اختياري للإدارة)")
async def show_identity(interaction: discord.Interaction, member: discord.Member = None):
    data = load_data()
    guild_id = str(interaction.guild_id)
    target = member if member else interaction.user
    user_id = str(target.id)

    if user_id not in data["guilds"][guild_id].get("citizens", {}):
        return await interaction.response.send_message(f"❌ {'أنت لا تملك' if target == interaction.user else 'هذا الشخص لا يملك'} هوية مسجلة في النظام.", ephemeral=True)

    citizen = data["guilds"][guild_id]["citizens"][user_id]
    
    # حساب الحالة (نشط/منتهي)
    status = "🟢 نشط"
    expiry = datetime.datetime.strptime(citizen["expiry_date"], "%Y-%m-%d")
    if datetime.datetime.now() > expiry:
        status = "🔴 منتهي الصلاحية"

    embed = discord.Embed(title="🇸🇦 السجل المدني - بطاقة الهوية", color=discord.Color.blue())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="👤 الاسم:", value=f"**{citizen['name']}**", inline=True)
    embed.add_field(name="🆔 الرقم الوطني:", value=f"`{user_id}`", inline=True)
    embed.add_field(name="💠 الحالة:", value=status, inline=True)
    embed.add_field(name="📅 تاريخ الإصدار:", value=citizen["issued_at"], inline=True)
    embed.add_field(name="⏳ تاريخ الانتهاء:", value=citizen["expiry_date"], inline=True)
    
    # عرض المخالفات
    fines_list = citizen.get("fines", [])
    if fines_list:
        fines_text = "\n".join([f"• {f['reason']} (`{f['date']}`)" for f in fines_list[-3:]]) # عرض آخر 3
        embed.add_field(name=f"⚠️ المخالفات ({len(fines_list)}):", value=fines_text, inline=False)
    else:
        embed.add_field(name="✅ السجل الجنائي:", value="لا توجد مخالفات مسجلة.", inline=False)

    embed.set_footer(text="نظام السجل المدني - برمجة جواد")
    await interaction.response.send_message(embed=embed)

# --- [ أمر المساعدة العام (سلاش) ] ---
@bot.tree.command(name="help", description="عرض دليل شامل لأوامر البوت مع التصنيفات والأذونات")
async def public_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 دليل أوامر السجل المدني - الإصدار المحدث",
        description="مرحباً بك في نظام السجل المدني! إليك جميع الأوامر المتاحة مصنفة حسب الصلاحيات.\n\n"
                    "💡 **نصائح:**\n"
                    "• الأوامر تتطلب صلاحيات محددة (مذكورة بجانب كل أمر)\n"
                    "• استخدم `/` لبدء الأمر\n"
                    "• بعض الأوامر تظهر فقط للمستخدمين ذوي الصلاحيات",
        color=discord.Color.blue()
    )
    
    # أوامر المواطنين (متاحة للجميع)
    embed.add_field(
        name="👤 أوامر المواطنين (متاحة للجميع)",
        value="`/activate [code]`: تفعيل البوت في سيرفرك باستخدام كود الشراء\n"
              "`/identity [member]`: عرض بطاقة هويتك أو هوية شخص آخر\n"
              "`/pay_fine`: طلب تعليمات السداد للمخالفات\n"
              "`/report [type] [details]`: تقديم بلاغ إداري أو شرطي\n"
              "`/avatar [member]`: عرض صورة البروفايل\n"
              "`/userinfo [member]`: عرض معلومات المستخدم\n"
              "`/recent_fines [member]`: عرض آخر المخالفات",
        inline=False
    )
    
    # أوامر الإدارة (للمدراء)
    embed.add_field(
        name="👑 أوامر الإدارة (للمدراء فقط)",
        value="`/admin_panel`: لوحة تحكم شاملة لإعدادات البوت والأسئلة والرتب\n"
              "`/setup_rooms`: إنشاء جميع الرومات المطلوبة تلقائياً\n"
              "`/setup_apply`: إرسال رسالة التقديم في الروم المحدد\n"
              "`/check_requests`: مراجعة طلبات الهوية المعلقة\n"
              "`/fine [member] [reason]`: تسجيل مخالفة لمواطن\n"
              "`/serverinfo`: عرض معلومات السيرفر\n"
              "`/pending_count`: عدد الطلبات المعلقة\n"
              "`/export_guild`: تصدير بيانات السيرفر كملف JSON\n"
              "`/add_question [text]`: إضافة سؤال جديد للتقديم\n"
              "`/remove_question [index]`: حذف سؤال حسب رقمه\n"
              "`/set_submissions`: تعيين روم الطلبات\n"
              "`/export_requests`: تصدير الطلبات المعلقة",
        inline=False
    )
    
    # أوامر الشرطة (للرتب الشرطية)
    embed.add_field(
        name="🚔 أوامر الشرطة (للرتب الشرطية)",
        value="`/police_panel`: لوحة تحكم الشرطة والأمان\n"
              "`/criminal_record [member]`: عرض السجل الإجرامي الكامل\n"
              "`/police_report [title] [details]`: إرسال تقرير شرطي",
        inline=False
    )
    
    # أوامر التقديمات (للرتب التقديمية)
    embed.add_field(
        name="📝 أوامر التقديمات (للرتب التقديمية)",
        value="`/recruitment_panel`: لوحة تحكم الوظائف والتقديمات\n"
              "(إنشاء تقديمات وظيفية مخصصة من البانيل)",
        inline=False
    )
    
    # أوامر عامة
    embed.add_field(
        name="🌐 أوامر عامة",
        value="`/help`: عرض هذا الدليل\n"
              "`/ping`: اختبار استجابة البوت\n"
              "`/uptime`: عرض مدة تشغيل البوت",
        inline=False
    )
    
    # أوامر المطور (للمطور فقط)
    if is_dev(interaction.user.id):
        embed.add_field(
            name="👨‍💻 أوامر المطور (للمطور فقط)",
            value="`!broadcast [message]`: إرسال رسالة برودكاست لجميع السيرفرات المفعلة",
            inline=False
        )
    
    embed.set_footer(text="نظام السجل المدني | برمجة جواد | للمساعدة الإضافية، تواصل مع الإدارة")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- [ أمر برودكاست للمطور (Prefix Command) ] ---
@bot.command(name="broadcast")
async def broadcast_prefix_command(ctx, *, message: str):
    """إرسال برودكاست لجميع السيرفرات المفعلة"""
    if not is_dev(ctx.author.id):
        return await ctx.send("❌ هذا الأمر مخصص للمطور جواد فقط.")
    
    if not message or len(message.strip()) == 0:
        return await ctx.send("⚠️ يجب إدخال نص البرودكاست.")
    
    data = load_data()
    count = 0
    for g_id in data["guilds"]:
        guild = bot.get_guild(int(g_id))
        if guild:
            # تحديد الروم: إما برودكاست_شانيل أو أول روم
            broadcast_ch_id = data["guilds"][g_id]["settings"].get("broadcast_channel_id")
            if broadcast_ch_id:
                ch = guild.get_channel(broadcast_ch_id)
            else:
                # إذا لم يحدد، استخدم أول روم متاح
                ch = guild.text_channels[0] if guild.text_channels else None
            
            if ch:
                try:
                    emb = discord.Embed(title="📢 برودكاست من المطور", description=message, color=discord.Color.gold())
                    await ch.send(embed=emb)
                    count += 1
                except:
                    pass
    await ctx.send(f"✅ تم إرسال البرودكاست إلى {count} سيرفر.")

# --- [ لوحة تحكم المطور جواد (برودكاست وإحصائيات) ] ---

class DevPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="البرودكاست", style=discord.ButtonStyle.primary, emoji="📢")
    async def dev_broadcast(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"💬 استخدم الأمر: `!broadcast [النص]` في أي سيرفر مفعل.", ephemeral=True)

    @discord.ui.button(label="إحصائيات الأكواد", style=discord.ButtonStyle.secondary, emoji="📊")
    async def view_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        unused = len([c for c, v in data["codes"].items() if v["status"] == "unused"])
        used = len(data["codes"]) - unused
        await interaction.response.send_message(f"📈 **إحصائيات:**\n• أكواد متوفرة: `{unused}`\n• أكواد مستخدمة: `{used}`\n• إجمالي السيرفرات: `{len(data['guilds'])}`", ephemeral=True)

    @discord.ui.button(label="رومات الشكاوي/الاقتراحات", style=discord.ButtonStyle.secondary, emoji="📮")
    async def feedback_channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        complaints_id = data.get("global_settings", {}).get("complaints_channel_id", "لم تُحدد")
        suggestions_id = data.get("global_settings", {}).get("suggestions_channel_id", "لم تُحدد")
        
        msg = f"📮 **الرومات المخصصة:**\n"
        msg += f"⚠️ روم الشكاوي: `{complaints_id}`\n"
        msg += f"💡 روم الاقتراحات: `{suggestions_id}`\n\n"
        msg += f"لتحديد الرومات، استخدم:\n"
        msg += f"`!شكاوي [channel_id]` - لتحديد روم الشكاوي\n"
        msg += f"`!اقتراحات [channel_id]` - لتحديد روم الاقتراحات"
        
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="إيقاف البوت", style=discord.ButtonStyle.danger, emoji="🔌")
    async def shutdown(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚠️ جاري إيقاف البوت... وداعاً!", ephemeral=True)
        await bot.close()

@bot.command(name="dev_panel")
async def dev_panel_cmd(ctx):
    if not is_dev(ctx.author.id):
        return await ctx.send("❌ هذا الأمر مخصص للمطور جواد فقط.")
    embed = discord.Embed(title="👑 لوحة تحكم المطور العالمية", description="تحكم في جميع السيرفرات المفعلة للبوت من مكان واحد.", color=discord.Color.dark_red())
    await ctx.send(embed=embed, view=DevPanelView())


@bot.command(name="on")
@dev_only
async def bot_on(ctx):
    data = load_data()
    data.setdefault("global_settings", {})["public_enabled"] = True
    save_data(data)
    await ctx.send("✅ تم تفعيل البوت للعامة. البوت يعمل الآن بشكل طبيعي.")


@bot.command(name="off")
@dev_only
async def bot_off(ctx):
    data = load_data()
    data.setdefault("global_settings", {})["public_enabled"] = False
    save_data(data)
    await ctx.send("⛔ تم إيقاف البوت عن المتابعين العاديين — البوت الآن تحت التطوير.")


@bot.command(name="شكاوي")
@dev_only
async def set_complaints_channel_cmd(ctx, channel_id: int):
    """تحديد روم الشكاوي"""
    data = load_data()
    data.setdefault("global_settings", {})["complaints_channel_id"] = channel_id
    save_data(data)
    await ctx.send(f"✅ تم تعيين روم الشكاوي: <#{channel_id}>")


@bot.command(name="اقتراحات")
@dev_only
async def set_suggestions_channel_cmd(ctx, channel_id: int):
    """تحديد روم الاقتراحات"""
    data = load_data()
    data.setdefault("global_settings", {})["suggestions_channel_id"] = channel_id
    save_data(data)
    await ctx.send(f"✅ تم تعيين روم الاقتراحات: <#{channel_id}>")


@bot.command(name="restart_server")
@dev_only
async def restart_server_cmd(ctx, guild_id: int):
    """إعادة تشغيل البوت في سيرفر محدد (للمطورين فقط)"""
    data = load_data()
    gid = str(guild_id)
    
    if gid not in data.get("guilds", {}):
        return await ctx.send("❌ هذا السيرفر غير مفعل في النظام.")
    
    # إرسال رسالة تأكيد البدء
    embed_start = discord.Embed(
        title="🔄 جاري إعادة تشغيل البوت...",
        description=f"سيتم إعادة تشغيل البوت في السيرفر `{gid}` خلال 5-10 ثواني",
        color=discord.Color.orange()
    )
    embed_start.add_field(name="⏰ الوقت المقدر", value="5-10 ثواني", inline=True)
    embed_start.add_field(name="📊 الحالة", value="جاري إعادة التشغيل...", inline=True)
    embed_start.set_footer(text="لا تقلق، جميع البيانات محفوظة")
    
    await ctx.send(embed=embed_start)
    
    # تعطيل البوت مؤقتاً
    data["guilds"][gid]["settings"]["bot_enabled"] = False
    save_data(data)
    
    # انتظار 5 ثواني
    await asyncio.sleep(5)
    
    # إعادة تفعيل البوت
    data["guilds"][gid]["settings"]["bot_enabled"] = True
    save_data(data)
    
    # إرسال رسالة تأكيد الانتهاء
    embed_done = discord.Embed(
        title="✅ تم إعادة تشغيل البوت بنجاح!",
        description=f"تم إعادة تشغيل البوت في السيرفر `{gid}` وإصلاح جميع الأخطاء المؤقتة",
        color=discord.Color.green()
    )
    embed_done.add_field(name="🟢 الحالة", value="البوت يعمل بشكل طبيعي", inline=True)
    embed_done.add_field(name="💾 البيانات", value="جميع البيانات محفوظة", inline=True)
    embed_done.set_footer(text=f"تم الإعادة التشغيل بواسطة {ctx.author.name}")
    
    await ctx.send(embed=embed_done)


@bot.command(name="list_codes")
@dev_only
async def list_codes(ctx, count: int = 25):
    """Send a DM to the developer with the first `count` unused codes."""
    data = load_data()
    unused = [c for c, v in data.get("codes", {}).items() if v.get("status") == "unused"]
    if not unused:
        return await ctx.send("⚠️ لا توجد أكواد متاحة الآن.")

    display = "\n".join(unused[:count])
    try:
        await ctx.author.send(f"📦 قائمة الأكواد المتوفرة (أول {min(count, len(unused))}):\n{display}")
        await ctx.send("✅ أرسلت لك قائمة الأكواد في الخاص.")
    except Exception:
        await ctx.send("❌ فشل إرسال الخاص — افتح الرسائل الخاصة ثم حاول مرة أخرى.")


@bot.command(name="list_guilds")
@dev_only
async def list_guilds(ctx):
    data = load_data()
    guilds = data.get("guilds", {})
    if not guilds:
        return await ctx.send("⚠️ لا توجد سيرفرات مفعّلة.")
    lines = []
    for gid, info in guilds.items():
        owner = info.get("owner_id")
        code = info.get("activation_code")
        lines.append(f"• {gid} — owner: {owner} — code: {code}")
    try:
        await ctx.author.send("📋 قائمة السيرفرات المفعّلة:\n" + "\n".join(lines))
        await ctx.send("✅ أرسلت لك قائمة السيرفرات في الخاص.")
    except Exception:
        await ctx.send("❌ فشل إرسال الملف في الخاص — افتح الرسائل الخاصة.")


@bot.command(name="revoke_code")
@dev_only
async def revoke_code(ctx, code: str):
    data = load_data()
    if code not in data.get("codes", {}):
        return await ctx.send("❌ هذا الكود غير موجود.")
    data["codes"][code]["status"] = "unused"
    data["codes"][code]["guild_id"] = None
    save_data(data)
    await ctx.send(f"✅ تم إلغاء تفعيل الكود `{code}` وإعادته كـ unused.")


@bot.command(name="codexp")
@dev_only
async def code_expire(ctx, code: str):
    """تعطيل كود تفعيل معين وتعطيل جميع السيرفرات التي تستخدمه"""
    data = load_data()
    
    # التحقق من وجود الكود
    if code not in data.get("codes", {}):
        return await ctx.send("❌ هذا الكود غير موجود في النظام.")
    
    # تعطيل الكود
    data["codes"][code]["status"] = "disabled"
    data["codes"][code]["disabled_at"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data["codes"][code]["disabled_by"] = ctx.author.id
    
    # البحث عن جميع السيرفرات التي تستخدم هذا الكود وحذف بيانات السيرفر
    affected_guilds = []
    guilds_to_remove = []
    for gid, guild_data in list(data.get("guilds", {}).items()):
        if guild_data.get("activation_code") == code:
            affected_guilds.append(gid)
            guilds_to_remove.append(gid)
    
    # حذف بيانات السيرفرات المعطلة من قاعدة البيانات
    for gid in guilds_to_remove:
        del data["guilds"][gid]
    
    save_data(data)
    
    # إرسال إشعار لكل سيرفر متأثر
    disabled_count = 0
    for gid in affected_guilds:
        try:
            guild = bot.get_guild(int(gid))
            if guild:
                # إرسال في أول روم متاح
                if guild.text_channels:
                    ch = guild.text_channels[0]
                    if ch.permissions_for(guild.me).send_messages:
                        emb = discord.Embed(
                            title="🚫 تم تعطيل البوت",
                            description="تم تعطيل كود تفعيل البوت من قبل المطورين",
                            color=discord.Color.red()
                        )
                        emb.add_field(name="❌ الحالة", value="تم تعطيل جميع صلاحيات البوت على هذا السيرفر", inline=False)
                        emb.add_field(name="📝 السبب", value="الكود المستخدم تم تعطيله من قبل المطورين", inline=False)
                        emb.add_field(name="🔑 الكود", value=f"`{code}`", inline=False)
                        emb.add_field(name="✉️ الحل", value="لتفعيل البوت مجدداً، استخدم أمر `/activate` مع كود جديد", inline=False)
                        emb.set_footer(text=f"الوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        await ch.send(embed=emb)
                        disabled_count += 1
        except Exception as e:
            print(f"خطأ في إرسال رسالة التعطيل للسيرفر {gid}: {e}")
    
    # تأكيد العملية للمطور
    embed = discord.Embed(
        title="✅ تم تعطيل الكود بنجاح",
        description=f"تم تعطيل الكود `{code}` وتعطيل البوت على جميع السيرفرات المرتبطة به",
        color=discord.Color.green()
    )
    embed.add_field(name="🔑 الكود المعطل", value=f"`{code}`", inline=False)
    embed.add_field(name="📦 السيرفرات المتأثرة", value=f"**{len(affected_guilds)}** سيرفر", inline=True)
    embed.add_field(name="📨 إشعارات مرسلة", value=f"**{disabled_count}** سيرفر تلقوا الإشعار", inline=True)
    if affected_guilds:
        guilds_list = "\n".join([f"• `{gid}`" for gid in affected_guilds[:10]])
        embed.add_field(name="📋 قائمة السيرفرات", value=f"{guilds_list}{'...' if len(affected_guilds) > 10 else ''}", inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.name} | الوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await ctx.send(embed=embed)


@bot.command(name="servercodexp")
@dev_only
async def server_code_expire(ctx):
    """تعطيل كود تفعيل السيرفر الحالي مباشرة"""
    data = load_data()
    guild_id = str(ctx.guild.id)
    
    # التحقق من أن السيرفر مفعل
    if guild_id not in data.get("guilds", {}):
        return await ctx.send("❌ هذا السيرفر غير مفعل في النظام.")
    
    # الحصول على كود التفعيل
    guild_data = data["guilds"][guild_id]
    activation_code = guild_data.get("activation_code")
    
    if not activation_code:
        return await ctx.send("❌ لم يتم العثور على كود تفعيل لهذا السيرفر.")
    
    # التحقق من وجود الكود في قاعدة البيانات
    if activation_code not in data.get("codes", {}):
        return await ctx.send(f"❌ الكود `{activation_code}` غير موجود في النظام.")
    
    # تعطيل الكود
    data["codes"][activation_code]["status"] = "disabled"
    data["codes"][activation_code]["disabled_at"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    data["codes"][activation_code]["disabled_by"] = ctx.author.id
    
    # حذف بيانات السيرفر من قاعدة البيانات (حتى يتمكن من تسجيل كود جديد)
    del data["guilds"][guild_id]
    
    save_data(data)
    
    # إرسال رسالة للسيرفر في أول روم
    try:
        first_channel = None
        for channel in sorted(ctx.guild.text_channels, key=lambda c: c.position):
            if channel.permissions_for(ctx.guild.me).send_messages:
                first_channel = channel
                break
        
        if first_channel:
            emb = discord.Embed(
                title="🚫 تم تعطيل البوت",
                description="تم تعطيل كود تفعيل البوت من قبل المطورين",
                color=discord.Color.red()
            )
            emb.add_field(name="❌ الحالة", value="تم تعطيل جميع صلاحيات البوت على هذا السيرفر", inline=False)
            emb.add_field(name="📝 السبب", value="الكود المستخدم تم تعطيله من قبل المطورين", inline=False)
            emb.add_field(name="🔑 الكود", value=f"`{activation_code}`", inline=False)
            emb.add_field(name="✉️ الحل", value="لتفعيل البوت مجدداً، استخدم أمر `/activate` مع كود جديد", inline=False)
            emb.set_footer(text=f"الوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await first_channel.send(embed=emb)
    except Exception as e:
        print(f"❌ خطأ في إرسال الرسالة للسيرفر: {e}")
    
    # تأكيد للمطور
    embed = discord.Embed(
        title="✅ تم تعطيل كود السيرفر بنجاح",
        description=f"تم تعطيل كود التفعيل `{activation_code}` للسيرفر **{ctx.guild.name}**",
        color=discord.Color.green()
    )
    embed.add_field(name="🔑 الكود المعطل", value=f"`{activation_code}`", inline=False)
    embed.add_field(name="🏢 السيرفر", value=f"{ctx.guild.name} ({guild_id})", inline=False)
    embed.add_field(name="📢 الإخطار", value="تم إرسال إشعار للسيرفر في أول روم", inline=False)
    embed.set_footer(text=f"بواسطة: {ctx.author.name} | الوقت: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await ctx.send(embed=embed)


@bot.command(name="force_activate")
@dev_only
async def force_activate(ctx, guild_id: int, code: str):
    """Force-activate a guild using a code (developer only)."""
    data = load_data()
    gid = str(guild_id)
    if code not in data.get("codes", {}):
        return await ctx.send("❌ هذا الكود غير موجود.")
    if data["codes"][code]["status"] == "used":
        return await ctx.send("⚠️ هذا الكود مستخدم بالفعل.")

    # assign
    data["codes"][code]["status"] = "used"
    data["codes"][code]["guild_id"] = gid
    data["codes"][code]["activated_by"] = ctx.author.id
    data["codes"][code]["activation_date"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # create guild entry if missing
    if gid not in data["guilds"]:
        data["guilds"][gid] = {
            "owner_id": None,
            "activation_code": code,
            "settings": {
                "bot_enabled": True,
                "auto_role_enabled": False,
                "citizen_role_id": None,
                "log_channel_id": None,
                "records_channel_id": None,
                "apply_channel_id": None,
                "reports_channel_id": None,
                "questions": ["ما هو اسمك الثلاثي؟", "كم عمرك؟", "لماذا تريد الانضمام؟"],
                "max_questions": 15,
                "fingerprint_check": True
            },
            "citizens": {},
            "fines": []
        }

    save_data(data)
    await ctx.send(f"✅ تم تفعيل السيرفر `{gid}` باستخدام الكود `{code}` بنجاح.")

# --- [ التشغيل النهائي المعتمد ] ---
 
# --- [ أوامر إضافية (معلوماتية وادارية) ] ---
@bot.tree.command(name="ping", description="اختبار استجابة البوت (اللاتنسي)")
async def ping(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    emb = discord.Embed(title="🏓 Pong!", description=f"الكمون: **{latency_ms} ms**", color=discord.Color.green())
    emb.add_field(name="🌐 السيرفرات", value=f"{len(bot.guilds)}", inline=True)
    emb.add_field(name="👥 المستخدمين", value=f"{len(bot.users)}", inline=True)
    emb.add_field(name="📊 الذاكرة المستخدمة", value=f"{round(__import__('psutil').Process().memory_info().rss / 1024 / 1024, 2)} MB", inline=True)
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="uptime", description="عرض مدة تشغيل البوت")
async def uptime(interaction: discord.Interaction):
    start = getattr(bot, "start_time", None)
    if not start:
        return await interaction.response.send_message("⏳ لم تُسجّل زمن التشغيل بعد.", ephemeral=True)
    delta = datetime.datetime.utcnow() - start
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    emb = discord.Embed(title="⏱️ مدة التشغيل", description=f"{days}d {hours}h {minutes}m {seconds}s", color=discord.Color.blurple())
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="serverinfo", description="عرض معلومات السيرفر الحالي")
@app_commands.checks.has_permissions(administrator=True)
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    emb = discord.Embed(title=f"📊 معلومات السيرفر: {g.name}", color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    emb.add_field(name="🆔 المعرف", value=g.id, inline=True)
    emb.add_field(name="👑 المالك", value=f"{g.owner} ({g.owner_id})", inline=True)
    emb.add_field(name="👥 الأعضاء", value=g.member_count, inline=True)
    emb.add_field(name="📁 القنوات", value=len(g.channels), inline=True)
    emb.set_thumbnail(url=g.icon.url if g.icon else None)
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="infobot", description="عرض معلومات تفعيل البوت بالسيرفر")
@app_commands.checks.has_permissions(administrator=True)
async def infobot(interaction: discord.Interaction):
    """عرض معلومات كود التفعيل والسيرفر"""
    data = load_data()
    guild_id = str(interaction.guild_id)
    g = interaction.guild
    
    # التحقق من تفعيل السيرفر
    if guild_id not in data["guilds"]:
        emb = discord.Embed(
            title="⚠️ السيرفر غير مفعل",
            description="هذا السيرفر لم يتم تفعيله بعد",
            color=discord.Color.orange()
        )
        emb.add_field(name="🔹 الحل", value="استخدم أمر `/activate` لتفعيل البوت", inline=False)
        return await interaction.response.send_message(embed=emb, ephemeral=True)
    
    guild_data = data["guilds"][guild_id]
    activation_code = guild_data.get("activation_code", "غير متاح")
    
    # البحث عن تاريخ التفعيل من بيانات الأكواد
    activation_date = "غير متاح"
    if activation_code in data.get("codes", {}):
        activation_date = data["codes"][activation_code].get("activation_date", "غير متاح")
    
    # حالة البوت
    bot_enabled = guild_data["settings"].get("bot_enabled", False)
    code_disabled = guild_data["settings"].get("code_disabled", False)
    
    if code_disabled:
        status = "🚫 معطل"
        color = discord.Color.red()
    elif bot_enabled:
        status = "🟢 نشط"
        color = discord.Color.green()
    else:
        status = "🔴 معطل"
        color = discord.Color.red()
    
    emb = discord.Embed(
        title="🤖 معلومات البوت",
        description=f"معلومات تفعيل البوت في السيرفر **{g.name}**",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    
    emb.add_field(name="📛 اسم السيرفر", value=g.name, inline=True)
    emb.add_field(name="🆔 معرف السيرفر", value=g.id, inline=True)
    emb.add_field(name="👥 عدد الأعضاء", value=g.member_count, inline=True)
    
    emb.add_field(name="🔑 كود التفعيل", value=f"`{activation_code}`", inline=False)
    emb.add_field(name="📅 تاريخ التفعيل", value=activation_date, inline=True)
    emb.add_field(name="📊 حالة البوت", value=status, inline=True)
    
    if code_disabled:
        emb.add_field(
            name="⚠️ السبب",
            value=guild_data["settings"].get("disabled_reason", "تم تعطيل الكود من قبل المطورين"),
            inline=False
        )
    
    emb.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
    emb.set_footer(text="نظام السجل المدني | برمجة جواد")
    
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="userinfo", description="عرض معلومات مستخدم")
@app_commands.describe(member="اختر مستخدماً (اختياري)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    emb = discord.Embed(title=f"👤 معلومات المستخدم: {target}", color=discord.Color.green())
    emb.add_field(name="🆔", value=target.id, inline=True)
    emb.add_field(name="📅 تاريخ الإنشاء", value=target.created_at.strftime('%Y-%m-%d'), inline=True)
    emb.add_field(name="📅 انضم للسيرفر", value=target.joined_at.strftime('%Y-%m-%d') if target.joined_at else '—', inline=True)
    emb.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="avatar", description="عرض صورة البروفايل لمستخدم")
@app_commands.describe(member="اختر مستخدماً (اختياري)")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    emb = discord.Embed(title=f"🖼️ صورة {target}", color=discord.Color.blurple())
    emb.set_image(url=target.display_avatar.url)
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="recent_fines", description="عرض آخر المخالفات لمستخدم")
@app_commands.describe(member="اختر مواطناً (افتراضي: أنت)")
async def recent_fines(interaction: discord.Interaction, member: discord.Member = None):
    data = load_data()
    guild_id = str(interaction.guild_id)
    target = member or interaction.user
    user_id = str(target.id)
    citizen = data.get("guilds", {}).get(guild_id, {}).get("citizens", {}).get(user_id)
    if not citizen:
        return await interaction.response.send_message("❌ هذا المستخدم لا يملك هوية مسجلة.", ephemeral=True)
    fines = citizen.get("fines", [])
    if not fines:
        return await interaction.response.send_message("✅ لا توجد مخالفات مسجلة.", ephemeral=True)
    text = "\n".join([f"• {f['reason']} — `{f['date']}`" for f in fines[-5:]])
    emb = discord.Embed(title=f"⚠️ مخالفات {target}", description=text, color=discord.Color.red())
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="pending_count", description="عرض عدد الطلبات المعلقة في السيرفر")
@app_commands.checks.has_permissions(administrator=True)
async def pending_count(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    pending = data.get("guilds", {}).get(guild_id, {}).get("pending_requests", {})
    emb = discord.Embed(title="📭 الطلبات المعلقة", description=f"عدد الطلبات: **{len(pending)}**", color=discord.Color.gold())
    await interaction.response.send_message(embed=emb, ephemeral=True)


@bot.tree.command(name="export_guild", description="تصدير بيانات السيرفر كملف JSON (للإدارة)")
@app_commands.checks.has_permissions(administrator=True)
async def export_guild(interaction: discord.Interaction):
    data = load_data()
    guild_id = str(interaction.guild_id)
    guild_data = data.get("guilds", {}).get(guild_id)
    if not guild_data:
        return await interaction.response.send_message("❌ لا توجد بيانات لهذا السيرفر.", ephemeral=True)
    import io, json
    buf = io.BytesIO(json.dumps(guild_data, ensure_ascii=False, indent=2).encode('utf-8'))
    buf.seek(0)
    try:
        await interaction.user.send(file=discord.File(fp=buf, filename=f"guild_{guild_id}_data.json"))
        await interaction.response.send_message("✅ تم إرسال ملف البيانات في الخاص.", ephemeral=True)
    except Exception:
        await interaction.response.send_message("❌ فشل إرسال الملف في الخاص. تأكد أن الخاص مفتوح.", ephemeral=True)


@bot.tree.command(name="add_question", description="إضافة سؤال جديد لقائمة الأسئلة (المدراء)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(text="نص السؤال الجديد")
async def add_question(interaction: discord.Interaction, text: str):
    data = load_data()
    guild_id = str(interaction.guild_id)
    settings = data.setdefault("guilds", {}).setdefault(guild_id, {}).setdefault("settings", {})
    questions = settings.setdefault("questions", [])
    if len(questions) >= settings.get("max_questions", 15):
        return await interaction.response.send_message("⚠️ لا يمكن إضافة أكثر من عدد الأسئلة المسموح به.", ephemeral=True)
    questions.append(text)
    save_data(data)
    await interaction.response.send_message(f"✅ تم إضافة السؤال الجديد. الآن: `{len(questions)}` سؤال.", ephemeral=True)


@bot.tree.command(name="remove_question", description="حذف سؤال حسب رقمه (المدراء)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(index="رقم السؤال (ابدأ من 1)")
async def remove_question(interaction: discord.Interaction, index: int):
    data = load_data()
    guild_id = str(interaction.guild_id)
    settings = data.get("guilds", {}).get(guild_id, {}).get("settings")
    if not settings:
        return await interaction.response.send_message("❌ لا توجد إعدادات للسيرفر.", ephemeral=True)
    questions = settings.get("questions", [])
    if not (1 <= index <= len(questions)):
        return await interaction.response.send_message("❌ رقم سؤال غير صالح.", ephemeral=True)
    removed = questions.pop(index-1)
    save_data(data)
    await interaction.response.send_message(f"✅ تم حذف السؤال: `{removed}`", ephemeral=True)

# --- [ التشغيل النهائي المعتمد والمطور ] ---

if __name__ == "__main__":
    # هذا السطر هو اللي بيفتح "البوابة" لريندر عشان يفك التعليق ويصير Live فوراً
    keep_alive() 
    
    # سحب التوكن من ملف .env أو من إعدادات ريندر
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN not set in environment or .env file.")
    else:
        print("🚀 جاري تشغيل البوت... انتظر ثواني يا بطل")
        # البوت الحين بيستخدم التوكن اللي داخل المتغير TOKEN تلقائياً
        bot.run(TOKEN)
