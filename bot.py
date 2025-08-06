import os
import logging
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ✅ Paste your bot token here
TELEGRAM_TOKEN = "8450049927:AAHx5T9jl-f7F2rbeET4cLGqzix3SI0QT6E"

# 🎯 Set up logging (optional but helpful)
logging.basicConfig(level=logging.INFO)

# 📥 Download video
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    if not user_message.startswith("http"):
        await update.message.reply_text("❌ Please send a valid Dailymotion video URL.")
        return

    video_url = user_message
    user_id = update.effective_user.id
    file_basename = f"user_{user_id}_video"

    output_path = f"{file_basename}.mp4"

    await update.message.reply_text("⏳ Downloading video, please wait...")

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_path,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        # Send video
        with open(output_path, 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="✅ Download complete!")

        # Clean up
        os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to download: {e}")

# 👋 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a Dailymotion video URL to download it!")

# 🚀 Main bot runner
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
