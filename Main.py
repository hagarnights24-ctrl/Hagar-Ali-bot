import os, asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "אתה אסיסטנט נחמד שעונה בעברית פשוטה (או באנגלית אם פונים באנגלית). "
    "ענה קצר, ברור, בלי חפירות."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("היי! תכתוב לי כל דבר ואני אענה בעזרת בינה מלאכותית 🙂")

def _ask_openai(user_text: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.7,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    # הקריאה ל-OpenAI סינכרונית, מריצים אותה ב-thread כדי לא לחסום
    answer = await asyncio.to_thread(_ask_openai, text)
    await update.message.reply_text(answer)

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    port = int(os.environ.get("PORT", 10000))
    public_url = os.environ.get("RENDER_EXTERNAL_URL")  # Render מגדירה את זה לבד

    if public_url:
        # מרימים webhook אוטומטית עם ה-URL הציבורי של Render
        await app.bot.set_webhook(url=f"{public_url}/webhook/{TELEGRAM_TOKEN}",
                                  allowed_updates=["message"])
        await app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=f"webhook/{TELEGRAM_TOKEN}",
        )
    else:
        # fallback לפולינג (מקומי)
        await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
