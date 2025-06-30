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
ORDER_NAME, ORDER_PHONE, ORDER_CIN, ORDER_SIZE, ORDER_COLOR, ORDER_MODEL, BUYER_NAME, BUYER_PHONE, BUYER_ADDRESS = range(5, 14)

# --- إعدادات عامة --- #
ADMIN_IDS = [6244970377]  # غيّر هذا إلى ID تاع المدير
OWNER_ID = 987654321     # Meedoo (المدير العام)
WAREHOUSE_ID = 5501140465
GROUP_LINK = "https://t.me/mohamed789123"

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

# --- بقية خطوات التسجيل (كما هي) --- #
# ... [get_name, get_phone, get_cin, get_wilaya, get_id_card remain unchanged] ...

# --- زر القبول والرفض --- #
async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك في فريق M.fashion.25! مرحبا بك!")
        await context.bot.send_message(chat_id=user_id, text=f"⬇️ رابط المجموعة: {GROUP_LINK}")
        await context.bot.send_message(chat_id=user_id, text=RULES_TEXT, parse_mode="HTML")
        await context.bot.send_message(chat_id=user_id, text="📝 لاستكمال الطلبيات، اضغط على /order")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("✅ تم قبول البائع.")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="❌ نعتذر، لم يتم قبول طلبك للانضمام.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("❌ تم رفض البائع.")

# --- طلبية جديدة --- #
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ اكتب اسمك الكامل:")
    return ORDER_NAME

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_name"] = update.message.text
    await update.message.reply_text("📞 رقم هاتفك:")
    return ORDER_PHONE

async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_phone"] = update.message.text
    await update.message.reply_text("🆔 رقم بطاقة التعريف:")
    return ORDER_CIN

async def order_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_cin"] = update.message.text
    await update.message.reply_text("📏 المقاس:")
    return ORDER_SIZE

async def order_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_size"] = update.message.text
    await update.message.reply_text("🎨 اللون:")
    return ORDER_COLOR

async def order_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_color"] = update.message.text
    await update.message.reply_text("🔢 رقم الموديل:")
    return ORDER_MODEL

async def order_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_model"] = update.message.text
    await update.message.reply_text("👤 اسم المشتري:")
    return BUYER_NAME

async def buyer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_name"] = update.message.text
    await update.message.reply_text("📞 رقم هاتف المشتري:")
    return BUYER_PHONE

async def buyer_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_phone"] = update.message.text
    await update.message.reply_text("📍 عنوان المشتري:")
    return BUYER_ADDRESS

async def buyer_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_address"] = update.message.text

    msg = (
        f"🛒 <b>طلبية جديدة:</b>\n\n"
        f"👤 البائع: {context.user_data['order_name']}\n"
        f"📞 الهاتف: {context.user_data['order_phone']}\n"
        f"🆔 رقم التعريف: {context.user_data['order_cin']}\n"
        f"📏 المقاس: {context.user_data['order_size']}\n"
        f"🎨 اللون: {context.user_data['order_color']}\n"
        f"🔢 رقم الموديل: {context.user_data['order_model']}\n\n"
        f"👤 المشتري: {context.user_data['buyer_name']}\n"
        f"📞 هاتفه: {context.user_data['buyer_phone']}\n"
        f"📍 العنوان: {context.user_data['buyer_address']}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 نفاد المخزون", callback_data=f"outofstock_{update.effective_user.id}")]
    ])

    await context.bot.send_message(chat_id=WAREHOUSE_ID, text=msg, parse_mode="HTML", reply_markup=keyboard)
    await update.message.reply_text("✅ تم إرسال الطلبية للمخزن. سيتم الرد عليك في حالة وجود مشكلة.")
    return ConversationHandler.END

# --- زر المخزون --- #
async def stock_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("outofstock_"):
        seller_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=seller_id, text="🚫 المنتج غير متوفر في المخزون حالياً.")
        await query.edit_message_reply_markup(reply_markup=None)

# --- التشغيل الرئيسي --- #
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cin)],
            WILAYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wilaya)],
            ID_CARD: [MessageHandler(filters.PHOTO, get_id_card)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    order_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order)],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_phone)],
            ORDER_CIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_cin)],
            ORDER_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_size)],
            ORDER_COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_color)],
            ORDER_MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_model)],
            BUYER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, buyer_name)],
            BUYER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, buyer_phone)],
            BUYER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, buyer_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(registration_handler)
    app.add_handler(order_handler)
    app.add_handler(CallbackQueryHandler(handle_decision))
    app.add_handler(CallbackQueryHandler(stock_decision))

    app.run_polling()
