import os
import json
import threading
from datetime import datetime

CONFIG_FILE = "config.json"
lock = threading.RLock()

DEFAULT_CONFIG = {
    "admin_username": "1511761010",
    "admin_password": "charan@123",
    "twitter_username": "chathere_online",
    "twitter_email": "",
    "twitter_password": "Charan@123",
    "gemini_api_key": "AIzaSyAgrVtcZuh4aXUAlZL4kJHbbpQxtWXz_jw",
    "bot_enabled": False,
    "post_interval_minutes": 30,
    "auto_reply_enabled": True,
    "target_keywords": [
        "omegle alternative",
        "bored online",
        "meet new people",
        "discord server dead",
        "random video chat",
        "chatroulette"
    ],
    "brand_url": "https://chathere.online",
    "persona_prompt": (
        "You are the unhinged, hilarious, savagely witty social media manager for chathere.online "
        "(a modern, instant, zero-lag random video & text chat platform where people connect instantly for free without signup). "
        "Your tone is heavily inspired by Ryanair's official Twitter account: sarcastic, self-aware, meme-heavy, snappy, "
        "trolling rival legacy chat sites (like dead Omegle clones, laggy Discord calls, awkward video apps), "
        "and roasting relatable internet behavior. Keep tweets under 240 characters. ALWAYS include or reference chathere.online "
        "or #chathere in a clever/funny way."
    ),
    "stats": {
        "total_posts": 0,
        "total_replies": 0,
        "last_post_time": None
    },
    "logs": []
}

def get_config():
    with lock:
        if not os.path.exists(CONFIG_FILE):
            save_config_data(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()

def save_config_data(data):
    with lock:
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

def update_config(new_fields):
    cfg = get_config()
    cfg.update(new_fields)
    save_config_data(cfg)
    return cfg

def increment_stat(stat_name):
    with lock:
        cfg = get_config()
        stats = cfg.get("stats", {"total_posts": 0, "total_replies": 0, "last_post_time": None})
        stats[stat_name] = stats.get(stat_name, 0) + 1
        stats["last_post_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cfg["stats"] = stats
        save_config_data(cfg)

def add_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"timestamp": timestamp, "level": level, "message": message}
    with lock:
        cfg = get_config()
        logs = cfg.get("logs", [])
        logs.insert(0, entry)
        cfg["logs"] = logs[:100]
        save_config_data(cfg)
    print(f"[{timestamp}] [{level}] {message}")

def get_masked_config():
    cfg = get_config()
    masked = cfg.copy()
    if masked.get("twitter_password"):
        masked["twitter_password"] = "••••••••"
    if masked.get("admin_password"):
        masked["admin_password"] = "••••••••"
    if masked.get("gemini_api_key"):
        key = masked["gemini_api_key"]
        masked["gemini_api_key"] = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "••••••••"
    return masked
