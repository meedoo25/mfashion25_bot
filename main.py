import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

FULL_NAME, PHONE_NUMBER, ID_CARD = range(3)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = eval(os.getenv("ADMIN_IDS"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    referral = args[0] if args else "غير معروف"
    context.user_data["referral"] = referral
    await update.message.reply_text("📋 مرحبًا في التسجيل. الاسم الكامل؟")
    return FULL_NAME

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("📱 رقم الهاتف؟")
    return PHONE_NUMBER

async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🪪 بطاقة التعريف (رقم أو صورة):")
    return ID_CARD

async def id_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    context.user_data["id_card"] = update.message.text if update.message.text else "📷 صورة مرسلة"
    msg = (
        f"🆕 تسجيل جديد:\n"
        f"👤 {context.user_data['full_name']}\n"
        f"📞 {context.user_data['phone']}\n"
        f"🆔 {context.user_data['id_card']}\n"
        f"🔗 إحالة: {context.user_data['referral']}\n"
        f"👤 @{user.username or 'بدون'}"
    )
    for admin in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin, text=msg)
    await update.message.reply_text("✅ تم تسجيل معلوماتك. شكراً لك.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ ألغيت العملية.")
    return ConversationHandler.END

app = ApplicationBuilder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
        PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number)],
        ID_CARD: [MessageHandler(filters.ALL & ~filters.COMMAND, id_card)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
app.add_handler(conv)

if __name__ == "__main__":
    app.run_polling()
