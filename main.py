from flask import Flask
import telebot
import os

TOKEN = os.getenv("BOT_TOKEN")  # שים את הטוקן שלך בסביבת העבודה של Render
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "היי! הבוט באוויר 🚀")

if __name__ == '__main__':
    import threading

    def run_bot():
        bot.polling()

    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
