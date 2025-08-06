from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import logging
import os
import asyncio

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Define your handlers here
async def start(update, context):
    await update.message.reply_text("👋 Hello! Send me a Dailymotion link to download.")

async def handle_message(update, context):
    await update.message.reply_text("⏳ Processing your link... (functionality here)")

async def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")

    # DON'T use asyncio.run — just await directly if __name__ == "__main__"
    await application.run_polling()

# Correct pattern for Render (already has event loop running)
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError as e:
        # fallback if loop already running
        loop = asyncio.get_event_loop()
        task = loop.create_task(main())
        loop.run_until_complete(task)
