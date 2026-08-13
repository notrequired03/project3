import asyncio
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from config import get_config, update_config, get_masked_config, add_log
from bot import execute_post_job, async_post_tweet, generate_meme_tweet_content

app = Flask(__name__)

JOB_ID = "twitter_bot_job"
scheduler = None
scheduler_started = False

def get_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(daemon=True)
    return scheduler

def update_scheduler_job():
    """
    Adds or updates the APScheduler interval job based on config settings.
    """
    cfg = get_config()
    is_enabled = cfg.get("bot_enabled", False)
    interval_mins = int(cfg.get("post_interval_minutes", 30))

    if interval_mins < 5:
        interval_mins = 5

    sched = get_scheduler()
    existing_job = sched.get_job(JOB_ID)

    if is_enabled:
        if existing_job:
            sched.reschedule_job(JOB_ID, trigger='interval', minutes=interval_mins)
            add_log(f"Rescheduled bot posting job to run every {interval_mins} minutes.")
        else:
            sched.add_job(
                execute_post_job,
                trigger='interval',
                minutes=interval_mins,
                id=JOB_ID,
                replace_existing=True
            )
            add_log(f"Started bot posting job (running every {interval_mins} minutes).")
    else:
        if existing_job:
            sched.remove_job(JOB_ID)
            add_log("Stopped scheduled bot posting job.")

def start_scheduler():
    global scheduler_started
    sched = get_scheduler()
    if not scheduler_started:
        if not sched.running:
            sched.start()
            add_log("APScheduler background service started.")
        scheduler_started = True
    update_scheduler_job()

@app.before_request
def ensure_scheduler_running():
    global scheduler_started
    if not scheduler_started:
        try:
            start_scheduler()
        except Exception as e:
            print(f"Error starting scheduler: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    cfg = get_config()
    correct_user = cfg.get("admin_username", "1511761010")
    correct_pass = cfg.get("admin_password", "charan@123")
    
    if username == correct_user and password == correct_pass:
        add_log(f"Admin user '{username}' logged in successfully.")
        return jsonify({
            "status": "success",
            "message": "Login successful! Welcome to ChatHere Bot Dashboard.",
            "user": username
        })
    else:
        add_log(f"Failed login attempt for username '{username}'.", level="WARNING")
        return jsonify({
            "status": "error",
            "message": "Invalid Username or Password!"
        }), 401

@app.route("/api/stats", methods=["GET"])
def api_stats():
    cfg = get_config()
    return jsonify({
        "status": "success",
        "stats": cfg.get("stats", {}),
        "twitter_username": cfg.get("twitter_username", "chathere_online"),
        "bot_enabled": cfg.get("bot_enabled", False),
        "post_interval_minutes": cfg.get("post_interval_minutes", 30),
        "auto_reply_enabled": cfg.get("auto_reply_enabled", True)
    })

@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify({
        "status": "success",
        "config": get_masked_config(),
        "scheduler_active": get_scheduler().get_job(JOB_ID) is not None
    })

@app.route("/api/config", methods=["POST"])
def api_save_config():
    data = request.json or {}
    
    # Filter updated fields
    updated_fields = {}
    
    if "twitter_username" in data:
        updated_fields["twitter_username"] = data["twitter_username"].strip()
    if "twitter_email" in data:
        updated_fields["twitter_email"] = data["twitter_email"].strip()
    if "twitter_password" in data and data["twitter_password"] != "••••••••":
        updated_fields["twitter_password"] = data["twitter_password"]
    if "gemini_api_key" in data and not data["gemini_api_key"].startswith("••••"):
        updated_fields["gemini_api_key"] = data["gemini_api_key"].strip()
    if "post_interval_minutes" in data:
        try:
            updated_fields["post_interval_minutes"] = int(data["post_interval_minutes"])
        except ValueError:
            pass
    if "auto_reply_enabled" in data:
        updated_fields["auto_reply_enabled"] = bool(data["auto_reply_enabled"])
    if "target_keywords" in data:
        if isinstance(data["target_keywords"], list):
            updated_fields["target_keywords"] = [k.strip() for k in data["target_keywords"] if k.strip()]
        elif isinstance(data["target_keywords"], str):
            updated_fields["target_keywords"] = [k.strip() for k in data["target_keywords"].split(",") if k.strip()]
    if "persona_prompt" in data:
        updated_fields["persona_prompt"] = data["persona_prompt"].strip()

    new_cfg = update_config(updated_fields)
    update_scheduler_job()
    add_log("Configuration settings updated successfully.")
    
    return jsonify({
        "status": "success",
        "message": "Settings saved!",
        "config": get_masked_config()
    })

@app.route("/api/toggle_bot", methods=["POST"])
def api_toggle_bot():
    data = request.json or {}
    enable = data.get("enable", False)
    
    update_config({"bot_enabled": enable})
    update_scheduler_job()
    
    status_str = "ENABLED" if enable else "DISABLED"
    add_log(f"Bot has been {status_str} by user.")
    
    return jsonify({
        "status": "success",
        "bot_enabled": enable,
        "scheduler_active": scheduler.get_job(JOB_ID) is not None
    })

@app.route("/api/post_now", methods=["POST"])
def api_post_now():
    add_log("Manual 'Post Now' triggered from Web Dashboard...")
    data = request.json or {}
    custom_text = data.get("custom_text")
    
    try:
        result = asyncio.run(async_post_tweet(text_content=custom_text))
        return jsonify(result)
    except Exception as e:
        error_msg = str(e)
        add_log(f"Manual post failed: {error_msg}", level="ERROR")
        return jsonify({"status": "error", "error": error_msg}), 500

@app.route("/api/preview_tweet", methods=["POST"])
def api_preview_tweet():
    try:
        sample_text = generate_meme_tweet_content()
        return jsonify({"status": "success", "preview": sample_text})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/logs", methods=["GET"])
def api_logs():
    cfg = get_config()
    return jsonify({
        "status": "success",
        "logs": cfg.get("logs", [])
    })

if __name__ == "__main__":
    print("==========================================", flush=True)
    print("Starting Flask Web Server on http://127.0.0.1:5000 ...", flush=True)
    print("==========================================", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
