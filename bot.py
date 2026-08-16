import asyncio
import os
import random
import time
from config import get_config, add_log

# Import Google GenAI SDK (2026 Google Gen AI SDK)
try:
    from google import genai
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

# Import Twikit
try:
    from twikit import Client
    HAS_TWIKIT = True
except ImportError:
    HAS_TWIKIT = False


def generate_ai_text(prompt_text, system_instruction=None):
    """
    Generates text using Google GenAI SDK with gemini-3.6-flash or gemini-2.5-flash.
    """
    cfg = get_config()
    api_key = cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key is missing. Please set it in the Dashboard.")

    if not HAS_GENAI_SDK:
        raise ImportError("google-genai SDK is not installed.")

    client = genai.Client(api_key=api_key)

    full_system = system_instruction or cfg.get("persona_prompt")

    # Try gemini-3.6-flash first, fallback to gemini-2.5-flash if needed
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt_text,
            config={
                "system_instruction": full_system,
                "temperature": 0.9,
                "max_output_tokens": 280,
            }
        )
        return response.text.strip()
    except Exception as e:
        err_str = str(e)
        if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
            error_msg = "Invalid Gemini API Key! Please get a new free API key at https://aistudio.google.com/ and set it in your Dashboard or Render Environment Variables."
            add_log(error_msg, level="ERROR")
            raise ValueError(error_msg)

        add_log(f"gemini-3.6-flash call failed, trying gemini-2.5-flash: {e}", level="WARNING")
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text,
                config={
                    "system_instruction": full_system,
                    "temperature": 0.9,
                    "max_output_tokens": 280,
                }
            )
            return response.text.strip()
        except Exception as e2:
            err_str2 = str(e2)
            if "API_KEY_INVALID" in err_str2 or "API key not valid" in err_str2:
                error_msg = "Invalid Gemini API Key! Please get a new free API key at https://aistudio.google.com/ and set it in your Dashboard or Render Environment Variables."
                add_log(error_msg, level="ERROR")
                raise ValueError(error_msg)
            raise e2


async def get_twikit_client():
    """
    Initializes and authenticates Twikit client with cookie persistence.
    """
    if not HAS_TWIKIT:
        raise ImportError("twikit is not installed.")

    cfg = get_config()
    username = cfg.get("twitter_username")
    email = cfg.get("twitter_email")
    password = cfg.get("twitter_password")

    if not username or not password:
        raise ValueError("Twitter credentials missing. Please set username & password in Dashboard.")

    tw_client = Client("en-US")

    cookie_file = "cookies.json"
    if os.path.exists(cookie_file):
        try:
            tw_client.load_cookies(cookie_file)
            add_log("Loaded Twitter session from cookies.json")
            return tw_client
        except Exception as e:
            add_log(f"Failed to load cookies.json, re-authenticating: {e}", level="WARNING")

    add_log(f"Logging in to Twitter as @{username}...")
    await tw_client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )
    tw_client.save_cookies(cookie_file)
    add_log("Successfully logged in to Twitter and saved cookies.json")
    return tw_client


def generate_meme_tweet_content():
    """
    Generates a Ryanair-style hilarious post about chathere.online
    """
    topics = [
        "Roast people spending 4 hours scrolling TikTok when they could talk to real humans instantly on chathere.online",
        "Mock legacy chat apps, laggy Discord voice calls, or awkward Zoom meetings vs 0-lag chathere.online",
        "A funny Ryanair-style meme quote about modern dating apps vs randomly connecting on chathere.online",
        "Sarcastic advice for people who say 'I'm bored online' while ignoring chathere.online",
        "Funny unhinged corporate banter comparing high flight prices to chathere.online being 100% free with no sign-up",
        "A hilarious roast of people who still miss Omegle when chathere.online exists"
    ]
    selected_topic = random.choice(topics)
    prompt = (
        f"Topic: {selected_topic}\n\n"
        "Write a single viral, hilarious tweet (max 220 characters). Make it unhinged, snappy, sarcastic, and funny like Ryanair's Twitter. "
        "Include 'chathere.online' or '#chathere' naturally in the tweet. Do NOT use emojis excessively."
    )
    return generate_ai_text(prompt)


def generate_reply_content(original_tweet, author_username):
    """
    Generates a witty, cheeky reply to a target user tweet.
    """
    prompt = (
        f"User @{author_username} tweeted: \"{original_tweet}\"\n\n"
        "Write a short, witty, hilarious Ryanair-style reply (max 180 characters) roasting their situation or suggesting "
        "they check out chathere.online to cure their boredom/loneliness. Be playful, slightly unhinged, but funny."
    )
    return generate_ai_text(prompt)


async def async_post_tweet(text_content=None):
    """
    Async task to post a tweet via Twikit
    """
    try:
        tw_client = await get_twikit_client()
        if not text_content:
            text_content = generate_meme_tweet_content()
        
        # Clean text
        text_content = text_content.strip('"\'')
        add_log(f"Publishing Tweet: {text_content}")

        tweet = await tw_client.create_tweet(text=text_content)
        add_log(f"SUCCESS: Tweet published! (ID: {tweet.id})")
        
        from config import increment_stat
        increment_stat("total_posts")
        
        return {"status": "success", "tweet_id": tweet.id, "text": text_content}
    except Exception as e:
        error_msg = f"ERROR in posting tweet: {e}"
        add_log(error_msg, level="ERROR")
        return {"status": "error", "error": str(e)}


async def async_auto_reply():
    """
    Async task to search keywords and reply to relevant tweets
    """
    cfg = get_config()
    if not cfg.get("auto_reply_enabled"):
        add_log("Auto-reply is disabled in configuration.")
        return

    keywords = cfg.get("target_keywords", ["omegle alternative", "bored online"])
    if not keywords:
        return

    target_keyword = random.choice(keywords)
    add_log(f"Searching Twitter for target keyword: '{target_keyword}'...")

    try:
        tw_client = await get_twikit_client()
        search_results = await tw_client.search_tweet(target_keyword, product='Latest')
        
        if not search_results:
            add_log(f"No recent tweets found for '{target_keyword}'.")
            return

        # Filter out tweets from self or retweets
        username = cfg.get("twitter_username", "").lower()
        candidates = [
            t for t in search_results 
            if hasattr(t, 'user') and t.user.screen_name.lower() != username
        ]

        if not candidates:
            add_log("No suitable tweets found to reply to.")
            return

        target_tweet = random.choice(candidates[:5])
        author = target_tweet.user.screen_name
        tweet_text = target_tweet.text

        add_log(f"Found tweet by @{author}: '{tweet_text[:50]}...'")

        reply_text = generate_reply_content(tweet_text, author)
        add_log(f"Replying to @{author}: {reply_text}")

        await target_tweet.reply(text=reply_text)
        add_log(f"SUCCESS: Replied to @{author}!")

        from config import increment_stat
        increment_stat("total_replies")

        # Safety delay
        delay = random.randint(30, 90)
        add_log(f"Safety cooldown active: waiting {delay}s...")
        await asyncio.sleep(delay)

    except Exception as e:
        add_log(f"ERROR in auto-reply: {e}", level="ERROR")


def execute_post_job():
    """
    Synchronous wrapper for APScheduler job
    """
    cfg = get_config()
    if not cfg.get("bot_enabled"):
        add_log("Scheduler triggered, but Bot is currently DISABLED. Skipping post.")
        return
    
    add_log("Starting scheduled auto-post job...")
    asyncio.run(async_post_tweet())

    if cfg.get("auto_reply_enabled"):
        add_log("Starting scheduled auto-reply job...")
        asyncio.run(async_auto_reply())
