# ғᴀʟᴄᴏɴ !!
import subprocess
import importlib
import sys

#======================
# Packages auto-installer
#======================
REQUIRED_PACKAGES = {
    "telegram": "python-telegram-bot",
    "gtts": "gTTS",
    "requests": "requests",
    "httpx": "httpx",
    "yt_dlp": "yt-dlp",
    "emoji": "emoji"
}

for module_name, package_name in REQUIRED_PACKAGES.items():
    try:
        importlib.import_module(module_name)
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except Exception:
            sys.exit(1)

import os
import logging
import json
import asyncio
import time
import random
import string
import io
import contextlib
import emoji as emoji_lib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

#------------------------
# Logging
#------------------------
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#------------------------
#  CONFIGURATION
#------------------------
BOT_TOKEN = "8487451759:AAG6V7MHZsMjNidwN_q7sEbZm3MhgJfhY4w"
OWNER_ID = 7766306643
BOT_NAME = "Alexa"

#---------------------------------
# PREMIUM EMOJIS (from TgPremiumEmojibot.py)
#---------------------------------
PREMIUM_EMOJIS = [
    "6100639476441161711", "6102462664288509137", "6100199534351097095",
    "6102926404792360795", "6100409966273764915", "6100430105375415737",
    "6102470558438400435", "6100451820730064687", "6102638599033858630",
    "6100179369479642954", "6100485115316542792", "6102661242101440205",
    "6102592514034770678", "6102475626499808862", "6102863908723236868",
    "6102510630483271620", "6282589525348720171", "6055377380204092112",
    "6055551219005398825", "6055181976371994390", "6055481009175010794",
    "6055484548228062462", "6055202102588742236", "6055450347403484860",
    "6055228576767155521", "6055183995006623379", "6337009415278828759",
    "6336756235546663929", "6334772471757020134", "6336732269629153634",
    "6336833407519038409", "6337048276142924106", "6337018975876030803",
    "6336608132189395373", "6336797785060286399", "6336685231147326793",
    "6336907611669011898", "6336988189550451848", "6337098578799893838",
    "6336808092981796477", "6337020083977592163", "6337112997005107243",
    "6337051755066433311", "6336835907190004485", "6336618976981818626",
    "6336857218817728795", "6336974471424908889", "6337125748763008448",
    "6337098338281725706", "6336962978092425393", "6336633214798404108",
    "6337019139084786234", "6337035356881296575", "6337026908680625329",
    "6336690569791676356", "6337106906741480828", "6337072645787361389",
    "6336720729052027967", "6336670885956557643", "6337113894653271580",
    "6334488003188105980", "6336721798498884548", "6336799284003873851",
    "6337112129421713282", "6336599202952388231", "6336755629956275338",
    "6334702021408465964", "6337109865973948062", "6336708763273142215",
    "6337083451925078342", "6336930400765484501", "6334788126912815244",
    "6337059606266651217", "6336812005697002754", "6336813629194640485",
    "6337085796977221633", "6336663202260065128", "6334324468013341494",
    "6337047855236129713", "6336782885818742144", "6336664645369076808",
    "6336910583786383660", "6336862179504954500", "6336697226990985005",
    "6336772620846899242", "6337033209397649451", "6336861449360514102",
    "6336573617832206335", "6337055242579876765", "6336789422758960593",
    "6336781331040577785", "6336603218746810844", "6337123072998383823",
    "6336894825551371014", "6334681658968513467", "6336799919659031563",
    "6336707603631972035", "6336874467406389346", "6336756411640323933",
    "6336608037700115865", "6336613247495445753", "6336973539417007164",
    "6336931040715612818", "6336653869296132233", "6336836572909938734",
    "6336798231736885254", "6336813951317187443", "6336866435817545002",
    "6336662845777780692", "6336580455420141312", "6336750437340816001",
    "6336677470141422007", "6337078718871117522", "6336931345658289868",
    "6336935322798005307", "6336646834139700626", "6337010179783007229",
    "6336618208182673162", "6336580975111184057", "6336957184181543528",
    "6336991256157101601", "6336655355354815762", "6336795865209904645",
    "6337054177427988529", "6336855354801921798", "6336878444546105899",
    "6336861037043654967", "6336662472115626382", "6337093386184432717",
    "6336637947852365586", "6336876696494417749", "6334678278829252492",
    "6337087411884923105", "6336989731443711607", "6336882614959349480",
    "6336886055228153516", "6336797591786757523", "6336674519498890396",
    "6336856849450540332", "6337048379222138619", "6336816932024491505",
    "6336672814396874442", "6336835035311644293", "6336668004033504924",
    "6336682357814205676", "6336764563488252026", "6337100812182887680",
    "6336575056646249129"
]

# Common emoji IDs for UI
UI_EMOJIS = {
    "success": "6336861449360514102",
    "error": "6337033209397649451",
    "broadcast": "6336698133229082903",
    "status": "6336674562448563935",
    "welcome": "6336646834139700626",
    "bot_active": "6336674562448563935",
    "upload": "6337010179783007229",
    "terminal": "6337018975876030803",
    "premium": "6336646834139700626",
}

#---------------------------------
# CHANNEL & GC LINKS
#---------------------------------
CHANNELS = [
    {"username": "@a3lxe"},
    {"username": "@a4lxe"},
    {"username": "@earnbyxman"},
    {"username": "@wolfsex"},
    {"username": "@lib_aarishu"}
]

CHANNEL_ID = CHANNELS[0]["username"]
GROUP_ID = CHANNELS[1]["username"]
CHANNEL_LINK = f"https://t.me/{CHANNELS[0]['username'][1:]}"
GROUP_LINK = f"https://t.me/{CHANNELS[1]['username'][1:]}"

HOST_DIR = "hosted_bots"
os.makedirs(HOST_DIR, exist_ok=True)

active_processes = {}
GLOBAL_HOSTING_ACTIVE = True
DB_FILE = "hosting_db.json"

# Terminal state
terminal_mode = set()

# ============================================================
# PREMIUM EMOJI ENGINE
# ============================================================
def convert_emojis_to_premium(text: str):
    """
    Normal emojis ko premium emojis me convert karta hai.
    Returns: (final_text, entities)
    """
    final_text = ""
    entities = []
    current_offset = 0

    for char in text:
        if emoji_lib.is_emoji(char):
            rand_id = random.choice(PREMIUM_EMOJIS)
            placeholder = "✨"
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=current_offset,
                length=len(placeholder),
                custom_emoji_id=rand_id
            ))
            final_text += placeholder
            current_offset += len(placeholder)
        else:
            final_text += char
            current_offset += 1

    return final_text, entities


def premium_entities(text: str, emoji_key: str = None, bold: bool = False, code_words: list = None):
    """
    Premium emoji + bold + code entities banata hai.
    """
    entities = []

    if emoji_key and emoji_key in UI_EMOJIS:
        # Find first non-space char position for emoji
        offset = 0
        if text and text[0] == "✨":
            entities.append(MessageEntity(
                type="custom_emoji",
                offset=0,
                length=1,
                custom_emoji_id=UI_EMOJIS[emoji_key]
            ))
            offset = 1

    if bold:
        entities.append(MessageEntity(type="bold", offset=0, length=len(text)))

    if code_words:
        for word in code_words:
            idx = text.find(str(word))
            if idx != -1:
                entities.append(MessageEntity(type="code", offset=idx, length=len(str(word))))

    return entities if entities else None


async def send_premium_message(update_or_context, chat_id, text, reply_markup=None, emoji_key=None, bold=False, code_words=None):
    """
    Premium emojis ke saath message bhejta hai.
    Agar text me normal emoji hai to woh premium me convert ho jayenge.
    """
    final_text, emoji_entities = convert_emojis_to_premium(text)
    base_entities = premium_entities(final_text, emoji_key=emoji_key, bold=bold, code_words=code_words)

    all_entities = []
    if base_entities:
        all_entities.extend(base_entities)
    all_entities.extend(emoji_entities)

    # Sort by offset
    all_entities.sort(key=lambda e: e.offset)

    bot = update_or_context.bot if hasattr(update_or_context, 'bot') else update_or_context
    return await bot.send_message(
        chat_id=chat_id,
        text=final_text,
        entities=all_entities if all_entities else None,
        reply_markup=reply_markup
    )


async def edit_premium_message(query, text, reply_markup=None, emoji_key=None, bold=False, code_words=None):
    """
    Premium emojis ke saath message edit karta hai.
    """
    final_text, emoji_entities = convert_emojis_to_premium(text)
    base_entities = premium_entities(final_text, emoji_key=emoji_key, bold=bold, code_words=code_words)

    all_entities = []
    if base_entities:
        all_entities.extend(base_entities)
    all_entities.extend(emoji_entities)
    all_entities.sort(key=lambda e: e.offset)

    try:
        await query.edit_message_text(
            final_text,
            entities=all_entities if all_entities else None,
            reply_markup=reply_markup
        )
    except Exception:
        pass


# ============================================================
# PREMIUM ANIMATION ENGINE
# ============================================================
PREMIUM_SPINNER = ["✨", "🌟", "💫", "⭐", "🌠", "✨"]
PREMIUM_BARS = ["░", "▒", "▓", "█"]

def premium_progress_bar(percent: int, length: int = 10) -> str:
    filled = int(length * percent / 100)
    empty = length - filled
    return "█" * filled + "░" * empty


async def premium_animation(update_or_context, chat_id, message_id=None, steps=None, final_text=None, final_keyboard=None, final_emoji_key=None):
    """
    Premium animation ke saath message bhejta/edit karta hai.
    """
    if steps is None:
        steps = [
            (f"✨ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ...\n[{premium_progress_bar(10)}] 10%", 0.25),
            (f"🌟 ᴄᴏɴɴᴇᴄᴛɪɴɢ...\n[{premium_progress_bar(25)}] 25%", 0.25),
            (f"💫 ʟᴏᴀᴅɪɴɢ ᴅᴀᴛᴀ...\n[{premium_progress_bar(45)}] 45%", 0.25),
            (f"⭐ ᴘʀᴏᴄᴇꜱꜱɪɴɢ...\n[{premium_progress_bar(65)}] 65%", 0.25),
            (f"🌠 ꜰɪɴᴀʟɪᴢɪɴɢ...\n[{premium_progress_bar(85)}] 85%", 0.25),
            (f"✨ ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ...\n[{premium_progress_bar(100)}] 100%", 0.35),
        ]

    bot = update_or_context.bot if hasattr(update_or_context, 'bot') else update_or_context
    msg = None

    for text, duration in steps:
        final, ents = convert_emojis_to_premium(text)
        if msg is None:
            msg = await bot.send_message(chat_id, final, entities=ents if ents else None)
        else:
            try:
                await msg.edit_text(final, entities=ents if ents else None)
            except Exception:
                pass
        await asyncio.sleep(duration)

    if final_text:
        final_converted, final_ents = convert_emojis_to_premium(final_text)
        base = premium_entities(final_converted, emoji_key=final_emoji_key, bold=True)
        all_ents = []
        if base:
            all_ents.extend(base)
        all_ents.extend(final_ents)
        all_ents.sort(key=lambda e: e.offset)

        if msg:
            try:
                await msg.edit_text(
                    final_converted,
                    entities=all_ents if all_ents else None,
                    reply_markup=final_keyboard
                )
                return msg
            except Exception:
                pass

    return msg


# ============================================================
# DATABASE
# ============================================================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"user_projects": {}, "pending_approvals": {}, "user_modules": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db_data = load_db()
user_projects = db_data.get("user_projects", {})
pending_approvals = db_data.get("pending_approvals", {})
user_modules = db_data.get("user_modules", {})

#======================
#  PROCESS RUNNER
#======================
def start_script_process(user_id, filename):
    key = f"{user_id}_{filename}"
    file_path = os.path.join(HOST_DIR, str(user_id), filename)
    if not os.path.exists(file_path):
        return False
    stop_script_process(user_id, filename)
    try:
        log_file = open(f"{file_path}.log", "w")
        proc = subprocess.Popen(
            [sys.executable, file_path],
            stdout=log_file,
            stderr=log_file,
            text=True
        )
        active_processes[key] = proc
        return True
    except Exception:
        return False


def stop_script_process(user_id, filename):
    key = f"{user_id}_{filename}"
    if key in active_processes:
        proc = active_processes[key]
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        del active_processes[key]
        return True
    return False


def auto_recover_scripts():
    for u_id, files in user_projects.items():
        for f_name, details in files.items():
            if details.get("status") == "Running" and details.get("approved"):
                start_script_process(u_id, f_name)


# ============================================================
# TERMINAL EXECUTOR
# ============================================================
async def run_terminal_command(user_id: int, command: str):
    """
    User ke liye terminal command run karta hai.
    Returns: (output, success)
    """
    output = ""

    # Security: block dangerous commands
    blocked = ["rm -rf /", "mkfs", "dd if=", ":(){ :|:& };:", "shutdown", "reboot", "poweroff"]
    for b in blocked:
        if b in command:
            return "❌ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ʙʟᴏᴄᴋᴇᴅ ꜰᴏʀ ꜱᴇᴄᴜʀɪᴛʏ ʀᴇᴀꜱᴏɴꜱ.", False

    try:
        # Use shell for pip install etc.
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=os.getcwd()
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            output = stdout.decode('utf-8', errors='ignore')
            success = (proc.returncode == 0)
        except asyncio.TimeoutError:
            proc.kill()
            output = "⏱️ ᴄᴏᴍᴍᴀɴᴅ ᴛɪᴍᴇᴅ ᴏᴜᴛ (120ꜱ ʟɪᴍɪᴛ)"
            success = False
    except Exception as e:
        output = f"❌ ᴇʀʀᴏʀ: {e}"
        success = False

    if not output.strip():
        output = "✅ ᴄᴏᴍᴍᴀɴᴅ ᴇxᴇᴄᴜᴛᴇᴅ (ɴᴏ ᴏᴜᴛᴘᴜᴛ)"

    return output, success


async def install_module(user_id: int, module_name: str):
    """
    User ke liye module install karta hai.
    """
    output, success = await run_terminal_command(user_id, f"{sys.executable} -m pip install {module_name}")
    return output, success


#======================
# JOIN CHECK
#======================
async def is_user_joined(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if user_id == OWNER_ID:
        return True
    try:
        for channel in CHANNELS:
            member = await context.bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status not in ['creator', 'administrator', 'member']:
                return False
        return True
    except Exception:
        return False


async def send_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_text = (
        "╔═════════════════════╗\n"
        "     ⚠️ ᴊᴏɪɴ ᴀʟʟ ᴄʜᴀɴɴᴇʟꜱ          \n"
        "╚═════════════════════╝\n\n"
        "👇 ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ʙᴏᴛ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀʟʟ 5 ᴄʜᴀɴɴᴇʟꜱ:\n"
    )

    keyboard = []
    for channel in CHANNELS:
        username = channel["username"].replace('@', '')
        link = f"https://t.me/{username}"
        keyboard.append([InlineKeyboardButton(f"📢 {username}", url=link)])

    keyboard.append([InlineKeyboardButton("✅ ᴊᴏɪɴ ᴅᴏɴᴇ ᴄʜᴇᴄᴋ", callback_data="check_join")])

    final, ents = convert_emojis_to_premium(join_text)

    if update.message:
        await context.bot.send_message(
            update.effective_chat.id, final,
            entities=ents if ents else None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        try:
            await update.callback_query.edit_message_text(
                final, entities=ents if ents else None,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass


#======================
# MAIN MENU - USER
#======================
async def send_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    user = update.effective_user
    user_id = str(user.id)
    is_owner = (int(user_id) == OWNER_ID)
    user_files = user_projects.get(user_id, {})
    total_bots = len(user_files)
    running_bots = sum(
        1 for f in user_files.keys()
        if f"{user_id}_{f}" in active_processes and active_processes[f"{user_id}_{f}"].poll() is None
    )

    menu_text = (
        "╔═════════════════════╗\n"
        "     🌌 ᴀʟᴇxᴀ ʜᴏꜱᴛɪɴɢ        \n"
        "╚═════════════════════╝\n\n"
        f"👋 ᴡᴇʟᴄᴏᴍᴇ, {user.first_name}!\n\n"
        "📊 ʏᴏᴜʀ ꜱᴛᴀᴛꜱ\n"
        "┌─────────────────────┐\n"
        f"│ 📁 ᴛᴏᴛᴀʟ ʙᴏᴛꜱ: {total_bots}/2\n"
        f"│ ⚡ ʀᴜɴɴɪɴɢ: {running_bots}\n"
        "│ ♾️ ʜᴏꜱᴛɪɴɢ: ᴜɴʟɪᴍɪᴛᴇᴅ\n"
        "└─────────────────────┘\n\n"
        "⚡ ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🔴 📁 ᴍʏ ʙᴏᴛꜱ", callback_data="menu_mybots"),
            InlineKeyboardButton("🔵 📤 ᴜᴘʟᴏᴀᴅ ʙᴏᴛ", callback_data="menu_upload")
        ],
        [
            InlineKeyboardButton("🟢 📊 ꜱᴛᴀᴛᴜꜱ", callback_data="menu_status"),
            InlineKeyboardButton("🟡 📞 ᴄᴏɴᴛᴀᴄᴛ", callback_data="menu_contact")
        ],
        [
            InlineKeyboardButton("💻 ᴛᴇʀᴍɪɴᴀʟ", callback_data="menu_terminal"),
            InlineKeyboardButton("🔴 ❓ ʜᴇʟᴘ", callback_data="menu_help")
        ]
    ]

    if is_owner:
        keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

    final, ents = convert_emojis_to_premium(menu_text)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                final,
                entities=ents if ents else None,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass
        await update.callback_query.answer()
    elif update.message:
        await context.bot.send_message(
            update.effective_chat.id, final,
            entities=ents if ents else None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        if update.callback_query:
            await context.bot.send_message(
                update.callback_query.message.chat_id, final,
                entities=ents if ents else None,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )


#======================
# MAIN MENU - OWNER
#======================
async def send_owner_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit: bool = False):
    total_files = sum(len(proj) for proj in user_projects.values())
    active_files = len([k for k, v in active_processes.items() if v.poll() is None])
    pending = len(pending_approvals)

    menu_text = (
        "╔═════════════════════╗\n"
        "            👑 ᴀʟᴇxᴀ ᴘᴀɴᴇʟ               \n"
        "╚═════════════════════╝\n\n"
        "📊 ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ\n"
        "┌─────────────────────┐\n"
        f"│ 👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {len(user_projects)}\n"
        f"│ 📁 ꜰɪʟᴇꜱ: {total_files}\n"
        f"│ ⚡ ʀᴜɴɴɪɴɢ: {active_files}\n"
        f"│ ⏳ ᴘᴇɴᴅɪɴɢ: {pending}\n"
        f"│ 🔄 ʜᴏꜱᴛɪɴɢ: {'🟢 ᴏɴ' if GLOBAL_HOSTING_ACTIVE else '🔴 ᴏꜰꜰ'}\n"
        "└─────────────────────┘\n\n"
        "⚡ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴄᴛɪᴏɴꜱ:"
    )

    keyboard = [
        [
            InlineKeyboardButton("🟢 ᴏɴ", callback_data="owner_on"),
            InlineKeyboardButton("🔴 ᴏꜰꜰ", callback_data="owner_off")
        ],
        [
            InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="owner_broadcast"),
            InlineKeyboardButton("🔄 ʀᴇꜱᴇᴛ", callback_data="owner_reset")
        ],
        [
            InlineKeyboardButton("📥 ᴘᴇɴᴅɪɴɢ", callback_data="owner_pending"),
            InlineKeyboardButton("📋 ʟᴏɢꜱ", callback_data="owner_logs")
        ],
        [
            InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ", callback_data="owner_delete"),
            InlineKeyboardButton("📊 ꜱᴛᴀᴛᴜꜱ", callback_data="owner_status")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴍᴇɴᴜ", callback_data="menu_back")
        ]
    ]

    final, ents = convert_emojis_to_premium(menu_text)

    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                final,
                entities=ents if ents else None,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass
        await update.callback_query.answer()
    else:
        await context.bot.send_message(
            update.effective_chat.id, final,
            entities=ents if ents else None,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


#======================
# START COMMAND
#======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_joined(user_id, context):
        await send_join_request(update, context)
        return

    # Premium animation
    anim_steps = [
        (f"✨ ᴀʟᴇxᴀ ɪꜱ ᴡᴀᴋɪɴɢ ᴜᴘ...\n[{premium_progress_bar(10)}] 10%", 0.25),
        (f"🌟 ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ꜱᴇʀᴠᴇʀ...\n[{premium_progress_bar(30)}] 30%", 0.25),
        (f"💫 ʟᴏᴀᴅɪɴɢ ᴍᴏᴅᴜʟᴇꜱ...\n[{premium_progress_bar(50)}] 50%", 0.25),
        (f"⭐ ᴠᴇʀɪꜰʏɪɴɢ ᴜꜱᴇʀ...\n[{premium_progress_bar(70)}] 70%", 0.25),
        (f"🌠 ᴘʀᴇᴘᴀʀɪɴɢ ᴍᴇɴᴜ...\n[{premium_progress_bar(90)}] 90%", 0.25),
        (f"✨ ᴀʟᴇxᴀ ɪꜱ ʀᴇᴀᴅʏ!\n[{premium_progress_bar(100)}] 100%\n\n🎉 ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀʟᴇxᴀ ʜᴏꜱᴛɪɴɢ!", 0.5),
    ]

    msg = None
    for text, duration in anim_steps:
        final, ents = convert_emojis_to_premium(text)
        if msg is None:
            msg = await context.bot.send_message(
                update.effective_chat.id, final,
                entities=ents if ents else None
            )
        else:
            try:
                await msg.edit_text(final, entities=ents if ents else None)
            except Exception:
                pass
        await asyncio.sleep(duration)

    if msg:
        try:
            await msg.delete()
        except Exception:
            pass

    if user_id == OWNER_ID:
        await send_owner_menu(update, context)
    else:
        await send_user_menu(update, context)


#======================
# HANDLE DOCUMENT
#======================
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_user_joined(user.id, context):
        return

    doc = update.message.document
    if not doc.file_name.endswith('.py'):
        await send_premium_message(
            update, update.effective_chat.id,
            "❌ ᴇʀʀᴏʀ\n\nᴏɴʟʏ ᴘʏᴛʜᴏɴ (`.ᴘʏ`) ꜰɪʟᴇꜱ ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ.",
            emoji_key="error"
        )
        return

    if not GLOBAL_HOSTING_ACTIVE:
        await send_premium_message(
            update, update.effective_chat.id,
            "⚠️ ʜᴏꜱᴛɪɴɢ ɪꜱ ᴄᴜʀʀᴇɴᴛʟʏ ᴏꜰꜰ.\n\nᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ.",
            emoji_key="error"
        )
        return

    # Upload animation
    upload_steps = [
        (f"📥 ᴀᴄᴄᴇᴘᴛɪɴɢ ꜰɪʟᴇ...\n[{premium_progress_bar(15)}] 15%", 0.2),
        (f"📥 ʀᴇᴀᴅɪɴɢ ꜰɪʟᴇ ꜱɪᴢᴇ...\n[{premium_progress_bar(35)}] 35%", 0.2),
        (f"📤 ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ꜱᴇʀᴠᴇʀ...\n[{premium_progress_bar(55)}] 55%", 0.25),
        (f"📤 ᴄʜᴇᴄᴋɪɴɢ ꜰᴏʀ ᴇʀʀᴏʀꜱ...\n[{premium_progress_bar(75)}] 75%", 0.2),
        (f"⏳ ᴘᴇɴᴅɪɴɢ ᴀᴘᴘʀᴏᴠᴀʟ...\n[{premium_progress_bar(100)}] 100%", 0.3),
    ]

    anim_msg = None
    for text, duration in upload_steps:
        final, ents = convert_emojis_to_premium(text)
        if anim_msg is None:
            anim_msg = await context.bot.send_message(
                update.effective_chat.id, final,
                entities=ents if ents else None
            )
        else:
            try:
                await anim_msg.edit_text(final, entities=ents if ents else None)
            except Exception:
                pass
        await asyncio.sleep(duration)

    if anim_msg:
        try:
            await anim_msg.delete()
        except Exception:
            pass

    size_mb = doc.file_size / (1024 * 1024)
    size_str = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{doc.file_size / 1024:.1f} KB"

    bot_name = doc.file_name.replace('.py', '').replace('_', ' ').title()

    pending_card = (
        "╔═════════════════════╗\n"
        "       ⏳ ᴘᴇɴᴅɪɴɢ ᴀᴘᴘʀᴏᴠᴀʟ      \n"
        "╚═════════════════════╝\n\n"
        f"🤖 ʙᴏᴛ ɴᴀᴍᴇ: `{bot_name}`\n"
        f"📄 ꜰɪʟᴇꜱ: 1\n"
        f"📦 ꜱɪᴢᴇ: {size_str}\n\n"
        "┌────────────────────────────┐\n"
        "│  ✨ ʏᴏᴜʀ ʙᴏᴛ ʜᴀꜱ ʙᴇᴇɴ  │\n"
        "│  ᴀᴄᴄᴇᴘᴛᴇᴅ ꜰᴏʀ ᴀᴘᴘʀᴏᴠᴀʟ   │\n"
        "│  ᴀɴᴅ ᴡɪʟʟ ʙᴇ ʀᴇᴠɪᴇᴡᴇᴅ   │\n"
        "└────────────────────────────┘\n\n"
        f"📢 ᴄᴏɴᴛᴀᴄᴛ: {GROUP_LINK}"
    )

    await send_premium_message(
        update, update.effective_chat.id, pending_card, emoji_key="upload"
    )

    owner_msg_text = (
        "╔═════════════════════╗\n"
        "📥 ɴᴇᴡ ʜᴏꜱᴛɪɴɢ ʀᴇQᴜᴇꜱᴛ     \n"
        "╚═════════════════════╝\n\n"
        f"👤 ᴜꜱᴇʀ: {user.full_name}\n"
        f"🆔 ɪᴅ: `{user.id}`\n"
        f"📄 ꜰɪʟᴇ: `{doc.file_name}`\n"
        f"📦 ꜱɪᴢᴇ: {size_str}\n\n"
        "⚡ ᴀᴄᴛɪᴏɴꜱ:"
    )

    owner_keyboard = [
        [
            InlineKeyboardButton("✅ ᴀᴘᴘʀᴏᴠᴇ", callback_data=f"approve_{user.id}_{doc.file_name}"),
            InlineKeyboardButton("❌ ʀᴇᴊᴇᴄᴛ", callback_data=f"reject_{user.id}_{doc.file_name}")
        ],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴍᴇɴᴜ", callback_data="owner_menu")]
    ]

    forwarded = await context.bot.send_document(
        chat_id=OWNER_ID,
        document=doc.file_id,
        caption=owner_msg_text,
        reply_markup=InlineKeyboardMarkup(owner_keyboard),
        parse_mode="Markdown"
    )

    pending_approvals[str(forwarded.message_id)] = {
        "user_id": user.id,
        "file_id": doc.file_id,
        "filename": doc.file_name,
        "message_id": forwarded.message_id
    }
    save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})


#======================
# OWNER INLINE APPROVE / REJECT
#======================
async def owner_approve_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != OWNER_ID:
        await query.answer("❌ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ! ᴏᴡɴᴇʀ ᴏɴʟʏ!", show_alert=True)
        return

    data = query.data
    action, user_id, filename = data.split("_", 2)

    target_key = None
    for msg_id, p_data in pending_approvals.items():
        if str(p_data["user_id"]) == user_id and p_data["filename"] == filename:
            target_key = msg_id
            break

    if not target_key:
        await query.edit_message_text("❌ ʀᴇQᴜᴇꜱᴛ ɴᴏ ʟᴏɴɢᴇʀ ᴇxɪꜱᴛꜱ.")
        return

    p_data = pending_approvals[target_key]

    if action == "approve":
        pending_approvals.pop(target_key)
        user_dir = os.path.join(HOST_DIR, user_id)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, filename)

        tg_file = await context.bot.get_file(p_data["file_id"])
        await tg_file.download_to_drive(file_path)

        if user_id not in user_projects:
            user_projects[user_id] = {}
        success = start_script_process(user_id, filename)
        user_projects[user_id][filename] = {
            "status": "Running" if success else "Stopped",
            "approved": True
        }
        save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

        await query.edit_message_text(
            f"✅ ᴀᴘᴘʀᴏᴠᴇᴅ\n\n"
            f"👤 ᴜꜱᴇʀ: `{user_id}`\n"
            f"📄 ꜰɪʟᴇ: `{filename}`\n"
            f"🚀 ꜱᴛᴀᴛᴜꜱ: ʀᴜɴɴɪɴɢ",
            parse_mode="Markdown"
        )

        try:
            await send_premium_message(
                context, int(user_id),
                "╔═════════════════════╗\n"
                "      🚀 ʏᴏᴜʀ ʙᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ      \n"
                "╚═════════════════════╝\n\n"
                f"ʏᴏᴜʀ ꜰɪʟᴇ `{filename}` ʜᴀꜱ ʙᴇᴇɴ\n"
                "ᴀᴘᴘʀᴏᴠᴇᴅ ᴀɴᴅ ɪꜱ ɴᴏᴡ ʀᴜɴɴɪɴɢ!",
                emoji_key="success", code_words=[filename]
            )
        except Exception:
            pass

    elif action == "reject":
        pending_approvals.pop(target_key)
        save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

        await query.edit_message_text(
            f"❌ ʀᴇᴊᴇᴄᴛᴇᴅ\n\n"
            f"👤 ᴜꜱᴇʀ: `{user_id}`\n"
            f"📄 ꜰɪʟᴇ: `{filename}`",
            parse_mode="Markdown"
        )

        try:
            await send_premium_message(
                context, int(user_id),
                "╔═════════════════════╗\n"
                "       ❌ ʀᴇᴊᴇᴄᴛᴇᴅ         \n"
                "╚═════════════════════╝\n\n"
                f"ʏᴏᴜʀ ꜰɪʟᴇ `{filename}` ʜᴀꜱ ʙᴇᴇɴ\n"
                "ʀᴇᴊᴇᴄᴛᴇᴅ ʙʏ ᴛʜᴇ ᴏᴡɴᴇʀ.",
                emoji_key="error", code_words=[filename]
            )
        except Exception:
            pass


#======================
# BROADCAST MODE
#======================
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ.")
        return

    if not context.args:
        await update.message.reply_text(
            "📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ\n\nᴜꜱᴀɢᴇ: `/ʙʀᴏᴀᴅᴄᴀꜱᴛ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ`",
            parse_mode="Markdown"
        )
        return

    broadcast_msg = " ".join(context.args)

    anim_msg = await context.bot.send_message(
        update.effective_chat.id,
        "📢 ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...\n░░░░░░░░░░ 0%"
    )

    total_users = len(user_projects)
    sent = 0
    failed = 0

    for i, user_id in enumerate(user_projects.keys()):
        try:
            await send_premium_message(
                context, int(user_id),
                "╔═════════════════════╗\n"
                "    📢 ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ     \n"
                "╚═════════════════════╝\n\n"
                f"{broadcast_msg}\n\n"
                "──────────────────────\n"
                "📢 ᴀʟᴇxᴀ ʜᴏꜱᴛɪɴɢ",
                emoji_key="broadcast"
            )
            sent += 1
        except Exception:
            failed += 1

        if total_users > 0:
            percent = int((i + 1) / total_users * 100)
            try:
                await anim_msg.edit_text(
                    f"📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...\n"
                    f"[{premium_progress_bar(percent)}] {percent}%\n"
                    f"✅ ꜱᴇɴᴛ: {sent} | ❌ ꜰᴀɪʟᴇᴅ: {failed}"
                )
            except Exception:
                pass
            await asyncio.sleep(0.1)

    try:
        await anim_msg.edit_text(
            "✅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ!\n\n"
            f"📊 ʀᴇꜱᴜʟᴛꜱ:\n"
            f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ: {sent}\n"
            f"❌ ꜰᴀɪʟᴇᴅ: {failed}"
        )
    except Exception:
        pass


#======================
# OWNER RESET
#======================
async def owner_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    for key in list(active_processes.keys()):
        try:
            active_processes[key].terminate()
        except Exception:
            pass

    active_processes.clear()
    user_projects.clear()
    pending_approvals.clear()
    user_modules.clear()

    import shutil
    if os.path.exists(HOST_DIR):
        shutil.rmtree(HOST_DIR)
    os.makedirs(HOST_DIR, exist_ok=True)

    save_db({"user_projects": {}, "pending_approvals": {}, "user_modules": {}})

    response = (
        "╔═════════════════════╗\n"
        "    🔄 ʀᴇꜱᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇ    \n"
        "╚═════════════════════╝\n\n"
        "✅ ᴀʟʟ ʙᴏᴛꜱ ꜱᴛᴏᴘᴘᴇᴅ\n"
        "✅ ᴀʟʟ ᴅᴀᴛᴀ ᴄʟᴇᴀʀᴇᴅ\n"
        "✅ ᴀʟʟ ꜰɪʟᴇꜱ ᴅᴇʟᴇᴛᴇᴅ\n"
        "✅ ᴘᴇɴᴅɪɴɢ Qᴜᴇᴜᴇ ᴄʟᴇᴀʀᴇᴅ"
    )

    if update.message:
        await send_premium_message(update, update.effective_chat.id, response, emoji_key="success")
    else:
        await edit_premium_message(update.callback_query, response, emoji_key="success")
        await context.bot.send_message(
            update.callback_query.message.chat_id,
            "🔙 ʙᴀᴄᴋ ᴛᴏ ᴏᴡɴᴇʀ ᴍᴇɴᴜ",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")]
            ])
        )


#======================
# OWNER PENDING LIST
#======================
async def owner_pending_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not pending_approvals:
        text = "📂 ɴᴏ ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ."
        if update.message:
            await send_premium_message(update, update.effective_chat.id, text)
        else:
            await edit_premium_message(update.callback_query, text)
        return

    text = "╔═════════════════════╗\n                   📥 ᴘᴇɴᴅɪɴɢ ʀᴇQᴜᴇꜱᴛꜱ  \n╚═════════════════════╝\n\n"

    for msg_id, p_data in pending_approvals.items():
        text += f"👤 ᴜꜱᴇʀ: `{p_data['user_id']}`\n"
        text += f"📄 ꜰɪʟᴇ: `{p_data['filename']}`\n"
        text += "──────────────────────\n"

    if update.message:
        await send_premium_message(update, update.effective_chat.id, text, code_words=list(pending_approvals.keys()))
    else:
        await edit_premium_message(update.callback_query, text)


#======================
# OWNER DELETE USER
#======================
async def owner_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ᴀᴄᴄᴇꜱꜱ ᴅᴇɴɪᴇᴅ.")
        return

    if not context.args:
        await update.message.reply_text(
            "🗑️ ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ\n\nᴜꜱᴀɢᴇ: `/ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ_ɪᴅ`\n\nᴇxᴀᴍᴘʟᴇ: `/ᴅᴇʟᴇᴛᴇ 123456789`",
            parse_mode="Markdown"
        )
        return

    user_id = context.args[0]

    if user_id not in user_projects:
        await update.message.reply_text(f"❌ ᴜꜱᴇʀ `{user_id}` ɴᴏᴛ ꜰᴏᴜɴᴅ.", parse_mode="Markdown")
        return

    for f_name in list(user_projects[user_id].keys()):
        stop_script_process(user_id, f_name)
        file_path = os.path.join(HOST_DIR, str(user_id), f_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    del user_projects[user_id]

    for msg_id, p_data in list(pending_approvals.items()):
        if str(p_data["user_id"]) == user_id:
            del pending_approvals[msg_id]

    save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

    await send_premium_message(
        update, update.effective_chat.id,
        f"🗑️ ᴜꜱᴇʀ ᴅᴇʟᴇᴛᴇᴅ\n\n👤 ᴜꜱᴇʀ ɪᴅ: `{user_id}`\n✅ ᴀʟʟ ʙᴏᴛꜱ ᴅᴇʟᴇᴛᴇᴅ",
        code_words=[user_id]
    )


#======================
# OWNER STATUS
#======================
async def owner_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    total_files = sum(len(proj) for proj in user_projects.values())
    active_files = len([k for k, v in active_processes.items() if v.poll() is None])
    pending = len(pending_approvals)

    text = (
        "╔═════════════════════╗\n"
        "       📊 ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛᴜꜱ     \n"
        "╚═════════════════════╝\n\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {len(user_projects)}\n"
        f"📁 ꜰɪʟᴇꜱ ʜᴏꜱᴛᴇᴅ: {total_files}\n"
        f"⚡ ʀᴜɴɴɪɴɢ: {active_files}\n"
        f"⏳ ᴘᴇɴᴅɪɴɢ: {pending}\n"
        f"🔄 ꜱʏꜱᴛᴇᴍ: {'🟢 ᴏɴʟɪɴᴇ' if GLOBAL_HOSTING_ACTIVE else '🔴 ᴏꜰꜰʟɪɴᴇ'}\n\n"
        f"📊 ᴀᴄᴛɪᴠᴇ ᴘʀᴏᴄᴇꜱꜱᴇꜱ: {len(active_processes)}"
    )

    if update.message:
        await send_premium_message(update, update.effective_chat.id, text)
    else:
        await edit_premium_message(update.callback_query, text)


#======================
# OWNER LOGS
#======================
async def owner_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "📋 ʟᴏɢꜱ\n\nᴜꜱᴀɢᴇ: `/ʟᴏɢ ᴜꜱᴇʀ_ɪᴅ`\n\nᴇxᴀᴍᴘʟᴇ: `/ʟᴏɢ 123456789`",
            parse_mode="Markdown"
        )
        return

    u_id = context.args[0]
    if u_id not in user_projects:
        await update.message.reply_text(f"❌ ᴜꜱᴇʀ `{u_id}` ɴᴏᴛ ꜰᴏᴜɴᴅ.", parse_mode="Markdown")
        return

    user_files = user_projects[u_id]
    f_name = list(user_files.keys())[0]
    log_path = os.path.join(HOST_DIR, str(u_id), f"{f_name}.log")

    if not os.path.exists(log_path):
        await update.message.reply_text("⚠️ ɴᴏ ʟᴏɢꜱ ꜰᴏᴜɴᴅ.")
        return

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_lines = lines[-20:] if len(lines) > 20 else lines
            log_content = "".join(last_lines) if last_lines else "ᴇᴍᴘᴛʏ"

        await update.message.reply_text(
            f"📋 ʟᴏɢꜱ ꜰᴏʀ ᴜꜱᴇʀ `{u_id}`\n\n"
            f"```text\n{log_content[:3000]}\n```",
            parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {e}")


#======================
# OWNER ON/OFF
#======================
async def owner_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    global GLOBAL_HOSTING_ACTIVE
    GLOBAL_HOSTING_ACTIVE = True

    for u_id in list(user_projects.keys()):
        for f_name in user_projects[u_id]:
            if user_projects[u_id][f_name].get("approved"):
                success = start_script_process(u_id, f_name)
                user_projects[u_id][f_name]["status"] = "Running" if success else "Stopped"

    save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

    response = (
        "╔═════════════════════╗\n"
        "    🟢 ʜᴏꜱᴛɪɴɢ ᴏɴ         \n"
        "╚═════════════════════╝\n\n"
        "✅ ʜᴏꜱᴛɪɴɢ ᴇɴᴀʙʟᴇᴅ\n"
        "✅ ᴀʟʟ ʙᴏᴛꜱ ʀᴇꜱᴛᴀʀᴛᴇᴅ"
    )

    if update.callback_query:
        await edit_premium_message(update.callback_query, response, emoji_key="success")
        await context.bot.send_message(
            update.callback_query.message.chat_id,
            "🔙 ʙᴀᴄᴋ ᴛᴏ ᴏᴡɴᴇʀ ᴍᴇɴᴜ",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")]
            ])
        )
    elif update.message:
        await send_premium_message(update, update.effective_chat.id, response, emoji_key="success")


async def owner_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    global GLOBAL_HOSTING_ACTIVE
    GLOBAL_HOSTING_ACTIVE = False

    for u_id in list(user_projects.keys()):
        for f_name in user_projects[u_id]:
            stop_script_process(u_id, f_name)
            user_projects[u_id][f_name]["status"] = "Stopped"

    save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

    response = (
        "╔═════════════════════╗\n"
        "     🔴 ʜᴏꜱᴛɪɴɢ ᴏꜰꜰ        \n"
        "╚═════════════════════╝\n\n"
        "⛔ ʜᴏꜱᴛɪɴɢ ᴅɪꜱᴀʙʟᴇᴅ\n"
        "⛔ ᴀʟʟ ʙᴏᴛꜱ ꜱᴛᴏᴘᴘᴇᴅ"
    )

    if update.callback_query:
        await edit_premium_message(update.callback_query, response, emoji_key="error")
        await context.bot.send_message(
            update.callback_query.message.chat_id,
            "🔙 ʙᴀᴄᴋ ᴛᴏ ᴏᴡɴᴇʀ ᴍᴇɴᴜ",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")]
            ])
        )
    elif update.message:
        await send_premium_message(update, update.effective_chat.id, response, emoji_key="error")


# ============================================================
# TERMINAL HANDLER
# ============================================================
async def terminal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Direct terminal command via /terminal or /sh"""
    user_id = update.effective_user.id
    if not await is_user_joined(user_id, context):
        return

    if not context.args:
        await send_premium_message(
            update, update.effective_chat.id,
            "💻 ᴛᴇʀᴍɪɴᴀʟ\n\n"
            "ᴜꜱᴀɢᴇ:\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ <ᴄᴏᴍᴍᴀɴᴅ>`\n\n"
            "ᴇxᴀᴍᴘʟᴇ:\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ ᴘɪᴘ ɪɴꜱᴛᴀʟʟ ʀᴇQᴜᴇꜱᴛꜱ`\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ ᴘɪᴘ ʟɪꜱᴛ`",
            code_words=["/terminal", "pip install requests", "pip list"]
        )
        return

    command = " ".join(context.args)

    # Animation
    anim_steps = [
        (f"💻 ᴇxᴇᴄᴜᴛɪɴɢ...\n[{premium_progress_bar(30)}] 30%", 0.2),
        (f"💻 ᴘʀᴏᴄᴇꜱꜱɪɴɢ...\n[{premium_progress_bar(60)}] 60%", 0.2),
        (f"💻 ꜰɪɴɪꜱʜɪɴɢ...\n[{premium_progress_bar(90)}] 90%", 0.2),
    ]

    anim_msg = None
    for text, duration in anim_steps:
        final, ents = convert_emojis_to_premium(text)
        if anim_msg is None:
            anim_msg = await context.bot.send_message(
                update.effective_chat.id, final,
                entities=ents if ents else None
            )
        else:
            try:
                await anim_msg.edit_text(final, entities=ents if ents else None)
            except Exception:
                pass
        await asyncio.sleep(duration)

    output, success = await run_terminal_command(user_id, command)

    if anim_msg:
        try:
            await anim_msg.delete()
        except Exception:
            pass

    status_icon = "✅" if success else "❌"
    result_text = (
        f"{status_icon} ᴛᴇʀᴍɪɴᴀʟ ᴏᴜᴛᴘᴜᴛ\n"
        f"┌────────────────────────────\n"
        f"│ ᴄᴏᴍᴍᴀɴᴅ: `{command[:100]}`\n"
        f"└────────────────────────────\n\n"
        f"```text\n{output[:3500]}\n```"
    )

    await send_premium_message(
        update, update.effective_chat.id, result_text,
        emoji_key="success" if success else "error",
        code_words=[command[:100]]
    )


async def install_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Install a module via /install"""
    user_id = update.effective_user.id
    if not await is_user_joined(user_id, context):
        return

    if not context.args:
        await send_premium_message(
            update, update.effective_chat.id,
            "📦 ɪɴꜱᴛᴀʟʟ ᴍᴏᴅᴜʟᴇ\n\n"
            "ᴜꜱᴀɢᴇ:\n"
            "`/ɪɴꜱᴛᴀʟʟ <ᴍᴏᴅᴜʟᴇ_ɴᴀᴍᴇ>`\n\n"
            "ᴇxᴀᴍᴘʟᴇ:\n"
            "`/ɪɴꜱᴛᴀʟʟ ʀᴇQᴜᴇꜱᴛꜱ`\n"
            "`/ɪɴꜱᴛᴀʟʟ ᴘʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ`",
            code_words=["/install", "requests", "python-telegram-bot"]
        )
        return

    module_name = context.args[0]

    anim_steps = [
        (f"📦 ɪɴꜱᴛᴀʟʟɪɴɢ {module_name}...\n[{premium_progress_bar(20)}] 20%", 0.2),
        (f"📦 ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘᴀᴄᴋᴀɢᴇ...\n[{premium_progress_bar(50)}] 50%", 0.2),
        (f"📦 ɪɴꜱᴛᴀʟʟɪɴɢ ᴅᴇᴘᴇɴᴅᴇɴᴄɪᴇꜱ...\n[{premium_progress_bar(80)}] 80%", 0.2),
    ]

    anim_msg = None
    for text, duration in anim_steps:
        final, ents = convert_emojis_to_premium(text)
        if anim_msg is None:
            anim_msg = await context.bot.send_message(
                update.effective_chat.id, final,
                entities=ents if ents else None
            )
        else:
            try:
                await anim_msg.edit_text(final, entities=ents if ents else None)
            except Exception:
                pass
        await asyncio.sleep(duration)

    output, success = await install_module(user_id, module_name)

    if anim_msg:
        try:
            await anim_msg.delete()
        except Exception:
            pass

    if success:
        # Save installed module
        if str(user_id) not in user_modules:
            user_modules[str(user_id)] = []
        if module_name not in user_modules[str(user_id)]:
            user_modules[str(user_id)].append(module_name)
        save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

        result_text = (
            "✅ ᴍᴏᴅᴜʟᴇ ɪɴꜱᴛᴀʟʟᴇᴅ\n\n"
            f"📦 ᴍᴏᴅᴜʟᴇ: `{module_name}`\n"
            f"```text\n{output[:3000]}\n```"
        )
    else:
        result_text = (
            "❌ ɪɴꜱᴛᴀʟʟᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ\n\n"
            f"📦 ᴍᴏᴅᴜʟᴇ: `{module_name}`\n"
            f"```text\n{output[:3000]}\n```"
        )

    await send_premium_message(
        update, update.effective_chat.id, result_text,
        emoji_key="success" if success else "error",
        code_words=[module_name]
    )


#======================
# MENU CALLBACK HANDLER
#======================
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()

    if query.data == "check_join":
        if await is_user_joined(int(user_id), context):
            try:
                await query.edit_message_text("✅ ᴊᴏɪɴᴇᴅ! ᴡᴇʟᴄᴏᴍᴇ.")
            except Exception:
                pass
            await context.bot.send_message(int(user_id), "/start")
        else:
            await query.answer("⚠️ ᴘʟᴇᴀꜱᴇ ᴊᴏɪɴ ᴀʟʟ 5 ᴄʜᴀɴɴᴇʟꜱ ꜰɪʀꜱᴛ!", show_alert=True)
        return

    if query.data == "owner_menu":
        await send_owner_menu(update, context, edit=True)
        return

    if query.data == "owner_on":
        await owner_on(update, context)
        return

    if query.data == "owner_off":
        await owner_off(update, context)
        return

    if query.data == "owner_reset":
        await owner_reset(update, context)
        return

    if query.data == "owner_pending":
        await owner_pending_list(update, context)
        return

    if query.data == "owner_logs":
        await edit_premium_message(
            query,
            "📋 ʟᴏɢꜱ\n\nᴜꜱᴇ `/ʟᴏɢ ᴜꜱᴇʀ_ɪᴅ` ᴛᴏ ᴠɪᴇᴡ ʟᴏɢꜱ"
        )
        return

    if query.data == "owner_delete":
        await edit_premium_message(
            query,
            "🗑️ ᴅᴇʟᴇᴛᴇ\n\nᴜꜱᴇ `/ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ_ɪᴅ` ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜꜱᴇʀ"
        )
        return

    if query.data == "owner_status":
        await owner_status(update, context)
        return

    if query.data == "owner_broadcast":
        await edit_premium_message(
            query,
            "📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ\n\nᴜꜱᴇ `/ʙʀᴏᴀᴅᴄᴀꜱᴛ ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ` ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ"
        )
        return

    if query.data == "menu_terminal":
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]]
        if int(user_id) == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await edit_premium_message(
            query,
            "╔═════════════════════╗\n"
            "      💻 ᴛᴇʀᴍɪɴᴀʟ         \n"
            "╚═════════════════════╝\n\n"
            "📌 ᴛᴇʀᴍɪɴᴀʟ ᴄᴏᴍᴍᴀɴᴅꜱ:\n\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ <ᴄᴍᴅ>`\n"
            "→ ʀᴜɴ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ\n\n"
            "`/ɪɴꜱᴛᴀʟʟ <ᴍᴏᴅᴜʟᴇ>`\n"
            "→ ɪɴꜱᴛᴀʟʟ ᴘʏᴛʜᴏɴ ᴍᴏᴅᴜʟᴇ\n\n"
            "📝 ᴇxᴀᴍᴘʟᴇꜱ:\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ ᴘɪᴘ ʟɪꜱᴛ`\n"
            "`/ɪɴꜱᴛᴀʟʟ ʀᴇQᴜᴇꜱᴛꜱ`\n"
            "`/ᴛᴇʀᴍɪɴᴀʟ ʟꜱ`",
            code_words=["/terminal", "/install", "pip list", "requests", "ls"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if query.data == "menu_mybots":
        files = user_projects.get(user_id, {})
        if not files:
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]]
            if int(user_id) == OWNER_ID:
                keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

            await edit_premium_message(
                query,
                "╔═════════════════════╗\n"
                "      📁 ᴍʏ ʙᴏᴛꜱ        \n"
                "╚═════════════════════╝\n\n"
                "📂 ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ ʙᴏᴛꜱ ʏᴇᴛ.\n\n"
                "📤 ᴜᴘʟᴏᴀᴅ ᴀ `.ᴘʏ` ꜰɪʟᴇ ᴛᴏ ꜱᴛᴀʀᴛ.",
                code_words=[".py"],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        await query.delete_message()

        for f_name, details in files.items():
            key = f"{user_id}_{f_name}"
            is_alive = key in active_processes and active_processes[key].poll() is None
            display_name = f_name.replace('.py', '').replace('_', ' ').title()

            status_icon = "🟢" if is_alive else "🔴"
            status_text = "ʀᴜɴɴɪɴɢ" if is_alive else "ꜱᴛᴏᴘᴘᴇᴅ"

            bot_card = (
                "╔═════════════════════╗\n"
                f"     🤖 {display_name[:20]}       \n"
                "╚═════════════════════╝\n\n"
                f"{status_icon} ꜱᴛᴀᴛᴜꜱ: {status_text}\n"
                f"📄 ꜰɪʟᴇ: `{f_name}`\n\n"
                "⚡ ᴀᴄᴛɪᴏɴꜱ:"
            )

            buttons = [
                [
                    InlineKeyboardButton(
                        "🛑 ꜱᴛᴏᴘ" if is_alive else "▶️ ꜱᴛᴀʀᴛ",
                        callback_data=f"toggle_{f_name}"
                    ),
                    InlineKeyboardButton("📋 ʟᴏɢꜱ", callback_data=f"logs_{f_name}")
                ],
                [
                    InlineKeyboardButton("🗑️ ᴅᴇʟᴇᴛᴇ", callback_data=f"delete_{f_name}")
                ]
            ]

            await send_premium_message(
                context, query.message.chat_id, bot_card,
                reply_markup=InlineKeyboardMarkup(buttons),
                code_words=[f_name]
            )

        back_keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data="menu_back")]]
        if int(user_id) == OWNER_ID:
            back_keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await context.bot.send_message(
            query.message.chat_id,
            "⬅️ ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ",
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )

    elif query.data == "menu_upload":
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]]
        if int(user_id) == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await edit_premium_message(
            query,
            "╔═════════════════════╗\n"
            "      📤 ᴜᴘʟᴏᴀᴅ ʙᴏᴛ       \n"
            "╚═════════════════════╝\n\n"
            "📤 ʜᴏᴡ ᴛᴏ ᴜᴘʟᴏᴀᴅ:\n\n"
            "1️⃣ ꜱᴇɴᴅ ᴀ `.ᴘʏ` ꜰɪʟᴇ\n"
            "2️⃣ ᴡᴀɪᴛ ꜰᴏʀ ᴀᴘᴘʀᴏᴠᴀʟ\n"
            "3️⃣ ʏᴏᴜʀ ʙᴏᴛ ꜱᴛᴀʀᴛꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ\n\n"
            "📦 ᴍᴀx ꜱɪᴢᴇ: ᴜᴘ ᴛᴏ 3.8+\n\n"
            "🔙 ʀᴇᴛᴜʀɴ ᴛᴏ ᴍᴇɴᴜ ᴛᴏ ᴜᴘʟᴏᴀᴅ",
            code_words=[".py"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "menu_status":
        total_files = sum(len(proj) for proj in user_projects.values())
        active_files = len([k for k, v in active_processes.items() if v.poll() is None])
        pending = len(pending_approvals)

        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]]
        if int(user_id) == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await edit_premium_message(
            query,
            "╔═════════════════════╗\n"
            "      📊 ʟɪᴠᴇ ꜱᴛᴀᴛᴜꜱ      \n"
            "╚═════════════════════╝\n\n"
            f"👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: {len(user_projects)}\n"
            f"📁 ꜰɪʟᴇꜱ ʜᴏꜱᴛᴇᴅ: {total_files}\n"
            f"⚡ ʀᴜɴɴɪɴɢ: {active_files}\n"
            f"⏳ ᴘᴇɴᴅɪɴɢ: {pending}\n"
            f"🔄 ꜱʏꜱᴛᴇᴍ: {'🟢 ᴏɴʟɪɴᴇ' if GLOBAL_HOSTING_ACTIVE else '🔴 ᴏꜰꜰʟɪɴᴇ'}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "menu_contact":
        keyboard = [
            [InlineKeyboardButton("💬 ᴊᴏɪɴ ɢʀᴏᴜᴘ", url=GROUP_LINK)],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]
        ]
        if int(user_id) == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await edit_premium_message(
            query,
            "╔═════════════════════╗\n"
            "   📞 ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ     \n"
            "╚═════════════════════╝\n\n"
            "👤 ᴏᴡɴᴇʀ: @yoursssrehan\n"
            f"💬 ɢʀᴏᴜᴘ: {GROUP_LINK}\n"
            f"📢 ᴄʜᴀɴɴᴇʟ: {CHANNEL_LINK}\n\n"
            "✉️ ꜰᴏʀ ꜱᴜᴘᴘᴏʀᴛ:\n"
            "• ᴅᴍ ᴏᴡɴᴇʀ ᴅɪʀᴇᴄᴛʟʏ\n"
            "• ᴊᴏɪɴ ɢʀᴏᴜᴘ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "menu_help":
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_back")]]
        if int(user_id) == OWNER_ID:
            keyboard.append([InlineKeyboardButton("👑 ᴀʟᴇxᴀ ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", callback_data="owner_menu")])

        await edit_premium_message(
            query,
            "╔═════════════════════╗\n"
            "         ❓ ʜᴇʟᴘ & ꜱᴜᴘᴘᴏʀᴛ            \n"
            "╚═════════════════════╝\n\n"
            "📚 ʜᴏᴡ ᴛᴏ ᴜꜱᴇ:\n"
            "1️⃣ ꜱᴇɴᴅ ᴀ `.ᴘʏ` ꜰɪʟᴇ\n"
            "2️⃣ ᴡᴀɪᴛ ꜰᴏʀ ᴀᴘᴘʀᴏᴠᴀʟ\n"
            "3️⃣ ʏᴏᴜʀ ʙᴏᴛ ꜱᴛᴀʀᴛꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ\n\n"
            "⚡ ᴄᴏᴍᴍᴀɴᴅꜱ:\n"
            "• `/ꜱᴛᴀʀᴛ` - ᴍᴀɪɴ ᴍᴇɴᴜ\n"
            "• `/ᴛᴇʀᴍɪɴᴀʟ <ᴄᴍᴅ>` - ʀᴜɴ ᴄᴏᴍᴍᴀɴᴅ\n"
            "• `/ɪɴꜱᴛᴀʟʟ <ᴍᴏᴅᴜʟᴇ>` - ɪɴꜱᴛᴀʟʟ ᴘᴀᴄᴋᴀɢᴇ\n\n"
            f"📢 ᴄʜᴀɴɴᴇʟ: {GROUP_LINK}\n"
            f"💬 ꜱᴜᴘᴘᴏʀᴛ: {GROUP_LINK}",
            code_words=["/start", "/terminal", "/install"],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "menu_back":
        await send_user_menu(update, context, edit=True)
        return


#======================
# BUTTON CALLBACK
#======================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()

    if query.data.startswith("approve_") or query.data.startswith("reject_"):
        await owner_approve_reject(update, context)
        return

    if query.data.startswith("menu_") or query.data == "check_join" or query.data.startswith("owner_"):
        await menu_callback(update, context)
        return

    if query.data.startswith("logs_"):
        f_name = query.data.replace("logs_", "")
        if user_id in user_projects and f_name in user_projects[user_id]:
            log_path = os.path.join(HOST_DIR, user_id, f"{f_name}.log")
            if os.path.exists(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        last_lines = lines[-20:] if len(lines) > 20 else lines
                        log_content = "".join(last_lines) if last_lines else "ɴᴏ ʟᴏɢꜱ ʏᴇᴛ."

                    display_name = f_name.replace('.py', '').replace('_', ' ').title()
                    await edit_premium_message(
                        query,
                        "╔═════════════════════╗\n"
                        f"     📋 ʟᴏɢꜱ: {display_name[:15]}         \n"
                        "╚═════════════════════╝\n\n"
                        f"```text\n{log_content[:3000]}\n```",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                        ]),
                        code_words=[]
                    )
                except Exception as e:
                    await edit_premium_message(
                        query,
                        f"❌ ᴇʀʀᴏʀ: {e}",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                        ])
                    )
            else:
                await edit_premium_message(
                    query,
                    "⚠️ ɴᴏ ʟᴏɢꜱ ꜰᴏᴜɴᴅ.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                    ])
                )
        return

    if query.data.startswith("toggle_"):
        f_name = query.data.replace("toggle_", "")
        if user_id in user_projects and f_name in user_projects[user_id]:
            display_name = f_name.replace('.py', '').replace('_', ' ').title()
            key = f"{user_id}_{f_name}"
            if key in active_processes and active_processes[key].poll() is None:
                stop_script_process(user_id, f_name)
                await edit_premium_message(
                    query,
                    f"🛑 `{display_name}` ꜱᴛᴏᴘᴘᴇᴅ.",
                    code_words=[display_name],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                    ])
                )
            else:
                if not GLOBAL_HOSTING_ACTIVE:
                    await edit_premium_message(
                        query,
                        "⚠️ ʜᴏꜱᴛɪɴɢ ɪꜱ ᴏꜰꜰ.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                        ])
                    )
                    return
                start_script_process(user_id, f_name)
                await edit_premium_message(
                    query,
                    f"🚀 `{display_name}` ɪꜱ ɴᴏᴡ ʀᴜɴɴɪɴɢ.",
                    code_words=[display_name],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                    ])
                )
            save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})

    elif query.data.startswith("delete_"):
        f_name = query.data.replace("delete_", "")
        if user_id in user_projects and f_name in user_projects[user_id]:
            display_name = f_name.replace('.py', '').replace('_', ' ').title()
            stop_script_process(user_id, f_name)
            file_path = os.path.join(HOST_DIR, user_id, f_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            del user_projects[user_id][f_name]
            save_db({"user_projects": user_projects, "pending_approvals": pending_approvals, "user_modules": user_modules})
            await edit_premium_message(
                query,
                f"🗑️ `{display_name}` ᴅᴇʟᴇᴛᴇᴅ.",
                code_words=[display_name],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="menu_mybots")]
                ])
            )


#======================
# MAIN
#======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    auto_recover_scripts()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("delete", owner_delete_user))
    app.add_handler(CommandHandler("log", owner_logs))
    app.add_handler(CommandHandler("terminal", terminal_command))
    app.add_handler(CommandHandler("sh", terminal_command))
    app.add_handler(CommandHandler("install", install_command))
    app.add_handler(CommandHandler("pip", install_command))

    # Document handler
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Callback handler
    app.add_handler(CallbackQueryHandler(button_callback))

    print(f"🚀 {BOT_NAME} ʜᴏꜱᴛɪɴɢ ʙᴏᴛ ɪꜱ ʀᴜɴɴɪɴɢ...")
    app.run_polling()


if __name__ == "__main__":
    main()