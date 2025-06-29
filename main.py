from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import os

# الحالة لكل سؤال
NAME, PHONE, CIN, WILAYA = range(4)

# معرف المدير (بدلو ب ID تاعك)
ADMIN_IDS = [123456789]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحبا! من فضلك اكتب اسمك الكامل:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 الآن أرسل رقم هاتفك:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🆔 أرسل رقم بطاقة تعريفك:")
    return CIN

async def get_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cin"] = update.message.text
    await update.message.reply_text("🌍 أخيرًا، أرسل ولايتك:")
    return WILAYA

async def get_wilaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wilaya"] = update.message.text

    # نجمع البيانات ونبعتها للمدير
    message = (
        f"📥 طلب تسجيل جديد:\n\n"
        f"👤 الاسم: {context.user_data['name']}\n"
        f"📞 الهاتف: {context.user_data['phone']}\n"
        f"🆔 بطاقة التعريف: {context.user_data['cin']}\n"
        f"🌍 الولاية: {context.user_data['wilaya']}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=message)

    await update.message.reply_text("✅ تم إرسال معلوماتك، سيتم التواصل معك قريبًا.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cin)],
            WILAYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wilaya)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
