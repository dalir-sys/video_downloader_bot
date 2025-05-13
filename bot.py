import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7569569536:AAGdPRShZ6SfQFhwFt09TSOcgoupBWodjsI"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("Please send a valid Instagram or YouTube link.")
        return

    await update.message.reply_text("⏳ Downloading... Please wait...")

    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
        'skip_download': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get("url")
            title = info.get("title", "Your video")
            await update.message.reply_text(f"✅ {title}\n📥 Download Link:\n{download_url}")
    except Exception as e:
        await update.message.reply_text("❌ Error: Could not fetch the video. It might be private or unsupported.")
        print("Error:", e)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
