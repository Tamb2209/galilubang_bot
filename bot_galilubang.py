import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_GROUP_ID = os.getenv('ADMIN_GROUP_ID')

user_message_mapping = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selamat datang ke Gali Lubang Bot!\nHantar mesej anda dan kami akan hantar kepada Admin secara rahsia."
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    sent_message = await context.bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=f"Mesej baru dari user ID {user.id}:\n\n{text}"
    )

    user_message_mapping[sent_message.message_id] = user.id

    await update.message.reply_text("Mesej anda telah dihantar secara rahsia.")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.chat_id == int(ADMIN_GROUP_ID):
        replied_message_id = update.message.reply_to_message.message_id
        user_id = user_message_mapping.get(replied_message_id)

        if user_id:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"Balasan admin:\n{update.message.text}"
                )
            except Exception as e:
                logging.error(f"Gagal hantar balasan ke user: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_user_message))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.REPLY & filters.TEXT, handle_admin_reply))

    await app.run_polling()

if _name_ == '_main_':
    import asyncio
    asyncio.run(main())
