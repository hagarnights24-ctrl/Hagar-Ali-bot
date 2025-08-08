import os
import io
import threading
import requests
from flask import Flask
import telebot
from openai import OpenAI

# ====== ENV ======
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_TOKEN env var")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY env var")

# ====== Clients ======
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# ====== Telegram handlers ======
@bot.message_handler(commands=['start', 'help'])
def on_start(message):
    bot.reply_to(
        message,
        "היי! אני כאן 😎\n"
        "• שלחו טקסט – אענה בעזרת בינה מלאכותית\n"
        "• /img תיאור – אייצר תמונה לפי הטקסט (לדוגמה: /img חתול בחללית)"
    )

@bot.message_handler(commands=['img'])
def on_img(message):
    prompt = message.text.replace('/img', '', 1).strip()
    if not prompt:
        bot.reply_to(message, "תנו תיאור לתמונה אחרי /img 🙂")
        return
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        # יצירת תמונה
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        url = img.data[0].url  # לינק זמני לתמונה
        # מורידים ושולחים לטלגרם
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        bot.send_photo(message.chat.id, photo=io.BytesIO(r.content), caption=f"✨ {prompt}")
    except Exception as e:
        bot.reply_to(message, f"קרתה שגיאה ביצירת תמונה: {e}")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def on_text(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "את עוזרת חכמה, חיובית וקצרה בתשובות."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=400
        )
        reply = completion.choices[0].message.content.strip()
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"קרתה שגיאה: {e}")

# ====== Flask (ל-Render צריך פורט פתוח) ======
app = Flask(__name__)

@app.get("/")
@app.get("/health")
def health():
    return "OK", 200

def start_polling():
    # ריצה אינסופית של הבוט
    bot.infinity_polling(timeout=60, skip_pending=True)

if __name__ == "__main__":
    # מפעילים את טלגרם ברקע + מאזינים לפורט עבור Render
    threading.Thread(target=start_polling, daemon=True).start()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)

