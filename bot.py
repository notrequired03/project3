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
    api_key = os.environ.get("GEMINI_API_KEY") or cfg.get("gemini_api_key")

    if not api_key:
        raise ValueError("Gemini API key is missing. Please set it in the Dashboard.")

    if not HAS_GENAI_SDK:
        raise ImportError("google-genai SDK is not installed.")

    client = genai.Client(api_key=api_key)

    full_system = system_instruction or cfg.get("persona_prompt")

    models_to_try = ["gemini-3.7-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config={
                    "system_instruction": full_system,
                    "temperature": 0.9,
                    "max_output_tokens": 500,
                }
            )
            text = response.text.strip().strip('"\'')
            return text
        except Exception as e:
            err_str = str(e)
            if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
                error_msg = "Invalid Gemini API Key! Please get a new free API key at https://aistudio.google.com/ and set it in your Dashboard or Render Environment Variables."
                add_log(error_msg, level="ERROR")
                raise ValueError(error_msg)

            last_error = e
            add_log(f"Model {model_name} call failed: {e}. Trying next model...", level="WARNING")

    raise last_error


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
        "Savage roast of paying $30/month for Tinder Gold just to get 0 replies, vs meeting real people instantly for free on chathere.online",
        "Mocking people spending 3 hours in dead Discord server waiting rooms vs 0-lag instant video chat on chathere.online",
        "Ryanair-style priority boarding announcement: Priority queue for people who want instant video chat without 15 sign-up forms is chathere.online",
        "Unhinged roast of people posting 'RIP Omegle' in 2026 like bro move on, chathere.online was right here the whole time",
        "Brutal joke about people complaining 'nobody texts me back' while ignoring 10,000 active people on chathere.online right now",
        "Watching a 4-hour Twitch stream just to feel human interaction vs hopping on chathere.online in 2 seconds",
        "Savage relationship advice: Your ex is not coming back, but stranger video chat on chathere.online is instant and free",
        "Unhinged Ryanair travel joke: Imagine paying $100 for plane tickets when you can travel the world meeting random strangers on chathere.online from bed",
        "Sarcastic roast of people who get nervous ordering coffee but want to make new friends: Start easy on chathere.online",
        "Mocking dead group chats where the last message was 'hi' 3 weeks ago vs non-stop live action on chathere.online"
    ]
    selected_topic = random.choice(topics)
    prompt = (
        f"Topic instruction: {selected_topic}\n\n"
        "Write ONE viral, unhinged, savagely funny Ryanair-style tweet.\n"
        "CRITICAL REQUIREMENTS:\n"
        "- MUST be between 100 and 220 characters.\n"
        "- MUST be a complete, fully-formed punchline ending with punctuation (. or ! or ?).\n"
        "- DO NOT stop or cut off mid-sentence.\n"
        "- Include 'chathere.online' or '#chathere' naturally."
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
