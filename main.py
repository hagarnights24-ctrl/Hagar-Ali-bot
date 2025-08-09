import os
from flask import Flask, request, jsonify
import telebot
import requests

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # ודא שהגדרת ב-Render
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# דף בית לבדיקה מהדפדפן
@app.get("/")
def home():
    return "Bot is running!", 200

# זה הנתיב שטלגרם יקרא לו
@app.post("/webhook")
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
    except Exception as e:
        print("webhook error:", e)
    return jsonify(ok=True)

# תגובה בסיסית לכל טקסט
@bot.message_handler(content_types=["text"])
def echo(msg):
    bot.reply_to(msg, f"קיבלתי: {msg.text}")

if __name__ == "__main__":
    # להרצה מקומית (לא בשימוש ב-Render)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
