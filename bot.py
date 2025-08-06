import os
import logging
from yt_dlp import YoutubeDL
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load token from environment
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or "PASTE_YOUR_BOT_TOKEN_HERE"

# Max upload size for Telegram bots
MAX_SIZE_MB = 50
CHUNK_SIZE_MB = 48  # Safety buffer

logging.basicConfig(level=logging.INFO)

# 📁 Split large file into smaller parts
def split_file(file_path, chunk_size_mb=CHUNK_SIZE_MB):
    parts = []
    chunk_size = chunk_size_mb * 1024 * 1024
    part_num = 1

    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            part_path = f"{file_path}.part{part_num}"
            with open(part_path, 'wb') as pf:
                pf.write(chunk)
            parts.append(part_path)
            part_num += 1

    return parts

# 🎬 Download and send video (with splitting if large)
async def download_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if not msg.startswith("http"):
        await update.message.reply_text("❌ Please send a valid Dailymotion video URL.")
        return

    user_id = update.effective_user.id
    output_file = f"user_{user_id}_video.mp4"

    await update.message.reply_text("⏳ Downloading video...")

    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_file,
            'noplaylist': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([msg])

        size_mb = os.path.getsize(output_file) / (1024 * 1024)

        if size_mb <= MAX_SIZE_MB:
            with open(output_file, 'rb') as f:
                await update.message.reply_video(video=f, caption="✅ Download complete!")
        else:
            await update.message.reply_text(f"⚠️ File size is {size_mb:.2f} MB. Sending in parts...")
            parts = split_file(output_file)
            for i, part in enumerate(parts, 1):
                with open(part, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=os.path.basename(part),
                        caption=f"📦 Part {i}/{len(parts)}"
                    )
                os.remove(part)

        os.remove(output_file)

    except Exception as e:
        logging.exception("Download error:")
        await update.message.reply_text(f"❌ Error: {e}")

# 👋 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a Dailymotion video link to download it.")

# 🚀 Start bot
async def main():
    from nest_asyncio import apply
    import asyncio

    apply()  # ⚙️ Fix event loop issues on Render

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_and_send))

    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())