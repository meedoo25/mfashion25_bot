from telegram import Update, ReplyKeyboardRemove, InputFile, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
import os

# --- مراحل المحادثة --- #
NAME, PHONE, CIN, WILAYA, ID_CARD = range(5)

# --- إعدادات عامة --- #
ADMIN_IDS = [7868012601]  # غيّر هذا إلى ID تاع المدير
OWNER_ID = 987654321     # Meedoo (المدير العام)
RULES_TEXT = """
⚠️ <b>قوانين العمل للبائعين:</b>
• كل غياب فوق 48 ساعة دون سبب = حذف تلقائي.
• كل بائع يتلقى رسالة تحفيزية يومية + إحصائياته.
• كل ترويج غير جدي أو مخالف يُلغى احتسابه.
• عند الانضمام، تُرسل له القوانين:
 - طريقة البيع
 - طريقة تسجيل الزبون
 - كيفية التوصيل
 - أوقات الرد
 - أخلاقيات التعامل مع الزبائن
"""

# --- البداية --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/start"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 مرحبا بك في M.fashion.25! اضغط على /start للبدء أو أرسل اسمك الكامل:",
        reply_markup=reply_markup
    )
    return NAME

# --- الحصول على الاسم --- #
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📱 أرسل رقم هاتفك:",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

# --- الحصول على الهاتف --- #
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🆔 أرسل رقم بطاقة تعريفك:")
    return CIN

# --- الحصول على رقم البطاقة --- #
async def get_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cin"] = update.message.text
    await update.message.reply_text("🌍 أرسل الولاية التي تسكن بها:")
    return WILAYA

# --- الحصول على الولاية --- #
async def get_wilaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wilaya"] = update.message.text
    await update.message.reply_text("📸 أرسل الآن صورة بطاقة التعريف الخاصة بك (كصورة وليس ملف):")
    return ID_CARD

# --- استقبال الصورة --- #
async def get_id_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ من فضلك أرسل بطاقة التعريف على شكل <b>صورة</b>.", parse_mode="HTML")
        return ID_CARD

    photo_file = await update.message.photo[-1].get_file()
    context.user_data["photo"] = photo_file.file_id

    user_id = update.effective_user.id

    message = (
        f"📥 <b>طلب تسجيل جديد:</b>\n\n👤 الاسم: {context.user_data['name']}\n"
        f"📞 الهاتف: {context.user_data['phone']}\n🆔 بطاقة التعريف: {context.user_data['cin']}\n"
        f"🌍 الولاية: {context.user_data['wilaya']}\n\n📸 البطاقة مرفقة كصورة.\n\n"
        f"👤 user_id: <code>{user_id}</code>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ قبول", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{user_id}")
        ]
    ])

    for admin_id in ADMIN_IDS:
        print(f"🔁 نحاول نبعث للإدمن: {admin_id}")
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=context.user_data["photo"],
                caption=message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            print(f"✅ تبعتت بنجاح لـ {admin_id}")
        except Exception as e:
            print(f"❌ خطأ أثناء الإرسال لـ {admin_id}: {e}")

    await update.message.reply_text("✅ تم إرسال معلوماتك. سيتم مراجعتها من طرف الإدارة والتواصل معك.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- زر القبول والرفض --- #
async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك في فريق M.fashion.25! مرحبا بك!")
        await context.bot.send_message(chat_id=user_id, text=RULES_TEXT, parse_mode="HTML")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("✅ تم قبول البائع.")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="❌ نعتذر، لم يتم قبول طلبك للانضمام.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ تم رفض البائع.")

# --- أمر يقبَل البائع (اختياري) --- #
async def accept_seller(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ ليس لديك صلاحية لاستعمال هذا الأمر.")
        return

    if not context.args:
        await update.message.reply_text("❗ أرسل الأمر هكذا:\n/accept <user_id>")
        return

    try:
        user_id = int(context.args[0])
        await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك في فريق M.fashion.25! مرحبا بك!")
        await context.bot.send_message(chat_id=user_id, text=RULES_TEXT, parse_mode="HTML")
        await update.message.reply_text("✅ تم قبول البائع وإرسال القوانين.")
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")

# --- إلغاء التسجيل --- #
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء العملية.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- التشغيل الرئيسي --- #
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("starttest", start),
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cin)],
            WILAYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wilaya)],
            ID_CARD: [MessageHandler(filters.PHOTO, get_id_card)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("accept", accept_seller))
    app.add_handler(CallbackQueryHandler(handle_decision))

    app.run_polling()
