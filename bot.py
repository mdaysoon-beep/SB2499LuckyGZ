"""
SB244Luckybot — Telegram Bot (Hindi)
Sends daily productivity and focus tips in Hindi, on request or subscription.

Run locally:
    export BOT_TOKEN="your-token-from-botfather"
    python bot.py

Deployed on Railway, BOT_TOKEN is read from an environment variable you set
in the Railway dashboard (Variables tab) — never hard-code it in this file.
"""

import json
import logging
import os
import random
from datetime import time as dtime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

SUBSCRIBERS_FILE = "subscribers.json"

# ---------------------------------------------------------------------------
# CONTENT LIBRARY (Hindi) — add new entries any time, no other code needs to change
# ---------------------------------------------------------------------------

TIPS = [
    {
        "title": "⏱️ दो-मिनट का नियम",
        "body": (
            "अगर कोई काम दो मिनट से कम समय में हो सकता है, तो उसे लिस्ट में डालने "
            "के बजाय तुरंत कर लें।\n\n"
            "छोटे काम टालने से दिमाग में उलझन ज़्यादा बढ़ती है, बनिस्बत उन्हें "
            "पूरा करने में लगने वाले समय के।"
        ),
    },
    {
        "title": "🎯 एक समय में एक काम",
        "body": (
            "बार-बार काम बदलने से असली समय और ध्यान दोनों की कीमत चुकानी पड़ती है।\n\n"
            "एक समय में एक ही काम पर ध्यान केंद्रित करें, कई कामों को एक साथ "
            "जग्गल करने के बजाय।"
        ),
    },
    {
        "title": "🧩 ज़रूरी बनाम तुरंत",
        "body": (
            "हर काम को चार हिस्सों में बांटें: ज़रूरी+तुरंत, ज़रूरी पर तुरंत नहीं, "
            "तुरंत पर ज़रूरी नहीं, और न ज़रूरी न तुरंत।\n\n"
            "ज़्यादातर लोग 'तुरंत पर ज़रूरी नहीं' वाले कामों में समय बर्बाद करते "
            "हैं, जो व्यस्त तो लगते हैं पर असल प्रगति नहीं देते।"
        ),
    },
    {
        "title": "🌱 आदतों को जोड़ना",
        "body": (
            "किसी नई आदत को पुरानी आदत से जोड़ें: 'जब मैं [पुरानी आदत] करूं, "
            "तब मैं [नई आदत] भी करूंगा।'\n\n"
            "पहले से मौजूद रूटीन को ट्रिगर बनाने से नई आदत बनाना आसान हो जाता है।"
        ),
    },
    {
        "title": "🔋 अपने सबसे अच्छे घंटों की रक्षा करें",
        "body": (
            "ज़्यादातर लोगों के दिन में 2-4 घंटे ऐसे होते हैं जब ध्यान और ऊर्जा "
            "सबसे ज़्यादा होती है।\n\n"
            "उस समय को अपने सबसे ज़रूरी काम के लिए बचाएं — ईमेल या मीटिंग के लिए नहीं।"
        ),
    },
    {
        "title": "📝 आज रात कल की योजना बनाएं",
        "body": (
            "रात को ही कल के तीन सबसे ज़रूरी काम तय कर लेने से सुबह सोचने में "
            "लगने वाली ऊर्जा बचती है।\n\n"
            "आप दिन की शुरुआत पहले से तय दिशा के साथ करते हैं।"
        ),
    },
    {
        "title": "🛑 'नहीं' कहने की ताकत",
        "body": (
            "किसी नई ज़िम्मेदारी को 'हां' कहना अक्सर अपनी ही प्राथमिकताओं को "
            "'नहीं' कहना होता है।\n\n"
            "अपने समय को सोच-समझकर बचाना स्वार्थी नहीं, बल्कि ध्यान केंद्रित "
            "काम के लिए ज़रूरी है।"
        ),
    },
    {
        "title": "🔄 हफ्ते में एक बार समीक्षा करें",
        "body": (
            "हफ्ते में एक छोटी समीक्षा — क्या काम आया, क्या नहीं — कई ऐसे पैटर्न "
            "दिखाती है जो रोज़ की योजना में छूट जाते हैं।\n\n"
            "हफ्ते के पंद्रह मिनट घंटों का समय बचा सकते हैं।"
        ),
    },
]

WELCOME_MESSAGE = (
    "👋 स्वागत है!\n\n"
    "यह बॉट आपको फोकस, प्रोडक्टिविटी और बेहतर आदतें बनाने के लिए छोटे, "
    "व्यावहारिक सुझाव भेजता है।\n\n"
    "कमांड्स:\n"
    "/tip — एक रैंडम सुझाव पाएं\n"
    "/subscribe — रोज़ाना सुझाव अपने आप पाएं\n"
    "/unsubscribe — रोज़ाना सुझाव बंद करें\n"
    "/help — यह मैसेज फिर से देखें"
)

# ---------------------------------------------------------------------------
# SUBSCRIBER STORAGE
# ---------------------------------------------------------------------------


def load_subscribers() -> set:
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_subscribers(subscribers: set) -> None:
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribers), f)


subscribers = load_subscribers()

# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE)


async def tip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pick = random.choice(TIPS)
    text = f"{pick['title']}\n\n{pick['body']}"
    await update.message.reply_text(text)


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        await update.message.reply_text("आप पहले से ही रोज़ाना सुझावों के लिए सब्सक्राइब हैं।")
        return
    subscribers.add(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text(
        "✅ सब्सक्राइब हो गया! अब आपको रोज़ एक सुझाव मिलेगा। कभी भी बंद करने के लिए /unsubscribe भेजें।"
    )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in subscribers:
        await update.message.reply_text("आप अभी सब्सक्राइब नहीं हैं।")
        return
    subscribers.discard(chat_id)
    save_subscribers(subscribers)
    await update.message.reply_text("रोज़ाना सुझाव बंद कर दिए गए हैं।")


async def send_daily_tip(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Runs once a day, sends one random tip to every subscriber."""
    if not subscribers:
        return
    pick = random.choice(TIPS)
    text = f"{pick['title']}\n\n{pick['body']}"
    for chat_id in list(subscribers):
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as exc:
            logger.warning("Failed to send to %s: %s", chat_id, exc)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is not set. "
            "Set it locally with `export BOT_TOKEN=...` or in Railway's Variables tab."
        )

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tip", tip))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    # Daily tip at 09:00 UTC — adjust the hour to suit your audience's timezone.
    job_queue = application.job_queue
    job_queue.run_daily(send_daily_tip, time=dtime(hour=9, minute=0))

    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
