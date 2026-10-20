# -*- coding: utf-8 -*-
import telebot
import subprocess
import os
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import sys
import atexit
import requests
import random

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread

app = Flask('')
NAME = 'Alexa'

@app.route('/')
def home():
    return f"I am {NAME} BOT"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")

# --- Configuration ---
TOKEN = '8487451759:AAG6V7MHZsMjNidwN_q7sEbZm3MhgJfhY4w'
OWNER_ID = 7766306643
ADMIN_ID = 7766306643
ADMIN_IDS = [7766306643, 7766306643]
YOUR_USERNAME = '@a3lxe'
UPDATE_CHANNEL = '@a4lxe'
UPDATE_CHANNEL_2 = '@PROXYDOMINATES'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

FREE_USER_LIMIT = 4
SUBSCRIBED_USER_LIMIT = 29
ADMIN_LIMIT = 9999999
OWNER_LIMIT = float('inf')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

bot = telebot.TeleBot(TOKEN)

bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = set(ADMIN_IDS)
banned_users = set()
user_limits = {}
bot_locked = False

pending_modules = {}
manual_install_requests = {}
mandatory_channels = {}
pending_zip_files = {}

SECURITY_CONFIG = {
    'blocked_modules': ['os.system', 'os', 'zipfile', 'subprocess.Popen', 'subprocess', 'eval', 'exec','compile', '__import__'],
    'max_file_size': 20 * 1024 * 1024,
    'max_script_runtime': 3600,
    'allowed_extensions': ['.py', '.js'],
    'blocked_imports': ['shutil.rmtree', 'subprocess','os.remove', 'os.unlink']
}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================
# PREMIUM EMOJI SYSTEM (HTML tg-emoji - WORKING METHOD)
# ============================================================
PREMIUM_EMOJI_IDS = [
    "5368324170671202286",  # 👍
    "5368581702575891023",  # ❤️
    "5368755911315654597",  # 🔥
    "5368530611856994392",  # ⭐
    "5368536262073301337",  # ✨
    "5368622426541425573",  # ✅
    "5368674576327570227",  # ❌
    "5368802797203387526",  # 🚀
    "5368794956902084172",  # 🎉
    "5368752721785399951",  # 💯
    "5368769103435260747",  # 😎
    "5368749486428674771",  # 💪
    "5368609209499517685",  # 🌟
    "5368682684110305997",  # 💎
    "5368699898353509729",  # 👑
    "5368776870617042818",  # 🔔
    "5368761207687035830",  # 📌
    "5368780358274942474",  # 🎯
    "5368708730783801480",  # 💡
    "5368738230844304522",  # ⚡
]

# Emoji-key specific premium IDs for UI elements
UI_EMOJI_IDS = {
    "success": "5368622426541425573",
    "error": "5368674576327570227",
    "broadcast": "5368776870617042818",
    "status": "5368780358274942474",
    "welcome": "5368536262073301337",
    "upload": "5368802797203387526",
    "premium": "5368536262073301337",
    "star": "5368530611856994392",
    "fire": "5368755911315654597",
    "heart": "5368581702575891023",
    "rocket": "5368802797203387526",
    "crown": "5368699898353509729",
    "check": "5368622426541425573",
    "cross": "5368674576327570227",
    "sparkles": "5368536262073301337",
    "lightning": "5368738230844304522",
    "diamond": "5368682684110305997",
    "bell": "5368776870617042818",
    "idea": "5368708730783801480",
    "party": "5368794956902084172",
}

# Regex for emoji detection
EMOJI_REGEX = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport & Map
    "\U0001F700-\U0001F77F"  # Alchemical
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\u2600-\u26FF"          # Misc Symbols
    "\u2700-\u27BF"          # Dingbats
    "\u2B00-\u2BFF"          # Misc Symbols and Arrows
    "\u203C\u2049\u2122\u2139"
    "\u2194-\u2199\u21A9-\u21AA"
    "\u231A-\u231B\u2328\u23CF"
    "\u23E9-\u23F3\u23F8-\u23FA"
    "\u24C2\u25AA-\u25AB\u25B6"
    "\u25C0\u25FB-\u25FE"
    "\u2934-\u2935\u2B05-\u2B07"
    "\u3030\u303D\u3297\u3299"
    "\u00A9\u00AE"
    "\u20E3"
    "\uFE0F"
    "\u200D"
    "]+",
    flags=re.UNICODE
)


def _escape_html(text: str) -> str:
    """HTML special characters escape karta hai."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def convert_emojis_to_premium_html(text: str, use_emoji_key: str = None) -> str:
    """
    Text ke emojis ko premium HTML `<tg-emoji>` tags me convert karta hai.
    Returns HTML-safe string with premium emoji tags.
    """
    # HTML escape first
    escaped_text = _escape_html(text)

    def replace_emoji(match):
        emoji_char = match.group(0)
        # Agar emoji_key diya hai to wahi ID use karo, warna random
        emoji_id = UI_EMOJI_IDS.get(use_emoji_key) if use_emoji_key else None
        if not emoji_id:
            emoji_id = random.choice(PREMIUM_EMOJI_IDS)
        return f'<tg-emoji emoji-id="{emoji_id}">{emoji_char}</tg-emoji>'

    return EMOJI_REGEX.sub(replace_emoji, escaped_text)


def premium_send(chat_id, text, reply_markup=None, emoji_key=None, bold=False,
                 code_words=None, disable_preview=True):
    """
    Premium emojis ke saath message bhejta hai.
    emoji_key → sirf pehle emoji ko us specific premium emoji se replace karta hai
    """
    html_text = _escape_html(text)

    # First emoji ko specific emoji_key se replace karo
    if emoji_key and emoji_key in UI_EMOJI_IDS:
        emoji_id = UI_EMOJI_IDS[emoji_key]
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{emoji_id}">{m.group(0)}</tg-emoji>',
            html_text, count=1
        )
        # Baaki emojis ko random premium me convert karo
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{random.choice(PREMIUM_EMOJI_IDS)}">{m.group(0)}</tg-emoji>',
            html_text
        )
    else:
        # Sab emojis ko random premium me convert karo
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{random.choice(PREMIUM_EMOJI_IDS)}">{m.group(0)}</tg-emoji>',
            html_text
        )

    # Bold wrap
    if bold:
        html_text = f"<b>{html_text}</b>"

    # Code words replace (careful: code_words must be original text, not escaped)
    if code_words:
        for word in code_words:
            escaped_word = _escape_html(str(word))
            html_text = html_text.replace(
                escaped_word,
                f"<code>{escaped_word}</code>"
            )

    try:
        return bot.send_message(
            chat_id,
            html_text,
            parse_mode='HTML',
            reply_markup=reply_markup,
            disable_web_page_preview=disable_preview
        )
    except Exception as e:
        logger.error(f"premium_send error: {e}")
        # Fallback: plain text without premium emojis
        try:
            return bot.send_message(chat_id, text, reply_markup=reply_markup)
        except Exception as e2:
            logger.error(f"Fallback send error: {e2}")
            return None


def premium_edit(chat_id, message_id, text, reply_markup=None, emoji_key=None,
                 bold=False, code_words=None, disable_preview=True):
    """Premium emojis ke saath message edit karta hai."""
    html_text = _escape_html(text)

    if emoji_key and emoji_key in UI_EMOJI_IDS:
        emoji_id = UI_EMOJI_IDS[emoji_key]
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{emoji_id}">{m.group(0)}</tg-emoji>',
            html_text, count=1
        )
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{random.choice(PREMIUM_EMOJI_IDS)}">{m.group(0)}</tg-emoji>',
            html_text
        )
    else:
        html_text = EMOJI_REGEX.sub(
            lambda m: f'<tg-emoji emoji-id="{random.choice(PREMIUM_EMOJI_IDS)}">{m.group(0)}</tg-emoji>',
            html_text
        )

    if bold:
        html_text = f"<b>{html_text}</b>"

    if code_words:
        for word in code_words:
            escaped_word = _escape_html(str(word))
            html_text = html_text.replace(
                escaped_word,
                f"<code>{escaped_word}</code>"
            )

    try:
        return bot.edit_message_text(
            html_text,
            chat_id,
            message_id,
            parse_mode='HTML',
            reply_markup=reply_markup,
            disable_web_page_preview=disable_preview
        )
    except Exception as e:
        if "message is not modified" in str(e).lower():
            return None
        logger.error(f"premium_edit error: {e}")
        try:
            return bot.edit_message_text(text, chat_id, message_id, reply_markup=reply_markup)
        except Exception:
            return None


def premium_reply(message, text, reply_markup=None, emoji_key=None, bold=False,
                  code_words=None, disable_preview=True):
    """Reply to a message with premium emojis."""
    return premium_send(
        message.chat.id, text,
        reply_markup=reply_markup, emoji_key=emoji_key, bold=bold,
        code_words=code_words, disable_preview=disable_preview
    )


# ============================================================
# BUTTON LAYOUTS
# ============================================================
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["📞 Support"],
    ["📦 Manual Install", "🆘 Help"]
]

ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["👑 Admin Panel", "📞 Support"],
    ["📢 Channel Add", "🛠️ Manual Install"],
    ["👥 User Management", "⚙️ Settings"]
]


# ============================================================
# DATABASE
# ============================================================
def init_db():
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY, join_date TEXT, last_seen TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY, added_by INTEGER, added_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS banned_users
                     (user_id INTEGER PRIMARY KEY, reason TEXT, banned_by INTEGER, ban_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_limits
                     (user_id INTEGER PRIMARY KEY, file_limit INTEGER, set_by INTEGER, set_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS mandatory_channels
                     (channel_id TEXT PRIMARY KEY,
                      channel_username TEXT,
                      channel_name TEXT,
                      added_by INTEGER,
                      added_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS install_logs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      module_name TEXT,
                      package_name TEXT,
                      status TEXT,
                      log TEXT,
                      install_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_files
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      file_name TEXT,
                      file_content BLOB,
                      file_type TEXT,
                      upload_date TEXT,
                      status TEXT DEFAULT 'pending')''')

        for admin_id in ADMIN_IDS:
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)',
                      (admin_id, OWNER_ID, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)


def load_data():
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        c.execute('SELECT user_id, expiry FROM subscriptions')
        for user_id, expiry in c.fetchall():
            try:
                user_subscriptions[user_id] = {'expiry': datetime.fromisoformat(expiry)}
            except ValueError:
                logger.warning(f"⚠️ Invalid expiry for user {user_id}: {expiry}. Skipping.")

        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        for admin_id in ADMIN_IDS:
            admin_ids.add(admin_id)

        c.execute('SELECT user_id FROM banned_users')
        banned_users.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT user_id, file_limit FROM user_limits')
        for user_id, file_limit in c.fetchall():
            user_limits[user_id] = file_limit

        c.execute('SELECT channel_id, channel_username, channel_name FROM mandatory_channels')
        for channel_id, channel_username, channel_name in c.fetchall():
            mandatory_channels[channel_id] = {
                'username': channel_username,
                'name': channel_name
            }

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subs, {len(admin_ids)} admins, {len(banned_users)} banned, {len(user_limits)} custom limits, {len(mandatory_channels)} channels.")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)


init_db()
load_data()

DB_LOCK = threading.Lock()

# ================= AUTO VERSION DETECTION =================

def detect_telegram_version(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if re.search(r'from telegram\.ext import (Updater|Dispatcher)', content):
            return '13.15'
        if re.search(r'updater\.start_polling', content) and 'dispatcher' in content:
            return '13.15'
        if 'telegram.ext.Updater' in content:
            return '13.15'
        if re.search(r'from telegram\.ext import Application', content):
            return '20.7'
        if 'ContextTypes' in content:
            return '20.7'
        if 'Application.builder' in content:
            return '20.7'
        return '20.7'
    except:
        return '20.7'


def get_python_for_version(version):
    if version == '13.15':
        for py in ['/usr/bin/python3.10', 'python3.10', '/usr/bin/python3.11', 'python3.11']:
            try:
                result = subprocess.run([py, '--version'], capture_output=True, timeout=2)
                if result.returncode == 0:
                    return py
            except:
                continue
        return sys.executable
    return sys.executable


def check_code_security(file_path, file_type):
    return True, "File sent to admin for review"


def scan_zip_security(zip_path):
    return True, "Archive sent to admin for review"


def is_user_member(user_id, channel_id):
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking member {user_id} in {channel_id}: {e}")
        return False


def check_mandatory_subscription(user_id):
    if not mandatory_channels:
        return True, []
    not_joined = []
    for channel_id, channel_info in mandatory_channels.items():
        if not is_user_member(user_id, channel_id):
            not_joined.append((channel_id, channel_info))
    if not_joined:
        return False, not_joined
    return True, []


def save_mandatory_channel(channel_id, channel_username, channel_name, added_by):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            added_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO mandatory_channels (channel_id, channel_username, channel_name, added_by, added_date) VALUES (?, ?, ?, ?, ?)',
                      (channel_id, channel_username, channel_name, added_by, added_date))
            conn.commit()
            mandatory_channels[channel_id] = {'username': channel_username, 'name': channel_name}
            logger.info(f"Saved channel: {channel_name} ({channel_id})")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving channel: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def remove_mandatory_channel_db(channel_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM mandatory_channels WHERE channel_id = ?', (channel_id,))
            conn.commit()
            if channel_id in mandatory_channels:
                del mandatory_channels[channel_id]
            return True
        except Exception as e:
            logger.error(f"❌ Error removing channel: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def create_mandatory_channels_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Channel', callback_data='add_mandatory_channel'),
        types.InlineKeyboardButton('➖ Remove Channel', callback_data='remove_mandatory_channel')
    )
    markup.row(types.InlineKeyboardButton('📋 List Channels', callback_data='list_mandatory_channels'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup


def create_subscription_check_message(not_joined_channels):
    message = "📢 **Important: Join Our Channels First:**\n\n"
    markup = types.InlineKeyboardMarkup()
    for channel_id, channel_info in not_joined_channels:
        channel_username = channel_info.get('username', '')
        channel_name = channel_info.get('name', 'Channel')
        if channel_username:
            channel_link = f"https://t.me/{channel_username.replace('@', '')}"
        else:
            channel_link = f"https://t.me/c/{channel_id.replace('-100', '')}"
        message += f"• {channel_name}\n"
        markup.add(types.InlineKeyboardButton(f"Join {channel_name}", url=channel_link))
    markup.add(types.InlineKeyboardButton("✅ Verify Subscription", callback_data='check_subscription_status'))
    return message, markup


def is_user_banned(user_id):
    return user_id in banned_users


def ban_user_db(user_id, reason, banned_by):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            ban_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO banned_users (user_id, reason, banned_by, ban_date) VALUES (?, ?, ?, ?)',
                      (user_id, reason, banned_by, ban_date))
            conn.commit()
            banned_users.add(user_id)
            return True
        except Exception as e:
            logger.error(f"❌ Error banning: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def unban_user_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
            conn.commit()
            banned_users.discard(user_id)
            return True
        except Exception as e:
            logger.error(f"❌ Error unbanning: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def set_user_limit_db(user_id, limit, set_by):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            set_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO user_limits (user_id, file_limit, set_by, set_date) VALUES (?, ?, ?, ?)',
                      (user_id, limit, set_by, set_date))
            conn.commit()
            user_limits[user_id] = limit
            return True
        except Exception as e:
            logger.error(f"❌ Error setting limit: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def remove_user_limit_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_limits WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_limits:
                del user_limits[user_id]
            return True
        except Exception as e:
            logger.error(f"❌ Error removing limit: {e}", exc_info=True)
            return False
        finally:
            conn.close()


def get_user_folder(user_id):
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


def get_user_file_limit(user_id):
    if user_id == OWNER_ID:
        return OWNER_LIMIT
    if user_id in admin_ids:
        return ADMIN_LIMIT
    if user_id in user_limits:
        return user_limits[user_id]
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return SUBSCRIBED_USER_LIMIT
    return FREE_USER_LIMIT


def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))


def is_bot_running(script_owner_id, file_name):
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception:
                        pass
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                    script_info['log_file'].close()
                except Exception:
                    pass
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Error checking process {script_key}: {e}")
            return False
    return False


def kill_process_tree(process_info):
    pid = None
    log_file_closed = False
    script_key = process_info.get('script_key', 'N/A')

    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
                log_file_closed = True
            except Exception as e:
                logger.error(f"Error closing log file {script_key}: {e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    for child in children:
                        try:
                            child.terminate()
                        except Exception:
                            try:
                                child.kill()
                            except Exception:
                                pass
                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        try:
                            p.kill()
                        except Exception:
                            pass
                    try:
                        parent.terminate()
                        try:
                            parent.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            parent.kill()
                    except psutil.NoSuchProcess:
                        pass
                    except Exception:
                        try:
                            parent.kill()
                        except Exception:
                            pass
                except psutil.NoSuchProcess:
                    pass
    except Exception as e:
        logger.error(f"❌ Error killing process {pid}: {e}", exc_info=True)


TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'telethon.sync': 'telethon',
    'telepot': 'telepot',
    'pytg': 'pytg',
    'tgcrypto': 'tgcrypto',
    'telegram_upload': 'telegram-upload',
    'telegram_send': 'telegram-send',
    'telegram_text': 'telegram-text',
    'mtproto': 'telegram-mtproto',
    'tl': 'telethon',
    'telegram_utils': 'telegram-utils',
    'telegram_logger': 'telegram-logger',
    'telegram_handlers': 'python-telegram-handlers',
    'telegram_redis': 'telegram-redis',
    'telegram_sqlalchemy': 'telegram-sqlalchemy',
    'telegram_payment': 'telegram-payment',
    'telegram_shop': 'telegram-shop-sdk',
    'pytest_telegram': 'pytest-telegram',
    'telegram_debug': 'telegram-debug',
    'telegram_scraper': 'telegram-scraper',
    'telegram_analytics': 'telegram-analytics',
    'telegram_nlp': 'telegram-nlp-toogit',
    'telegram_ai': 'telegram-ai',
    'telegram_api': 'telegram-api-client',
    'telegram_web': 'telegram-web-integration',
    'telegram_games': 'telegram-games',
    'telegram_quiz': 'telegram-quiz-bot',
    'telegram_ffmpeg': 'telegram-ffmpeg',
    'telegram_media': 'telegram-media-utils',
    'telegram_2fa': 'telegram-twofa',
    'telegram_crypto': 'telegram-crypto-bot',
    'telegram_i18n': 'telegram-i18n',
    'telegram_translate': 'telegram-translate',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'Flask',
    'django': 'Django',
    'sqlalchemy': 'SQLAlchemy',
    'asyncio': None, 'json': None, 'datetime': None, 'os': None, 'sys': None,
    're': None, 'time': None, 'math': None, 'random': None, 'logging': None,
    'threading': None, 'subprocess': None, 'zipfile': None, 'tempfile': None,
    'shutil': None, 'sqlite3': None, 'psutil': 'psutil', 'atexit': None
}


def save_install_log(user_id, module_name, package_name, status, log):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            install_date = datetime.now().isoformat()
            c.execute('INSERT INTO install_logs (user_id, module_name, package_name, status, log, install_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, module_name, package_name, status, log, install_date))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error saving install log: {e}")
        finally:
            conn.close()


def save_pending_file(user_id, file_name, file_content, file_type):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            upload_date = datetime.now().isoformat()
            c.execute('INSERT INTO pending_files (user_id, file_name, file_content, file_type, upload_date, status) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, file_name, file_content, file_type, upload_date, 'pending'))
            conn.commit()
            return c.lastrowid
        except Exception as e:
            logger.error(f"❌ Error saving pending file: {e}", exc_info=True)
            return None
        finally:
            conn.close()


def get_pending_file(pending_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('SELECT user_id, file_name, file_content, file_type, status FROM pending_files WHERE id = ?', (pending_id,))
            result = c.fetchone()
            if result:
                return {
                    'user_id': result[0], 'file_name': result[1],
                    'file_content': result[2], 'file_type': result[3], 'status': result[4]
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error getting pending file: {e}")
            return None
        finally:
            conn.close()


def delete_pending_file(pending_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM pending_files WHERE id = ?', (pending_id,))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting pending file: {e}")
            return False
        finally:
            conn.close()


def get_pending_files_for_admin():
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('SELECT id, user_id, file_name, file_type, upload_date FROM pending_files WHERE status = "pending" ORDER BY upload_date DESC')
            return c.fetchall()
        except Exception as e:
            logger.error(f"❌ Error getting pending files: {e}")
            return []
        finally:
            conn.close()


def attempt_install_pip(module_name, message, manual_request=False):
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None:
        return False, "Core module - no installation needed"
    try:
        if manual_request:
            premium_reply(message, f"🔧 Manual installation for `{module_name}` -> `{package_name}`...", code_words=[module_name, package_name])
        else:
            premium_reply(message, f"🐍 Module `{module_name}` not found. Installing `{package_name}`...", code_words=[module_name, package_name])

        command = [sys.executable, '-m', 'pip', 'install', package_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            log_msg = f"Installed {package_name}.\n{result.stdout}"
            premium_reply(message, f"✅ Package `{package_name}` installed successfully.", emoji_key="success", code_words=[package_name])
            save_install_log(message.from_user.id, module_name, package_name, "success", log_msg)
            return True, log_msg
        else:
            error_msg = f"❌ Failed to install `{package_name}`.\n{result.stderr or result.stdout}"
            if len(error_msg) > 4000:
                error_msg = error_msg[:4000] + "\n... (truncated)"
            premium_reply(message, error_msg, emoji_key="error", code_words=[package_name])
            save_install_log(message.from_user.id, module_name, package_name, "failed", error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error installing `{package_name}`: {str(e)}"
        premium_reply(message, error_msg, emoji_key="error")
        save_install_log(message.from_user.id, module_name, package_name, "error", error_msg)
        return False, error_msg


def attempt_install_npm(module_name, user_folder, message, manual_request=False):
    try:
        if manual_request:
            premium_reply(message, f"🔧 Manual Node install for `{module_name}`...", code_words=[module_name])
        else:
            premium_reply(message, f"🟣 Node package `{module_name}` not found. Installing...", code_words=[module_name])

        command = ['npm', 'install', module_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=user_folder, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            log_msg = f"Installed {module_name}.\n{result.stdout}"
            premium_reply(message, f"✅ Node package `{module_name}` installed.", emoji_key="success", code_words=[module_name])
            save_install_log(message.from_user.id, module_name, module_name, "success", log_msg)
            return True, log_msg
        else:
            error_msg = f"❌ Failed to install `{module_name}`.\n{result.stderr or result.stdout}"
            if len(error_msg) > 4000:
                error_msg = error_msg[:4000]
            premium_reply(message, error_msg, emoji_key="error", code_words=[module_name])
            save_install_log(message.from_user.id, module_name, module_name, "failed", error_msg)
            return False, error_msg
    except FileNotFoundError:
        error_msg = "❌ 'npm' not found."
        premium_reply(message, error_msg, emoji_key="error")
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        premium_reply(message, error_msg, emoji_key="error")
        return False, error_msg


def manual_install_module_init(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned from using this bot.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(message.chat.id, subscription_message, reply_markup=markup)
        return
    if bot_locked and user_id not in admin_ids:
        premium_reply(message, "⚠️ Bot locked by admin. Try later.", emoji_key="error")
        return

    msg = premium_reply(message, "📦 Send module name to install (e.g., `requests` or `pillow`)\nFor Node.js: `npm:module_name`\n/cancel to cancel", emoji_key="upload")
    bot.register_next_step_handler(msg, process_manual_install_module)


def process_manual_install_module(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned from using this bot.", emoji_key="error")
        return
    if message.text.lower() == '/cancel':
        premium_reply(message, "❌ Installation cancelled.", emoji_key="error")
        return
    module_name = message.text.strip()
    if module_name.lower().startswith('npm:'):
        module_name = module_name[4:].strip()
        user_folder = get_user_folder(user_id)
        attempt_install_npm(module_name, user_folder, message, manual_request=True)
    else:
        attempt_install_pip(module_name, message, manual_request=True)


def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
        except Exception as e:
            logger.error(f"❌ Error saving file: {e}", exc_info=True)
        finally:
            conn.close()


def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]:
                    del user_files[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing file: {e}", exc_info=True)
        finally:
            conn.close()


def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            join_date = datetime.now().isoformat()
            c.execute('INSERT OR REPLACE INTO active_users (user_id, join_date, last_seen) VALUES (?, ?, ?)',
                      (user_id, join_date, join_date))
            conn.commit()
        except Exception as e:
            logger.error(f"❌ Error adding active user: {e}", exc_info=True)
        finally:
            conn.close()


def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat()
            c.execute('INSERT OR REPLACE INTO subscriptions (user_id, expiry) VALUES (?, ?)', (user_id, expiry_str))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry}
        except Exception as e:
            logger.error(f"❌ Error saving subscription: {e}", exc_info=True)
        finally:
            conn.close()


def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions:
                del user_subscriptions[user_id]
        except Exception as e:
            logger.error(f"❌ Error removing subscription: {e}", exc_info=True)
        finally:
            conn.close()


def add_admin_db(admin_id, added_by):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            added_date = datetime.now().isoformat()
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_date) VALUES (?, ?, ?)',
                      (admin_id, added_by, added_date))
            conn.commit()
            admin_ids.add(admin_id)
        except Exception as e:
            logger.error(f"❌ Error adding admin: {e}", exc_info=True)
        finally:
            conn.close()


def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        return False
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0
                if removed:
                    admin_ids.discard(admin_id)
            else:
                admin_ids.discard(admin_id)
            return removed
        except Exception as e:
            logger.error(f"❌ Error removing admin: {e}", exc_info=True)
            return False
        finally:
            conn.close()


# ============================================================
# KEYBOARDS
# ============================================================
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('📢 Updates Channel', callback_data='updates'),
        types.InlineKeyboardButton('📤 Upload File', callback_data='upload'),
        types.InlineKeyboardButton('📂 Check Files', callback_data='check_files'),
        types.InlineKeyboardButton('⚡ Bot Speed', callback_data='speed'),
        types.InlineKeyboardButton('📦 Manual Install', callback_data='manual_install'),
        types.InlineKeyboardButton('📞 Support', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]
    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💳 Subscriptions', callback_data='subscription'),
            types.InlineKeyboardButton('📊 Statistics', callback_data='stats'),
            types.InlineKeyboardButton('🔒 Lock Bot' if not bot_locked else '🔓 Unlock Bot',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 Broadcast', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 Admin Panel', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 Run All Scripts', callback_data='run_all_scripts'),
            types.InlineKeyboardButton('📢 Channel Add', callback_data='manage_mandatory_channels'),
            types.InlineKeyboardButton('👥 User Management', callback_data='user_management'),
            types.InlineKeyboardButton('🛠️ Admin Install', callback_data='admin_install'),
            types.InlineKeyboardButton('⚙️ Settings', callback_data='admin_settings'),
            types.InlineKeyboardButton('📋 Pending Files', callback_data='view_pending_files')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(admin_buttons[6], admin_buttons[8])
        markup.add(admin_buttons[7], admin_buttons[9])
        markup.add(admin_buttons[4])
        markup.add(admin_buttons[10])
        markup.add(buttons[5])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], buttons[4])
        markup.add(types.InlineKeyboardButton('📊 Statistics', callback_data='stats'))
        markup.add(buttons[5])
    return markup


def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup


def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("🔴 Stop", callback_data=f'stop_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🔄 Restart", callback_data=f'restart_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("📜 Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🟢 Start", callback_data=f'start_{script_owner_id}_{file_name}'),
            types.InlineKeyboardButton("🗑️ Delete", callback_data=f'delete_{script_owner_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton("📜 View Logs", callback_data=f'logs_{script_owner_id}_{file_name}')
        )
    markup.add(types.InlineKeyboardButton("🔙 Back to Files", callback_data='check_files'))
    return markup


def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Admin', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 List Admins', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup


def create_user_management_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('🚫 Ban User', callback_data='ban_user'),
        types.InlineKeyboardButton('✅ Unban User', callback_data='unban_user')
    )
    markup.row(
        types.InlineKeyboardButton('📊 User Info', callback_data='user_info'),
        types.InlineKeyboardButton('👥 All Users', callback_data='all_users')
    )
    markup.row(
        types.InlineKeyboardButton('🔧 Set User Limit', callback_data='set_user_limit'),
        types.InlineKeyboardButton('🗑️ Remove User Limit', callback_data='remove_user_limit')
    )
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup


def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Subscription', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton('🔍 Check Subscription', callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup


def create_admin_settings_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📊 System Info', callback_data='system_info'),
        types.InlineKeyboardButton('📈 Bot Performance', callback_data='bot_performance')
    )
    markup.row(
        types.InlineKeyboardButton('🧹 Cleanup Files', callback_data='cleanup_files'),
        types.InlineKeyboardButton('📋 Installation Logs', callback_data='install_logs')
    )
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup


# ============================================================
# FILE / SCRIPT HANDLING
# ============================================================
def handle_zip_file(downloaded_file_content, file_name_zip, message):
    user_id = message.from_user.id
    try:
        pending_id = save_pending_file(user_id, file_name_zip, downloaded_file_content, 'zip')
        if pending_id is None:
            premium_reply(message, "❌ Failed to save file for admin review.", emoji_key="error")
            return

        admin_notification = (
            f"📁 **New File Uploaded for Review**\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"📄 File: `{file_name_zip}`\n"
            f"📂 Type: ZIP Archive\n"
            f"🆔 Pending ID: `{pending_id}`\n\n"
            f"Use /pendingfiles or '📋 Pending Files' button to review."
        )
        for admin_id in admin_ids:
            try:
                premium_send(admin_id, admin_notification, emoji_key="upload",
                             code_words=[str(user_id), file_name_zip, str(pending_id)])
            except Exception as e:
                logger.error(f"Failed to send admin notification: {e}")

        premium_reply(
            message,
            f"✅ Your file `{file_name_zip}` has been uploaded and is pending admin approval.\nYou will be notified when it's approved.",
            emoji_key="success", code_words=[file_name_zip]
        )
    except Exception as e:
        logger.error(f"❌ Error processing zip for {user_id}: {e}", exc_info=True)
        premium_reply(message, f"❌ Error processing zip: {str(e)}", emoji_key="error")


def process_zip_file_with_content(downloaded_file_content, user_id, file_name_zip, message):
    user_folder = get_user_folder(user_id)
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_zip_")
        zip_path = os.path.join(temp_dir, file_name_zip)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.infolist():
                member_path = os.path.abspath(os.path.join(temp_dir, member.filename))
                if not member_path.startswith(os.path.abspath(temp_dir)):
                    raise zipfile.BadZipFile(f"Zip has unsafe path: {member.filename}")
            zip_ref.extractall(temp_dir)

        extracted_items = os.listdir(temp_dir)
        py_files = [f for f in extracted_items if f.endswith('.py')]
        js_files = [f for f in extracted_items if f.endswith('.js')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            premium_send(message.chat.id, f"🔧 Installing Python deps from `{req_file}`...", code_words=[req_file])
            try:
                command = [sys.executable, '-m', 'pip', 'install', '-r', req_path]
                subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
                premium_send(message.chat.id, f"✅ Python deps installed.", emoji_key="success")
            except subprocess.CalledProcessError as e:
                premium_send(message.chat.id, f"❌ Failed to install deps: {(e.stderr or e.stdout)[:500]}", emoji_key="error")
                return
            except Exception as e:
                premium_send(message.chat.id, f"❌ Error: {e}", emoji_key="error")
                return

        if pkg_json:
            premium_send(message.chat.id, f"🔧 Installing Node deps...", code_words=[pkg_json])
            try:
                subprocess.run(['npm', 'install'], capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                premium_send(message.chat.id, f"✅ Node deps installed.", emoji_key="success")
            except Exception as e:
                premium_send(message.chat.id, f"❌ Node deps error: {e}", emoji_key="error")

        main_script_name = None
        file_type = None
        for p in ['main.py', 'bot.py', 'app.py']:
            if p in py_files:
                main_script_name = p
                file_type = 'py'
                break
        if not main_script_name:
            for p in ['index.js', 'main.js', 'bot.js', 'app.js']:
                if p in js_files:
                    main_script_name = p
                    file_type = 'js'
                    break
        if not main_script_name:
            if py_files:
                main_script_name = py_files[0]
                file_type = 'py'
            elif js_files:
                main_script_name = js_files[0]
                file_type = 'js'
        if not main_script_name:
            premium_send(message.chat.id, "❌ No `.py` or `.js` script found!", emoji_key="error")
            return

        for item_name in os.listdir(temp_dir):
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            elif os.path.exists(dest_path):
                os.remove(dest_path)
            shutil.move(src_path, dest_path)

        save_user_file(user_id, main_script_name, file_type)
        main_script_path = os.path.join(user_folder, main_script_name)
        premium_send(message.chat.id, f"✅ Files extracted. Starting: `{main_script_name}`...", emoji_key="success", code_words=[main_script_name])

        if file_type == 'py':
            threading.Thread(target=run_script_with_auto_version,
                             args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script_with_auto_version,
                             args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
    except Exception as e:
        logger.error(f"Error processing zip file: {e}", exc_info=True)
        premium_send(message.chat.id, f"❌ Error processing zip: {str(e)}", emoji_key="error")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass


def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script_with_auto_version,
                         args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error handling JS {file_name}: {e}", exc_info=True)
        premium_send(message.chat.id, f"❌ Error: {str(e)}", emoji_key="error")


def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script_with_auto_version,
                         args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error handling PY {file_name}: {e}", exc_info=True)
        premium_send(message.chat.id, f"❌ Error: {str(e)}", emoji_key="error")


def run_script_with_auto_version(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        premium_send(message_obj_for_reply.chat.id, f"❌ Failed to run '{file_name}' after {max_attempts} attempts.", emoji_key="error", code_words=[file_name])
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} Python: {script_path} (Key: {script_key})")
    detected_version = detect_telegram_version(script_path)
    python_cmd = get_python_for_version(detected_version)

    try:
        if not os.path.exists(script_path):
            premium_send(message_obj_for_reply.chat.id, f"❌ Script '{file_name}' not found!", emoji_key="error", code_words=[file_name])
            if script_owner_id in user_files:
                user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
            remove_user_file_db(script_owner_id, file_name)
            return

        if attempt == 1:
            check_command = [python_cmd, script_path]
            check_proc = None
            try:
                check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                if return_code != 0 and stderr:
                    match_py = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match_py:
                        module_name = match_py.group(1).strip().strip("'\"")
                        success, _ = attempt_install_pip(module_name, message_obj_for_reply)
                        if success:
                            premium_send(message_obj_for_reply.chat.id, f"🔧 Install successful. Retrying '{file_name}'...", emoji_key="success", code_words=[file_name])
                            time.sleep(2)
                            threading.Thread(target=run_script_with_auto_version,
                                             args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                            return
                        else:
                            premium_send(message_obj_for_reply.chat.id, f"❌ Install failed. Cannot run '{file_name}'.", emoji_key="error", code_words=[file_name])
                            return
                    else:
                        error_summary = stderr[:500]
                        premium_send(message_obj_for_reply.chat.id, f"❌ Error in script '{file_name}':\n{error_summary}", emoji_key="error", code_words=[file_name])
                        return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()
            except FileNotFoundError:
                premium_send(message_obj_for_reply.chat.id, f"❌ Python '{python_cmd}' not found.", emoji_key="error")
                return
            except Exception as e:
                premium_send(message_obj_for_reply.chat.id, f"❌ Pre-check error: {e}", emoji_key="error")
                return
            finally:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None
        process = None
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
            premium_send(message_obj_for_reply.chat.id, f"❌ Failed to open log: {e}", emoji_key="error")
            return
        try:
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                [python_cmd, script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore'
            )
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'py',
                'script_key': script_key, 'python_cmd': python_cmd, 'detected_version': detected_version
            }
            premium_send(
                message_obj_for_reply.chat.id,
                f"✅ Python script '{file_name}' started! (PID: {process.pid}) (Version: {detected_version})",
                emoji_key="success", code_words=[file_name, str(process.pid)]
            )
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            premium_send(message_obj_for_reply.chat.id, f"❌ Error starting '{file_name}': {e}", emoji_key="error", code_words=[file_name])
            if process and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]
    except Exception as e:
        logger.error(f"❌ Unexpected: {e}", exc_info=True)
        premium_send(message_obj_for_reply.chat.id, f"❌ Unexpected: {str(e)}", emoji_key="error")
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]


def run_js_script_with_auto_version(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    max_attempts = 2
    if attempt > max_attempts:
        premium_send(message_obj_for_reply.chat.id, f"❌ Failed to run '{file_name}' after {max_attempts} attempts.", emoji_key="error", code_words=[file_name])
        return

    script_key = f"{script_owner_id}_{file_name}"
    logger.info(f"Attempt {attempt} JS: {script_path} (Key: {script_key})")

    try:
        if not os.path.exists(script_path):
            premium_send(message_obj_for_reply.chat.id, f"❌ JS Script '{file_name}' not found!", emoji_key="error", code_words=[file_name])
            if script_owner_id in user_files:
                user_files[script_owner_id] = [f for f in user_files.get(script_owner_id, []) if f[0] != file_name]
            remove_user_file_db(script_owner_id, file_name)
            return

        if attempt == 1:
            check_proc = None
            try:
                check_proc = subprocess.Popen(['node', script_path], cwd=user_folder,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                              text=True, encoding='utf-8', errors='ignore')
                stdout, stderr = check_proc.communicate(timeout=5)
                return_code = check_proc.returncode
                if return_code != 0 and stderr:
                    match_js = re.search(r"Cannot find module '(.+?)'", stderr)
                    if match_js:
                        module_name = match_js.group(1).strip().strip("'\"")
                        if not module_name.startswith('.') and not module_name.startswith('/'):
                            success, _ = attempt_install_npm(module_name, user_folder, message_obj_for_reply)
                            if success:
                                premium_send(message_obj_for_reply.chat.id, f"🔧 NPM install OK. Retrying '{file_name}'...", emoji_key="success", code_words=[file_name])
                                time.sleep(2)
                                threading.Thread(target=run_js_script_with_auto_version,
                                                 args=(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt + 1)).start()
                                return
                            else:
                                premium_send(message_obj_for_reply.chat.id, f"❌ NPM install failed.", emoji_key="error")
                                return
                    error_summary = stderr[:500]
                    premium_send(message_obj_for_reply.chat.id, f"❌ JS Error: {error_summary}", emoji_key="error", code_words=[file_name])
                    return
            except subprocess.TimeoutExpired:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()
            except FileNotFoundError:
                premium_send(message_obj_for_reply.chat.id, "❌ 'node' not found. Install Node.js.", emoji_key="error")
                return
            except Exception as e:
                premium_send(message_obj_for_reply.chat.id, f"❌ JS pre-check error: {e}", emoji_key="error")
                return
            finally:
                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = None
        process = None
        try:
            log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        except Exception as e:
            premium_send(message_obj_for_reply.chat.id, f"❌ Failed log: {e}", emoji_key="error")
            return
        try:
            startupinfo = None
            creationflags = 0
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            process = subprocess.Popen(
                ['node', script_path], cwd=user_folder, stdout=log_file, stderr=log_file,
                stdin=subprocess.PIPE, startupinfo=startupinfo, creationflags=creationflags,
                encoding='utf-8', errors='ignore'
            )
            bot_scripts[script_key] = {
                'process': process, 'log_file': log_file, 'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id, 'script_owner_id': script_owner_id,
                'start_time': datetime.now(), 'user_folder': user_folder, 'type': 'js',
                'script_key': script_key
            }
            premium_send(
                message_obj_for_reply.chat.id,
                f"✅ JS script '{file_name}' started! (PID: {process.pid})",
                emoji_key="success", code_words=[file_name, str(process.pid)]
            )
        except Exception as e:
            if log_file and not log_file.closed:
                log_file.close()
            premium_send(message_obj_for_reply.chat.id, f"❌ Error starting '{file_name}': {e}", emoji_key="error", code_words=[file_name])
            if process and process.poll() is None:
                kill_process_tree({'process': process, 'log_file': log_file, 'script_key': script_key})
            if script_key in bot_scripts:
                del bot_scripts[script_key]
    except Exception as e:
        logger.error(f"❌ JS Unexpected: {e}", exc_info=True)
        premium_send(message_obj_for_reply.chat.id, f"❌ Unexpected: {str(e)}", emoji_key="error")
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]


# ============================================================
# LOGIC HANDLERS
# ============================================================
def _logic_send_welcome(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    if is_user_banned(user_id):
        premium_send(chat_id, "❌ You are banned from using this bot.", emoji_key="error")
        return

    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(chat_id, subscription_message, reply_markup=markup)
        return

    if bot_locked and user_id not in admin_ids:
        premium_send(chat_id, "⚠️ Bot locked by admin. Try later.", emoji_key="error")
        return

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            premium_send(
                OWNER_ID,
                f"🎉 New user!\n👤 Name: {user_name}\n🆔 ID: `{user_id}`",
                emoji_key="party", code_words=[str(user_id)]
            )
        except Exception as e:
            logger.error(f"⚠️ Failed notify owner: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    expiry_info = ""

    if user_id == OWNER_ID:
        user_status = "👑 Owner"
    elif user_id in admin_ids:
        user_status = "🛡️ Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"
            days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n⏳ Subscription expires in: {days_left} days"
        else:
            user_status = "🆓 Free User (Expired Sub)"
            remove_subscription_db(user_id)
    else:
        user_status = "🆓 Free User"

    welcome_msg_text = (
        f"╔═════════════════════╗\n"
        f"   🤖 ᴀʟᴇxᴀ ʜᴏꜱᴛɪɴɢ ʙᴏᴛ   \n"
        f"╚═════════════════════╝\n\n"
        f"✨ ᴡᴇʟᴄᴏᴍᴇ, {user_name}!\n\n"
        f"🆔 Your User ID: `{user_id}`\n"
        f"🔰 Your Status: {user_status}{expiry_info}\n"
        f"📁 Files Uploaded: {current_files} / {limit_str}\n\n"
        f"🤖 Host & run Python (`.py`) or JS (`.js`) scripts.\n"
        f"   Upload single scripts or `.zip` archives.\n"
        f"📦 Manual module installation available\n\n"
        f"👇 Use buttons or type commands."
    )

    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    premium_send(chat_id, welcome_msg_text, reply_markup=main_reply_markup, emoji_key="welcome",
                 code_words=[str(user_id), ".py", ".js", ".zip"])


def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('📢 Updates Channel 1', url=f'https://t.me/{UPDATE_CHANNEL.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('📢 Updates Channel 2', url=f'https://t.me/{UPDATE_CHANNEL_2.replace("@", "")}'))
    premium_reply(message, "📢 Our Updates Channels:", emoji_key="broadcast", reply_markup=markup)


def _logic_upload_file(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(message.chat.id, subscription_message, reply_markup=markup)
        return
    if bot_locked and user_id not in admin_ids:
        premium_reply(message, "⚠️ Bot locked.", emoji_key="error")
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        premium_reply(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files first.", emoji_key="error")
        return
    premium_reply(message, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.\n\n⏳ Your file will be sent to admin for approval before running.",
                  emoji_key="upload", code_words=[".py", ".js", ".zip"])


def _logic_check_files(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(message.chat.id, subscription_message, reply_markup=markup)
        return
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        premium_reply(message, "📂 Your files:\n\n(No files uploaded yet)", emoji_key="upload")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    premium_reply(message, "📂 Your files:\nClick to manage.", emoji_key="upload", reply_markup=markup)


def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(chat_id, subscription_message, reply_markup=markup)
        return
    start_time_ping = time.time()
    wait_msg = premium_reply(message, "🏃 Testing speed...", emoji_key="rocket")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🟢 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID:
            user_level = "👑 Owner"
        elif user_id in admin_ids:
            user_level = "🛡️ Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now():
            user_level = "⭐ Premium"
        else:
            user_level = "🆓 Free User"
        speed_msg = (f"⚡ Bot Speed & Status:\n\n⏱️ API Response: {response_time} ms\n"
                     f"🚦 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}")
        premium_edit(chat_id, wait_msg.message_id, speed_msg, emoji_key="lightning")
    except Exception as e:
        logger.error(f"Speed error: {e}")
        premium_edit(chat_id, wait_msg.message_id, "❌ Error during speed test.", emoji_key="error")


def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 Support', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    premium_reply(message, "📞 Click to contact support:", emoji_key="heart", reply_markup=markup)


def _logic_manual_install(message):
    manual_install_module_init(message)


def _logic_help(message):
    help_text = """
🤖 **ALEXA HOSTING Bot Help Guide**

**📌 Basic Commands:**
• /start - Start the bot
• /help - Show this help message
• /status - Show bot statistics

**📁 File Management:**
• Upload `.py` or `.js` files directly
• Upload `.zip` archives with multiple files
• Files go to admin for approval before running
• Auto-installs dependencies from `requirements.txt` or `package.json`
• 🔥 **Auto Version Detection** - Works with old (v13.x) & new (v20.x)!

**📦 Module Installation:**
• Auto-install missing Python/Node modules
• Manual install via "📦 Manual Install" button
• Admin can install modules for users

**👑 Admin Features:**
• User management (ban/unban)
• Set custom file limits
• Manage mandatory channels
• Broadcast messages
• Run all user scripts
• Approve/reject pending files

**Support:** @a3lxe
**Updates:** @a4lxe
"""
    premium_reply(message, help_text, emoji_key="idea")


def _logic_subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    premium_reply(message, "💳 Subscription Management\nUse inline buttons.",
                  emoji_key="diamond", reply_markup=create_subscription_menu())


def _logic_statistics(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(message.chat.id, subscription_message, reply_markup=markup)
        return

    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())
    running_bots_count = 0
    user_running_bots = 0
    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots += 1

    pending_files = get_pending_files_for_admin()
    pending_count = len(pending_files)

    stats_msg_base = (f"📊 Bot Statistics:\n\n"
                      f"👥 Total Users: {total_users}\n"
                      f"🚫 Banned Users: {len(banned_users)}\n"
                      f"📂 Total File Records: {total_files_records}\n"
                      f"🟢 Total Active Bots: {running_bots_count}\n")

    if user_id in admin_ids:
        stats_msg_admin = (f"🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
                           f"📢 Mandatory Channels: {len(mandatory_channels)}\n"
                           f"⚙️ Custom Limits: {len(user_limits)}\n"
                           f"🤖 Your Running Bots: {user_running_bots}\n"
                           f"⏳ Pending Files: {pending_count}\n"
                           f"🔥 Auto Version Detection: Active")
        stats_msg = stats_msg_base + stats_msg_admin
    else:
        stats_msg = stats_msg_base + f"🤖 Your Running Bots: {user_running_bots}"

    premium_reply(message, stats_msg, emoji_key="status")


def _logic_broadcast_init(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    msg = premium_reply(message, "📢 Send message to broadcast to all active users.\n/cancel to abort.", emoji_key="broadcast")
    bot.register_next_step_handler(msg, process_broadcast_message)


def _logic_toggle_lock_bot(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "locked" if bot_locked else "unlocked"
    premium_reply(message, f"🔒 Bot has been {status}.", emoji_key="success" if not bot_locked else "error")


def _logic_admin_panel(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    premium_reply(message, "👑 Admin Panel\nManage admins.", emoji_key="crown", reply_markup=create_admin_panel())


def _logic_user_management(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    premium_reply(message, "👥 User Management", emoji_key="crown", reply_markup=create_user_management_menu())


def _logic_admin_settings(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    premium_reply(message, "⚙️ Admin Settings", emoji_key="crown", reply_markup=create_admin_settings_menu())


def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: premium_send(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: premium_send(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message
    else:
        return

    if admin_user_id not in admin_ids:
        reply_func("⚠️ Admin permissions required.", emoji_key="error")
        return

    reply_func("⏳ Starting all user scripts...", emoji_key="rocket")
    started_count = 0
    attempted_users = 0
    skipped_files = 0

    all_user_files_snapshot = dict(user_files)
    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user:
            continue
        attempted_users += 1
        user_folder = get_user_folder(target_user_id)
        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script_with_auto_version,
                                             args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script_with_auto_version,
                                             args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            skipped_files += 1
                        time.sleep(0.7)
                    except Exception as e:
                        logger.error(f"Error queueing {file_name}: {e}")
                        skipped_files += 1
                else:
                    skipped_files += 1

    summary_msg = (f"✅ Processing Complete:\n\n"
                   f"▶️ Started: {started_count}\n"
                   f"👥 Users: {attempted_users}\n"
                   f"⚠️ Skipped: {skipped_files}")
    reply_func(summary_msg, emoji_key="success")


def _logic_manage_mandatory_channels(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    premium_reply(message, "📢 Manage Mandatory Channels", emoji_key="bell", reply_markup=create_mandatory_channels_menu())


def _logic_admin_install(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    msg = premium_reply(message, "🛠️ Admin Module Installation\nSend user ID and module (e.g., `12345678 requests`)\n/cancel to cancel", emoji_key="upload")
    bot.register_next_step_handler(msg, process_admin_install)


def process_admin_install(message):
    admin_id = message.from_user.id
    if admin_id not in admin_ids:
        premium_reply(message, "⚠️ Not authorized.", emoji_key="error")
        return
    if message.text.lower() == '/cancel':
        premium_reply(message, "❌ Cancelled.", emoji_key="error")
        return
    try:
        parts = message.text.split()
        if len(parts) < 2:
            premium_reply(message, "⚠️ Format: `user_id module_name`", emoji_key="error")
            return
        user_id = int(parts[0])
        module_name = ' '.join(parts[1:])
        if module_name.lower().startswith('npm:'):
            module_name = module_name[4:].strip()
            user_folder = get_user_folder(user_id)
            success, log = attempt_install_npm(module_name, user_folder, message, manual_request=True)
        else:
            success, log = attempt_install_pip(module_name, message, manual_request=True)
        if success:
            try:
                premium_send(user_id, f"📦 Admin installed module `{module_name}` for you.",
                             emoji_key="success", code_words=[module_name])
            except Exception:
                pass
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")
    except Exception as e:
        premium_reply(message, f"❌ Error: {e}", emoji_key="error")


# ============================================================
# COMMAND HANDLERS
# ============================================================
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    if message.text == '/help':
        _logic_help(message)
    else:
        _logic_send_welcome(message)


@bot.message_handler(commands=['status'])
def command_show_status(message):
    _logic_statistics(message)


@bot.message_handler(commands=['pendingfiles'])
def command_pending_files(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    view_pending_files(message)


BUTTON_TEXT_TO_LOGIC = {
    "📢 Updates Channel": _logic_updates_channel,
    "📤 Upload File": _logic_upload_file,
    "📂 Check Files": _logic_check_files,
    "⚡ Bot Speed": _logic_bot_speed,
    "📞 Support": _logic_contact_owner,
    "📊 Statistics": _logic_statistics,
    "💳 Subscriptions": _logic_subscriptions_panel,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Lock Bot": _logic_toggle_lock_bot,
    "🟢 Running All Code": _logic_run_all_scripts,
    "👑 Admin Panel": _logic_admin_panel,
    "📢 Channel Add": _logic_manage_mandatory_channels,
    "👥 User Management": _logic_user_management,
    "🛠️ Manual Install": _logic_manual_install,
    "⚙️ Settings": _logic_admin_settings,
    "📦 Manual Install": _logic_manual_install,
    "🆘 Help": _logic_help
}


@bot.message_handler(func=lambda message: message.text in BUTTON_TEXT_TO_LOGIC)
def handle_button_text(message):
    logic_func = BUTTON_TEXT_TO_LOGIC.get(message.text)
    if logic_func:
        logic_func(message)


@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message):
    _logic_updates_channel(message)


@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message):
    _logic_upload_file(message)


@bot.message_handler(commands=['checkfiles'])
def command_check_files(message):
    _logic_check_files(message)


@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message):
    _logic_bot_speed(message)


@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message):
    _logic_contact_owner(message)


@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message):
    _logic_subscriptions_panel(message)


@bot.message_handler(commands=['statistics'])
def command_statistics(message):
    _logic_statistics(message)


@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    _logic_broadcast_init(message)


@bot.message_handler(commands=['lockbot'])
def command_lock_bot(message):
    _logic_toggle_lock_bot(message)


@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message):
    _logic_admin_panel(message)


@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message):
    _logic_run_all_scripts(message)


@bot.message_handler(commands=['managechannels'])
def command_manage_channels(message):
    _logic_manage_mandatory_channels(message)


@bot.message_handler(commands=['usermanagement'])
def command_user_management(message):
    _logic_user_management(message)


@bot.message_handler(commands=['manualinstall'])
def command_manual_install(message):
    _logic_manual_install(message)


@bot.message_handler(commands=['admininstall'])
def command_admin_install(message):
    _logic_admin_install(message)


@bot.message_handler(commands=['ping'])
def ping(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(message.chat.id, subscription_message, reply_markup=markup)
        return
    start_ping_time = time.time()
    msg = premium_reply(message, "🏓 Pong!", emoji_key="lightning")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    premium_edit(message.chat.id, msg.message_id, f"🏓 Pong! Latency: {latency} ms", emoji_key="lightning")


# ============================================================
# DOCUMENT HANDLER
# ============================================================
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_user_banned(user_id):
        premium_reply(message, "❌ You are banned.", emoji_key="error")
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        premium_send(chat_id, subscription_message, reply_markup=markup)
        return

    doc = message.document
    if bot_locked and user_id not in admin_ids:
        premium_reply(message, "⚠️ Bot locked.", emoji_key="error")
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        premium_reply(message, f"⚠️ File limit ({current_files}/{limit_str}) reached.", emoji_key="error")
        return

    file_name = doc.file_name
    if not file_name:
        premium_reply(message, "⚠️ No file name.", emoji_key="error")
        return
    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        premium_reply(message, "⚠️ Unsupported type! Only `.py`, `.js`, `.zip` allowed.",
                      emoji_key="error", code_words=[".py", ".js", ".zip"])
        return
    max_file_size = 20 * 1024 * 1024
    if doc.file_size > max_file_size:
        premium_reply(message, f"⚠️ File too large (Max: 20 MB).", emoji_key="error")
        return

    try:
        try:
            bot.forward_message(OWNER_ID, chat_id, message.message_id)
            premium_send(OWNER_ID, f"⬆️ File '{file_name}' from {message.from_user.first_name} (`{user_id}`)",
                         emoji_key="upload", code_words=[file_name, str(user_id)])
        except Exception as e:
            logger.error(f"Failed forward to owner: {e}")

        download_wait_msg = premium_reply(message, f"⏳ Downloading `{file_name}`...",
                                          emoji_key="upload", code_words=[file_name])
        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(file_info_tg_doc.file_path)
        premium_edit(chat_id, download_wait_msg.message_id,
                     f"✅ Downloaded `{file_name}`. Processing...",
                     emoji_key="success", code_words=[file_name])

        if file_ext == '.zip':
            handle_zip_file(downloaded_file_content, file_name, message)
        else:
            file_type = 'py' if file_ext == '.py' else 'js'
            pending_id = save_pending_file(user_id, file_name, downloaded_file_content, file_type)
            if pending_id is None:
                premium_reply(message, "❌ Failed to save for review.", emoji_key="error")
                return

            admin_notification = (
                f"📁 **New File Uploaded for Review**\n\n"
                f"👤 User ID: `{user_id}`\n"
                f"📄 File: `{file_name}`\n"
                f"📂 Type: {file_type.upper()} File\n"
                f"🆔 Pending ID: `{pending_id}`\n\n"
                f"Use /pendingfiles to review."
            )
            for admin_id in admin_ids:
                try:
                    premium_send(admin_id, admin_notification, emoji_key="upload",
                                 code_words=[str(user_id), file_name, str(pending_id)])
                except Exception as e:
                    logger.error(f"Failed admin notification: {e}")

            premium_reply(
                message,
                f"✅ Your file `{file_name}` uploaded & pending admin approval.\nYou will be notified when approved.",
                emoji_key="success", code_words=[file_name]
            )

    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Telegram API Error: {e}", exc_info=True)
        if "file is too big" in str(e).lower():
            premium_reply(message, "❌ File too large to download (~20MB limit).", emoji_key="error")
        else:
            premium_reply(message, f"❌ API Error: {str(e)}", emoji_key="error")
    except Exception as e:
        logger.error(f"❌ Error handling file: {e}", exc_info=True)
        premium_reply(message, f"❌ Error: {str(e)}", emoji_key="error")


# ============================================================
# CALLBACK HANDLER
# ============================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    logger.info(f"Callback: User={user_id}, Data='{data}'")

    if is_user_banned(user_id) and data not in ['back_to_main']:
        bot.answer_callback_query(call.id, "❌ You are banned.", show_alert=True)
        return

    if data not in ['check_subscription_status', 'back_to_main', 'manual_install', 'view_pending_files']:
        is_subscribed, not_joined = check_mandatory_subscription(user_id)
        if not is_subscribed and user_id not in admin_ids:
            subscription_message, markup = create_subscription_check_message(not_joined)
            bot.answer_callback_query(call.id)
            try:
                premium_edit(call.message.chat.id, call.message.message_id, subscription_message, reply_markup=markup)
            except:
                premium_send(call.message.chat.id, subscription_message, reply_markup=markup)
            return

    if bot_locked and user_id not in admin_ids and data not in ['back_to_main', 'speed', 'stats', 'check_subscription_status', 'manual_install', 'view_pending_files']:
        bot.answer_callback_query(call.id, "⚠️ Bot locked.", show_alert=True)
        return

    try:
        if data == 'updates':
            updates_callback(call)
        elif data == 'upload':
            upload_callback(call)
        elif data == 'check_files':
            check_files_callback(call)
        elif data.startswith('file_'):
            file_control_callback(call)
        elif data.startswith('start_'):
            start_bot_callback(call)
        elif data.startswith('stop_'):
            stop_bot_callback(call)
        elif data.startswith('restart_'):
            restart_bot_callback(call)
        elif data.startswith('delete_'):
            delete_bot_callback(call)
        elif data.startswith('logs_'):
            logs_bot_callback(call)
        elif data == 'speed':
            speed_callback(call)
        elif data == 'back_to_main':
            back_to_main_callback(call)
        elif data.startswith('confirm_broadcast_'):
            handle_confirm_broadcast(call)
        elif data == 'cancel_broadcast':
            handle_cancel_broadcast(call)
        elif data == 'manual_install':
            manual_install_callback(call)
        elif data == 'subscription':
            admin_required_callback(call, subscription_management_callback)
        elif data == 'stats':
            stats_callback(call)
        elif data == 'lock_bot':
            admin_required_callback(call, lock_bot_callback)
        elif data == 'unlock_bot':
            admin_required_callback(call, unlock_bot_callback)
        elif data == 'run_all_scripts':
            admin_required_callback(call, run_all_scripts_callback)
        elif data == 'broadcast':
            admin_required_callback(call, broadcast_init_callback)
        elif data == 'admin_panel':
            admin_required_callback(call, admin_panel_callback)
        elif data == 'add_admin':
            owner_required_callback(call, add_admin_init_callback)
        elif data == 'remove_admin':
            owner_required_callback(call, remove_admin_init_callback)
        elif data == 'list_admins':
            admin_required_callback(call, list_admins_callback)
        elif data == 'add_subscription':
            admin_required_callback(call, add_subscription_init_callback)
        elif data == 'remove_subscription':
            admin_required_callback(call, remove_subscription_init_callback)
        elif data == 'check_subscription':
            admin_required_callback(call, check_subscription_init_callback)
        elif data == 'user_management':
            admin_required_callback(call, user_management_callback)
        elif data == 'ban_user':
            admin_required_callback(call, ban_user_callback)
        elif data == 'unban_user':
            admin_required_callback(call, unban_user_callback)
        elif data == 'user_info':
            admin_required_callback(call, user_info_callback)
        elif data == 'all_users':
            admin_required_callback(call, all_users_callback)
        elif data == 'set_user_limit':
            admin_required_callback(call, set_user_limit_callback)
        elif data == 'remove_user_limit':
            admin_required_callback(call, remove_user_limit_callback)
        elif data == 'admin_settings':
            admin_required_callback(call, admin_settings_callback)
        elif data == 'system_info':
            admin_required_callback(call, system_info_callback)
        elif data == 'bot_performance':
            admin_required_callback(call, bot_performance_callback)
        elif data == 'cleanup_files':
            admin_required_callback(call, cleanup_files_callback)
        elif data == 'install_logs':
            admin_required_callback(call, install_logs_callback)
        elif data == 'admin_install':
            admin_required_callback(call, admin_install_callback)
        elif data == 'manage_mandatory_channels':
            admin_required_callback(call, manage_mandatory_channels_callback)
        elif data == 'add_mandatory_channel':
            admin_required_callback(call, add_mandatory_channel_callback)
        elif data == 'remove_mandatory_channel':
            admin_required_callback(call, remove_mandatory_channel_callback)
        elif data == 'list_mandatory_channels':
            admin_required_callback(call, list_mandatory_channels_callback)
        elif data.startswith('remove_channel_'):
            admin_required_callback(call, process_remove_channel)
        elif data == 'check_subscription_status':
            check_subscription_status_callback(call)
        elif data == 'view_pending_files':
            admin_required_callback(call, view_pending_files_callback)
        elif data.startswith('approve_pending_'):
            admin_required_callback(call, approve_pending_file_callback)
        elif data.startswith('reject_pending_'):
            admin_required_callback(call, reject_pending_file_callback)
        else:
            bot.answer_callback_query(call.id, "Unknown action.")
    except Exception as e:
        logger.error(f"Error handling callback '{data}': {e}", exc_info=True)
        try:
            bot.answer_callback_query(call.id, "Error processing request.", show_alert=True)
        except Exception:
            pass


def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin permissions required.", show_alert=True)
        return
    func_to_run(call)


def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "⚠️ Owner permissions required.", show_alert=True)
        return
    func_to_run(call)


# ============================================================
# USER CALLBACKS
# ============================================================
def updates_callback(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton('📢 Updates Channel 1', url=f'https://t.me/{UPDATE_CHANNEL.replace("@", "")}'))
    markup.add(types.InlineKeyboardButton('📢 Updates Channel 2', url=f'https://t.me/{UPDATE_CHANNEL_2.replace("@", "")}'))
    try:
        premium_edit(call.message.chat.id, call.message.message_id, "📢 Our Updates Channels:", reply_markup=markup, emoji_key="broadcast")
    except Exception as e:
        logger.error(f"Error showing updates: {e}")


def manual_install_callback(call):
    bot.answer_callback_query(call.id)
    manual_install_module_init(call.message)


def upload_callback(call):
    user_id = call.from_user.id
    if is_user_banned(user_id):
        bot.answer_callback_query(call.id, "❌ You are banned.", show_alert=True)
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.answer_callback_query(call.id)
        try:
            premium_edit(call.message.chat.id, call.message.message_id, subscription_message, reply_markup=markup)
        except:
            premium_send(call.message.chat.id, subscription_message, reply_markup=markup)
        return
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    if current_files >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.answer_callback_query(call.id, f"⚠️ File limit ({current_files}/{limit_str}) reached.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    premium_send(call.message.chat.id, "📤 Send your Python (`.py`), JS (`.js`), or ZIP (`.zip`) file.\n\n⏳ Your file will be sent to admin for approval.",
                 emoji_key="upload", code_words=[".py", ".js", ".zip"])


def check_files_callback(call):
    user_id = call.from_user.id
    if is_user_banned(user_id):
        bot.answer_callback_query(call.id, "❌ You are banned.", show_alert=True)
        return
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if not is_subscribed and user_id not in admin_ids:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.answer_callback_query(call.id)
        try:
            premium_edit(call.message.chat.id, call.message.message_id, subscription_message, reply_markup=markup)
        except:
            premium_send(call.message.chat.id, subscription_message, reply_markup=markup)
        return
    chat_id = call.message.chat.id
    user_files_list = user_files.get(user_id, [])
    if not user_files_list:
        bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
            premium_edit(chat_id, call.message.message_id, "📂 Your files:\n\n(No files uploaded)", reply_markup=markup, emoji_key="upload")
        except Exception as e:
            logger.error(f"Error editing empty: {e}")
        return
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in sorted(user_files_list):
        is_running = is_bot_running(user_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        btn_text = f"{file_name} ({file_type}) - {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
    try:
        premium_edit(chat_id, call.message.message_id, "📂 Your files:\nClick to manage.", reply_markup=markup, emoji_key="upload")
    except telebot.apihelper.ApiTelegramException as e:
        if "message is not modified" not in str(e):
            logger.error(f"Error editing files: {e}")
    except Exception as e:
        logger.error(f"Error files: {e}")


def file_control_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        requesting_user_id = call.from_user.id
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ You can only manage your own files.", show_alert=True)
            check_files_callback(call)
            return
        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call)
            return
        bot.answer_callback_query(call.id)
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?')
        try:
            premium_edit(
                call.message.chat.id, call.message.message_id,
                f"⚙️ Controls: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: {status_text}",
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                emoji_key="idea", code_words=[file_name, str(script_owner_id)]
            )
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" not in str(e):
                raise
    except (ValueError, IndexError) as ve:
        logger.error(f"Parse error: {ve}. Data: '{call.data}'")
        bot.answer_callback_query(call.id, "Error: Invalid data.", show_alert=True)
    except Exception as e:
        logger.error(f"file_control error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, "An error occurred.", show_alert=True)


def start_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if not (user_id == script_owner_id or user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
            return
        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, "⚠️ Already running.", show_alert=True)
            return
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "🔄 Starting...")
        file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), 'py')
        if file_type == 'py':
            threading.Thread(target=run_script_with_auto_version,
                             args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script_with_auto_version,
                             args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
    except Exception as e:
        logger.error(f"start_bot error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)


def stop_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if not (user_id == script_owner_id or user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            bot.answer_callback_query(call.id, "🛑 Stopping...")
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
            premium_send(call.message.chat.id, f"🛑 Bot '{file_name}' stopped.", emoji_key="error", code_words=[file_name])
        else:
            bot.answer_callback_query(call.id, "⚠️ Not running.", show_alert=True)
    except Exception as e:
        logger.error(f"stop error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)


def restart_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if not (user_id == script_owner_id or user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            bot.answer_callback_query(call.id, "🔄 Restarting...")
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
            user_folder = get_user_folder(script_owner_id)
            file_path = os.path.join(user_folder, file_name)
            file_type = next((f[1] for f in user_files.get(script_owner_id, []) if f[0] == file_name), 'py')
            if file_type == 'py':
                threading.Thread(target=run_script_with_auto_version,
                                 args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
            elif file_type == 'js':
                threading.Thread(target=run_js_script_with_auto_version,
                                 args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
            bot.answer_callback_query(call.id, "⚠️ Not running.", show_alert=True)
    except Exception as e:
        logger.error(f"restart error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)


def delete_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if not (user_id == script_owner_id or user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
            return
        script_key = f"{script_owner_id}_{file_name}"
        if script_key in bot_scripts:
            bot.answer_callback_query(call.id, "🗑️ Stopping and deleting...")
            kill_process_tree(bot_scripts[script_key])
            del bot_scripts[script_key]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if os.path.exists(log_file_path):
            os.remove(log_file_path)
        remove_user_file_db(script_owner_id, file_name)
        premium_send(call.message.chat.id, f"🗑️ '{file_name}' deleted.", emoji_key="success", code_words=[file_name])
        check_files_callback(call)
    except Exception as e:
        logger.error(f"delete error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)


def logs_bot_callback(call):
    try:
        _, script_owner_id_str, file_name = call.data.split('_', 2)
        script_owner_id = int(script_owner_id_str)
        user_id = call.from_user.id
        if not (user_id == script_owner_id or user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
            return
        user_folder = get_user_folder(script_owner_id)
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            if log_content:
                if len(log_content) > 4000:
                    log_content = log_content[-4000:]
                bot.send_message(call.message.chat.id, f"📜 Last 4000 chars of logs for `{file_name}`:\n```\n{log_content}\n```", parse_mode='Markdown')
            else:
                premium_send(call.message.chat.id, f"📜 Log file is empty.", emoji_key="upload", code_words=[file_name])
        else:
            premium_send(call.message.chat.id, f"📜 No log file found.", emoji_key="error", code_words=[file_name])
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"logs error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"Error: {str(e)}", show_alert=True)


def speed_callback(call):
    bot.answer_callback_query(call.id)
    _logic_bot_speed(call.message)


def back_to_main_callback(call):
    user_id = call.from_user.id
    bot.answer_callback_query(call.id)
    markup = create_main_menu_inline(user_id)
    try:
        premium_edit(call.message.chat.id, call.message.message_id, "🤖 Welcome back to the main menu!",
                     reply_markup=markup, emoji_key="welcome")
    except Exception as e:
        logger.error(f"Error returning: {e}")


def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message)


def lock_bot_callback(call):
    global bot_locked
    bot_locked = True
    bot.answer_callback_query(call.id, "🔒 Bot locked.")
    back_to_main_callback(call)
    for admin_id in admin_ids:
        try:
            premium_send(admin_id, "🔒 Bot has been locked by admin.", emoji_key="error")
        except:
            pass


def unlock_bot_callback(call):
    global bot_locked
    bot_locked = False
    bot.answer_callback_query(call.id, "🔓 Bot unlocked.")
    back_to_main_callback(call)
    for admin_id in admin_ids:
        try:
            premium_send(admin_id, "🔓 Bot has been unlocked by admin.", emoji_key="success")
        except:
            pass


def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)


def broadcast_init_callback(call):
    admin_required_callback(call, _logic_broadcast_init)


def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    admin_required_callback(call, _logic_admin_panel)


def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "➕ Enter user ID to add as admin:", emoji_key="crown")
    bot.register_next_step_handler(msg, process_add_admin)


def process_add_admin(message):
    if message.from_user.id != OWNER_ID:
        premium_reply(message, "⚠️ Owner permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        if user_id in admin_ids:
            premium_reply(message, f"⚠️ User {user_id} is already admin.", emoji_key="error", code_words=[str(user_id)])
            return
        add_admin_db(user_id, OWNER_ID)
        premium_reply(message, f"✅ User {user_id} added as admin.", emoji_key="success", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "➖ Enter user ID to remove from admin:", emoji_key="crown")
    bot.register_next_step_handler(msg, process_remove_admin)


def process_remove_admin(message):
    if message.from_user.id != OWNER_ID:
        premium_reply(message, "⚠️ Owner permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        if user_id == OWNER_ID:
            premium_reply(message, "⚠️ Cannot remove owner.", emoji_key="error")
            return
        if remove_admin_db(user_id):
            premium_reply(message, f"✅ User {user_id} removed from admin.", emoji_key="success", code_words=[str(user_id)])
        else:
            premium_reply(message, f"⚠️ User {user_id} not admin.", emoji_key="error", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    admin_list = list(admin_ids)
    if admin_list:
        admin_text = "👑 **Admin List:**\n" + "\n".join([f"• `{admin_id}`" for admin_id in admin_list])
    else:
        admin_text = "No admins found."
    premium_send(call.message.chat.id, admin_text, emoji_key="crown")


def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    premium_send(call.message.chat.id, "💳 Subscription Management",
                 emoji_key="diamond", reply_markup=create_subscription_menu())


def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "➕ Enter user ID and days (e.g., `12345678 30`):", emoji_key="diamond")
    bot.register_next_step_handler(msg, process_add_subscription)


def process_add_subscription(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            premium_reply(message, "⚠️ Format: `user_id days`", emoji_key="error")
            return
        user_id = int(parts[0])
        days = int(parts[1])
        if days <= 0:
            premium_reply(message, "⚠️ Days must be positive.", emoji_key="error")
            return
        expiry = datetime.now() + timedelta(days=days)
        save_subscription(user_id, expiry)
        premium_reply(message, f"✅ User {user_id} subscribed for {days} days.\nExpires: {expiry.strftime('%Y-%m-%d %H:%M')}",
                      emoji_key="success", code_words=[str(user_id), str(days)])
        try:
            premium_send(user_id, f"🎉 Your subscription has been upgraded!\nExpires: {expiry.strftime('%Y-%m-%d %H:%M')}",
                         emoji_key="party")
        except:
            pass
    except ValueError:
        premium_reply(message, "⚠️ Invalid input.", emoji_key="error")


def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "➖ Enter user ID to remove subscription:", emoji_key="diamond")
    bot.register_next_step_handler(msg, process_remove_subscription)


def process_remove_subscription(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        remove_subscription_db(user_id)
        premium_reply(message, f"✅ Subscription removed for user {user_id}", emoji_key="success", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "🔍 Enter user ID to check subscription:", emoji_key="diamond")
    bot.register_next_step_handler(msg, process_check_subscription)


def process_check_subscription(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        if user_id in user_subscriptions:
            expiry = user_subscriptions[user_id]['expiry']
            days_left = (expiry - datetime.now()).days
            if days_left > 0:
                premium_reply(message, f"✅ User {user_id} has active subscription.\nExpires in {days_left} days.",
                              emoji_key="success", code_words=[str(user_id), str(days_left)])
            else:
                premium_reply(message, f"⚠️ User {user_id} subscription expired on {expiry.strftime('%Y-%m-%d %H:%M')}",
                              emoji_key="error", code_words=[str(user_id)])
        else:
            premium_reply(message, f"⚠️ No subscription for user {user_id}", emoji_key="error", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def user_management_callback(call):
    bot.answer_callback_query(call.id)
    premium_send(call.message.chat.id, "👥 User Management",
                 emoji_key="crown", reply_markup=create_user_management_menu())


def ban_user_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "🚫 Enter user ID and reason (e.g., `12345678 spam`):", emoji_key="error")
    bot.register_next_step_handler(msg, process_ban_user)


def process_ban_user(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        parts = message.text.strip().split(maxsplit=1)
        if len(parts) < 2:
            premium_reply(message, "⚠️ Format: `user_id reason`", emoji_key="error")
            return
        user_id = int(parts[0])
        reason = parts[1]
        if user_id in admin_ids:
            premium_reply(message, "⚠️ Cannot ban admin.", emoji_key="error")
            return
        if user_id == OWNER_ID:
            premium_reply(message, "⚠️ Cannot ban owner.", emoji_key="error")
            return
        ban_user_db(user_id, reason, message.from_user.id)
        premium_reply(message, f"✅ User {user_id} banned.\nReason: {reason}",
                      emoji_key="error", code_words=[str(user_id)])
        try:
            premium_send(user_id, f"🚫 You have been banned from the bot.\nReason: {reason}", emoji_key="error")
        except:
            pass
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def unban_user_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "✅ Enter user ID to unban:", emoji_key="success")
    bot.register_next_step_handler(msg, process_unban_user)


def process_unban_user(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        if unban_user_db(user_id):
            premium_reply(message, f"✅ User {user_id} unbanned.", emoji_key="success", code_words=[str(user_id)])
        else:
            premium_reply(message, f"⚠️ User {user_id} not banned.", emoji_key="error", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def user_info_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "📊 Enter user ID:", emoji_key="status")
    bot.register_next_step_handler(msg, process_user_info)


def process_user_info(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        info = f"📊 **User Info for {user_id}**\n\n"
        info += f"👤 Status: {'🟢 Active' if user_id in active_users else '🔴 Inactive'}\n"
        info += f"🚫 Banned: {'Yes' if user_id in banned_users else 'No'}\n"
        info += f"📂 Files: {len(user_files.get(user_id, []))}\n"
        info += f"📁 File Limit: {get_user_file_limit(user_id)}\n"
        if user_id in user_subscriptions:
            expiry = user_subscriptions[user_id]['expiry']
            days_left = (expiry - datetime.now()).days
            info += f"⭐ Subscription: {'Active' if days_left > 0 else 'Expired'}\n"
            info += f"⏳ Expires: {expiry.strftime('%Y-%m-%d %H:%M')}\n"
        else:
            info += f"⭐ Subscription: None\n"
        if user_id in admin_ids:
            info += f"🛡️ Admin: Yes\n"
        else:
            info += f"🛡️ Admin: No\n"
        premium_send(call.message.chat.id, info, emoji_key="status", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def all_users_callback(call):
    bot.answer_callback_query(call.id)
    users = list(active_users)
    if users:
        user_text = "👥 **All Active Users:**\n" + "\n".join([f"• `{user_id}`" for user_id in users[:50]])
        if len(users) > 50:
            user_text += f"\n... and {len(users) - 50} more users."
        premium_send(call.message.chat.id, user_text, emoji_key="crown")
    else:
        premium_send(call.message.chat.id, "No active users.", emoji_key="error")


def set_user_limit_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "🔧 Enter user ID and new limit (e.g., `12345678 10`):", emoji_key="idea")
    bot.register_next_step_handler(msg, process_set_user_limit)


def process_set_user_limit(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        parts = message.text.split()
        if len(parts) != 2:
            premium_reply(message, "⚠️ Format: `user_id limit`", emoji_key="error")
            return
        user_id = int(parts[0])
        limit = int(parts[1])
        if limit < 1:
            premium_reply(message, "⚠️ Limit must be >= 1.", emoji_key="error")
            return
        set_user_limit_db(user_id, limit, message.from_user.id)
        premium_reply(message, f"✅ File limit for user {user_id} set to {limit}",
                      emoji_key="success", code_words=[str(user_id), str(limit)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid input.", emoji_key="error")


def remove_user_limit_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "🗑️ Enter user ID to remove custom limit:", emoji_key="idea")
    bot.register_next_step_handler(msg, process_remove_user_limit)


def process_remove_user_limit(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    try:
        user_id = int(message.text.strip())
        remove_user_limit_db(user_id)
        premium_reply(message, f"✅ Custom limit removed for user {user_id}",
                      emoji_key="success", code_words=[str(user_id)])
    except ValueError:
        premium_reply(message, "⚠️ Invalid user ID.", emoji_key="error")


def admin_settings_callback(call):
    bot.answer_callback_query(call.id)
    premium_send(call.message.chat.id, "⚙️ Admin Settings",
                 emoji_key="crown", reply_markup=create_admin_settings_menu())


def system_info_callback(call):
    bot.answer_callback_query(call.id)
    import platform
    info = f"📊 **System Info**\n\n"
    info += f"🐍 Python: {sys.version.split()[0]}\n"
    info += f"💻 OS: {platform.system()} {platform.release()}\n"
    info += f"🔢 CPU Cores: {os.cpu_count()}\n"
    info += f"💾 RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB\n"
    info += f"💿 Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB\n"
    info += f"📁 Base Dir: {BASE_DIR}\n"
    info += f"📂 Upload Dir: {UPLOAD_BOTS_DIR}\n"
    info += f"💾 DB Path: {DATABASE_PATH}\n"
    premium_send(call.message.chat.id, info, emoji_key="status")


def bot_performance_callback(call):
    bot.answer_callback_query(call.id)
    active_bots = len(bot_scripts)
    running_bots = sum(1 for key in bot_scripts if is_bot_running(int(key.split('_')[0]), bot_scripts[key]['file_name']))
    info = f"📈 **Bot Performance**\n\n"
    info += f"🟢 Active Bots: {active_bots}\n"
    info += f"🟢 Running: {running_bots}\n"
    info += f"👥 Active Users: {len(active_users)}\n"
    info += f"📂 Total Files: {sum(len(files) for files in user_files.values())}\n"
    cpu_percent = psutil.cpu_percent(interval=1)
    mem_percent = psutil.virtual_memory().percent
    info += f"💻 CPU Usage: {cpu_percent}%\n"
    info += f"💾 RAM Usage: {mem_percent}%\n"
    premium_send(call.message.chat.id, info, emoji_key="status")


def cleanup_files_callback(call):
    bot.answer_callback_query(call.id, "🧹 Cleaning...")
    cleaned = 0
    for user_id, files in list(user_files.items()):
        user_folder = get_user_folder(user_id)
        for file_name, file_type in files:
            file_path = os.path.join(user_folder, file_name)
            if not os.path.exists(file_path):
                remove_user_file_db(user_id, file_name)
                cleaned += 1
    premium_send(call.message.chat.id, f"🧹 Cleaned {cleaned} stale file entries.",
                 emoji_key="success", code_words=[str(cleaned)])


def install_logs_callback(call):
    bot.answer_callback_query(call.id)
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT id, user_id, module_name, status, install_date FROM install_logs ORDER BY id DESC LIMIT 20')
    logs = c.fetchall()
    conn.close()
    if logs:
        log_text = "📋 **Recent Installation Logs**\n\n"
        for log in logs:
            log_text += f"#{log[0]} - User: {log[1]} - {log[2]} - {log[3]} - {log[4]}\n"
        premium_send(call.message.chat.id, log_text, emoji_key="status")
    else:
        premium_send(call.message.chat.id, "No installation logs found.", emoji_key="error")


def admin_install_callback(call):
    bot.answer_callback_query(call.id)
    _logic_admin_install(call.message)


def manage_mandatory_channels_callback(call):
    bot.answer_callback_query(call.id)
    _logic_manage_mandatory_channels(call.message)


def add_mandatory_channel_callback(call):
    bot.answer_callback_query(call.id)
    msg = premium_send(call.message.chat.id, "➕ Send channel username (e.g., @channel) or channel ID:", emoji_key="bell")
    bot.register_next_step_handler(msg, process_add_mandatory_channel)


def process_add_mandatory_channel(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    channel_input = message.text.strip()
    try:
        if channel_input.startswith('@') or channel_input.startswith('-100'):
            try:
                chat = bot.get_chat(channel_input)
                channel_name = chat.title
                channel_id = str(chat.id)
                channel_username = chat.username or channel_input
                save_mandatory_channel(channel_id, channel_username, channel_name, message.from_user.id)
                premium_reply(message, f"✅ Channel '{channel_name}' added as mandatory.",
                              emoji_key="success", code_words=[channel_name])
            except Exception as e:
                premium_reply(message, f"❌ Failed to get channel: {str(e)}", emoji_key="error")
        else:
            premium_reply(message, "⚠️ Invalid. Use @username or -100xxxxx.", emoji_key="error")
    except Exception as e:
        premium_reply(message, f"❌ Error: {str(e)}", emoji_key="error")


def remove_mandatory_channel_callback(call):
    bot.answer_callback_query(call.id)
    if mandatory_channels:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for channel_id, info in mandatory_channels.items():
            name = info.get('name', 'Unknown')
            markup.add(types.InlineKeyboardButton(f"➖ Remove {name}", callback_data=f'remove_channel_{channel_id}'))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='manage_mandatory_channels'))
        premium_send(call.message.chat.id, "Select channel to remove:", emoji_key="bell", reply_markup=markup)
    else:
        premium_send(call.message.chat.id, "No mandatory channels to remove.", emoji_key="error")


def process_remove_channel(call):
    channel_id = call.data.replace('remove_channel_', '')
    if remove_mandatory_channel_db(channel_id):
        bot.answer_callback_query(call.id, "✅ Channel removed.")
        premium_send(call.message.chat.id, "✅ Channel removed from mandatory list.", emoji_key="success")
    else:
        bot.answer_callback_query(call.id, "❌ Failed to remove.")


def list_mandatory_channels_callback(call):
    bot.answer_callback_query(call.id)
    if mandatory_channels:
        text = "📢 **Mandatory Channels:**\n\n"
        for channel_id, info in mandatory_channels.items():
            name = info.get('name', 'Unknown')
            username = info.get('username', 'N/A')
            text += f"• {name} (@{username.replace('@', '')})\n"
            text += f"  ID: `{channel_id}`\n\n"
        premium_send(call.message.chat.id, text, emoji_key="bell")
    else:
        premium_send(call.message.chat.id, "No mandatory channels set.", emoji_key="error")


def check_subscription_status_callback(call):
    user_id = call.from_user.id
    is_subscribed, not_joined = check_mandatory_subscription(user_id)
    if is_subscribed:
        bot.answer_callback_query(call.id, "✅ You have joined all required channels!", show_alert=True)
        back_to_main_callback(call)
    else:
        subscription_message, markup = create_subscription_check_message(not_joined)
        bot.answer_callback_query(call.id)
        try:
            premium_edit(call.message.chat.id, call.message.message_id, subscription_message, reply_markup=markup)
        except:
            premium_send(call.message.chat.id, subscription_message, reply_markup=markup)


# ============================================================
# PENDING FILES
# ============================================================
def view_pending_files_callback(call):
    view_pending_files(call.message)


def view_pending_files(message):
    pending_files = get_pending_files_for_admin()
    if not pending_files:
        premium_send(message.chat.id, "📋 No pending files for review.", emoji_key="upload")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    for file_id, user_id, file_name, file_type, upload_date in pending_files:
        btn_text = f"📄 {file_name} ({file_type}) - User: {user_id}"
        markup.row(
            types.InlineKeyboardButton(f"✅ Approve", callback_data=f'approve_pending_{file_id}'),
            types.InlineKeyboardButton(f"❌ Reject", callback_data=f'reject_pending_{file_id}')
        )
        markup.row(types.InlineKeyboardButton(f"📄 {file_name} ({file_type}) - User: {user_id}", callback_data=f'view_pending_{file_id}'))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
    premium_send(message.chat.id, "📋 **Pending Files for Review:**\nClick Approve/Reject.",
                 emoji_key="upload", reply_markup=markup)


def approve_pending_file_callback(call):
    try:
        file_id = int(call.data.replace('approve_pending_', ''))
        pending_data = get_pending_file(file_id)
        if not pending_data:
            bot.answer_callback_query(call.id, "❌ File not found.", show_alert=True)
            return
        user_id = pending_data['user_id']
        file_name = pending_data['file_name']
        file_content = pending_data['file_content']
        file_type = pending_data['file_type']
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        logger.info(f"Admin {call.from_user.id} approved {file_name} for {user_id}")
        if file_type == 'zip':
            threading.Thread(target=process_zip_file_with_content,
                             args=(file_content, user_id, file_name, call.message)).start()
        elif file_type == 'py':
            handle_py_file(file_path, user_id, user_folder, file_name, call.message)
        elif file_type == 'js':
            handle_js_file(file_path, user_id, user_folder, file_name, call.message)
        delete_pending_file(file_id)
        try:
            premium_send(user_id, f"✅ Your file `{file_name}` approved by admin and is now running!",
                         emoji_key="success", code_words=[file_name])
        except:
            pass
        bot.answer_callback_query(call.id, "✅ Approved.")
        view_pending_files_callback(call)
    except Exception as e:
        logger.error(f"approve error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)}", show_alert=True)


def reject_pending_file_callback(call):
    try:
        file_id = int(call.data.replace('reject_pending_', ''))
        pending_data = get_pending_file(file_id)
        if not pending_data:
            bot.answer_callback_query(call.id, "❌ File not found.", show_alert=True)
            return
        user_id = pending_data['user_id']
        file_name = pending_data['file_name']
        delete_pending_file(file_id)
        try:
            premium_send(user_id, f"❌ Your file `{file_name}` was rejected by admin.",
                         emoji_key="error", code_words=[file_name])
        except:
            pass
        bot.answer_callback_query(call.id, "❌ Rejected.")
        view_pending_files_callback(call)
    except Exception as e:
        logger.error(f"reject error: {e}", exc_info=True)
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)}", show_alert=True)


# ============================================================
# BROADCAST
# ============================================================
broadcast_message_cache = {}


def process_broadcast_message(message):
    if message.from_user.id not in admin_ids:
        premium_reply(message, "⚠️ Admin permissions required.", emoji_key="error")
        return
    if message.text.lower() == '/cancel':
        premium_reply(message, "❌ Broadcast cancelled.", emoji_key="error")
        return
    broadcast_message_cache[message.from_user.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_broadcast_{message.from_user.id}"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
    )
    premium_reply(message, f"📢 **Broadcast Message:**\n\n{message.text}\n\nClick Confirm to send to all users.",
                  emoji_key="broadcast", reply_markup=markup)


def handle_confirm_broadcast(call):
    admin_id = int(call.data.replace('confirm_broadcast_', ''))
    if call.from_user.id != admin_id:
        bot.answer_callback_query(call.id, "⚠️ Not authorized.", show_alert=True)
        return
    if admin_id not in broadcast_message_cache:
        bot.answer_callback_query(call.id, "❌ No broadcast found.")
        return
    message_text = broadcast_message_cache[admin_id]
    del broadcast_message_cache[admin_id]
    bot.answer_callback_query(call.id, "📢 Broadcasting...")
    success_count = 0
    fail_count = 0
    for user_id in list(active_users):
        try:
            premium_send(user_id, message_text, emoji_key="broadcast")
            success_count += 1
            time.sleep(0.1)
        except Exception as e:
            fail_count += 1
            logger.error(f"Failed broadcast to {user_id}: {e}")
    premium_send(call.message.chat.id, f"📢 Broadcast complete!\n✅ Sent: {success_count}\n❌ Failed: {fail_count}",
                 emoji_key="broadcast", code_words=[str(success_count), str(fail_count)])


def handle_cancel_broadcast(call):
    admin_id = call.from_user.id
    if admin_id in broadcast_message_cache:
        del broadcast_message_cache[admin_id]
    bot.answer_callback_query(call.id, "❌ Broadcast cancelled.")
    premium_edit(call.message.chat.id, call.message.message_id, "❌ Broadcast cancelled.", emoji_key="error")


# ============================================================
# CLEANUP
# ============================================================
def cleanup():
    logger.warning("Shutdown. Cleaning up...")
    script_keys_to_stop = list(bot_scripts.keys())
    if not script_keys_to_stop:
        return
    for key in script_keys_to_stop:
        if key in bot_scripts:
            kill_process_tree(bot_scripts[key])
    logger.warning("Cleanup finished.")


atexit.register(cleanup)


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    logger.info("=" * 50 + "\n🤖 ALEXA Hosting Bot Starting Up...\n"
                + f"🐍 Python: {sys.version.split()[0]}\n"
                + f"🔧 Base Dir: {BASE_DIR}\n"
                + f"📁 Upload Dir: {UPLOAD_BOTS_DIR}\n"
                + f"📊 Data Dir: {IROTECH_DIR}\n"
                + f"👑 Owner ID: {OWNER_ID}\n"
                + f"🛡️ Admins: {len(admin_ids)}\n"
                + f"🚫 Banned: {len(banned_users)}\n"
                + f"📢 Channels: {len(mandatory_channels)}\n"
                + f"🔥 Auto Version Detection: Active\n"
                + "=" * 50)
    keep_alive()
    logger.info("🚀 Starting polling...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            logger.warning("Polling ReadTimeout. Restarting in 5s...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"ConnectionError: {ce}. Retrying in 15s...")
            time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable: {e}", exc_info=True)
            logger.info("Restarting in 30s...")
            time.sleep(30)
        finally:
            time.sleep(1)