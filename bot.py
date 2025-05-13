import os
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "7569569536:AAGdPRShZ6SfQFhwFt09TSOcgoupBWodjsI"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Step 1: Handle received links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ Please send a valid Instagram or YouTube link.")
        return

    # Save the link to use it in button callback
    context.user_data['last_url'] = url

    # Show download options
    buttons = [
        [InlineKeyboardButton("📹 Download 1080p Video", callback_data="video_1080p")],
        [InlineKeyboardButton("🎵 Download MP3 Audio", callback_data="audio_mp3")]
    ]
    await update.message.reply_text(
        "What do you want to download?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Step 2: Handle button clicks
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    url = context.user_data.get('last_url')
    if not url:
        await query.edit_message_text("❌ No URL found. Please send the link again.")
        return

    action = query.data
    msg = await query.edit_message_text("⏳ Processing...")

    video_path = os.path.join(DOWNLOAD_DIR, f"{query.id}.mp4")
    audio_path = os.path.join(DOWNLOAD_DIR, f"{query.id}.mp3")

    try:
        if action == "video_1080p":
            ydl_opts = {
                'format': 'bestvideo[height<=1080]+bestaudio/best',
                'outtmpl': video_path,
                'merge_output_format': 'mp4',
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await query.message.reply_video(video=open(video_path, 'rb'))
            os.remove(video_path)

        elif action == "audio_mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await query.message.reply_audio(audio=open(audio_path, 'rb'))
            os.remove(audio_path)

        else:
            await query.edit_message_text("❌ Unknown action.")
            return

        await msg.delete()

    except Exception as e:
        await query.edit_message_text("❌ Failed to download or send the media.")
        print("Error:", e)

# Main app
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()
