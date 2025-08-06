import os
import logging
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8450049927:AAHx5T9jl-f7F2rbeET4cLGqzix3SI0QT6E"
MAX_SIZE_MB = 50  # Max Telegram bot upload size
CHUNK_SIZE_MB = 48  # Safety margin for each chunk

logging.basicConfig(level=logging.INFO)

# 📁 Split video into parts if too big
def split_file(file_path, chunk_size_mb=48):
    parts = []
    part_num = 1
    chunk_size = chunk_size_mb * 1024 * 1024

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            part_file = f"{file_path}.part{part_num}"
            with open(part_file, 'wb') as pf:
                pf.write(chunk)
            parts.append(part_file)
            part_num += 1

    return parts

# 🎬 Download and send video
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    if not user_message.startswith("http"):
        await update.message.reply_text("❌ Please send a valid Dailymotion video URL.")
        return

    video_url = user_message
    user_id = update.effective_user.id
    output_file = f"user_{user_id}_video.mp4"

    await update.message.reply_text("⏳ Downloading video. Please wait...")

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_file,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)

        if file_size_mb <= MAX_SIZE_MB:
            with open(output_file, 'rb') as f:
                await update.message.reply_video(video=f, caption="✅ Download complete!")
        else:
            await update.message.reply_text(f"⚠️ File is {file_size_mb:.2f} MB. Splitting into parts...")
            parts = split_file(output_file, CHUNK_SIZE_MB)

            for i, part in enumerate(parts, 1):
                with open(part, 'rb') as f:
                    await update.message.reply_document(document=f, filename=os.path.basename(part),
                                                        caption=f"📦 Part {i}/{len(parts)}")
                os.remove(part)

        os.remove(output_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# 👋 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a Dailymotion video URL to download it.")

# 🚀 Main bot setup
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
