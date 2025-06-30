from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
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
STOCK_OWNER_ID = 5501140465
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/order"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 مرحبا بك! ارسل اسمك الكامل:",
        reply_markup=reply_markup
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 أرسل رقم هاتفك:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🔐 أرسل رقم بطاقة التعريف:")
    return CIN

async def get_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cin"] = update.message.text
    await update.message.reply_text("🌍 أرسل الولاية:")
    return WILAYA

async def get_wilaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wilaya"] = update.message.text
    await update.message.reply_text("📸 ارسل صورة بطاقة التعريف:")
    return ID_CARD

async def get_id_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ ارسل صورة فقط.")
        return ID_CARD
    file_id = update.message.photo[-1].file_id
    context.user_data["photo"] = file_id
    user_id = update.effective_user.id

    caption = f"\ud83d\udcc5 <b>طلب جديد:</b>\n<b>الاسم:</b> {context.user_data['name']}\n<b>الهاتف:</b> {context.user_data['phone']}\n<b>البطاقة:</b> {context.user_data['cin']}\n<b>الولاية:</b> {context.user_data['wilaya']}\n<code>{user_id}</code>"
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("\u2705 قبول", callback_data=f"accept_{user_id}"),
                                    InlineKeyboardButton("\u274c رفض", callback_data=f"reject_{user_id}")]])
    for admin in ADMIN_IDS:
        await context.bot.send_photo(chat_id=admin, photo=file_id, caption=caption, parse_mode="HTML", reply_markup=markup)

    await update.message.reply_text("✅ تم إرسال معلوماتك، سيتم مراجعتها قريبًا.")
    return ConversationHandler.END

async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = int(data.split("_")[1])
    if data.startswith("accept"):
        await context.bot.send_message(chat_id=user_id, text="🎉 تم قبولك!")
        await context.bot.send_message(chat_id=user_id, text=f"انضم للمجموعة: {GROUP_LINK}")
        await context.bot.send_message(chat_id=user_id, text=RULES_TEXT, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=user_id, text="❌ تم رفض طلبك.")
    await query.edit_message_reply_markup(reply_markup=None)

# --- الطلبية --- #
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 اسمك الكامل:")
    return ORDER_NAME

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_name'] = update.message.text
    await update.message.reply_text("📞 رقم هاتفك:")
    return ORDER_PHONE

async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_phone'] = update.message.text
    await update.message.reply_text("🆔 رقم بطاقة تعريفك:")
    return ORDER_CIN

async def order_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_cin'] = update.message.text
    await update.message.reply_text("📏 المقاس:")
    return ORDER_SIZE

async def order_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_size'] = update.message.text
    await update.message.reply_text("🎨 اللون:")
    return ORDER_COLOR

async def order_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_color'] = update.message.text
    await update.message.reply_text("🔢 رقم الموديل:")
    return ORDER_MODEL

async def order_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['order_model'] = update.message.text
    await update.message.reply_text("👤 اسم المشتري:")
    return BUYER_NAME

async def buyer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['buyer_name'] = update.message.text
    await update.message.reply_text("📞 رقم هاتف المشتري:")
    return BUYER_PHONE

async def buyer_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['buyer_phone'] = update.message.text
    await update.message.reply_text("📍 عنوان المشتري:")
    return BUYER_ADDRESS

async def buyer_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['buyer_address'] = update.message.text

    msg = (
        f"📦 <b>طلب جديد:</b>\n<b>الاسم:</b> {context.user_data['order_name']}\n<b>الهاتف:</b> {context.user_data['order_phone']}\n"
        f"<b>البطاقة:</b> {context.user_data['order_cin']}\n<b>المقاس:</b> {context.user_data['order_size']}\n<b>اللون:</b> {context.user_data['order_color']}\n"
        f"<b>الموديل:</b> {context.user_data['order_model']}\n\n👥 <b>المشتري:</b> {context.user_data['buyer_name']}\n📞 {context.user_data['buyer_phone']}\n📍 {context.user_data['buyer_address']}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 نفاد المخزون", callback_data=f"stockout_{update.effective_user.id}")]
    ])

    await context.bot.send_message(chat_id=STOCK_OWNER_ID, text=msg, parse_mode="HTML", reply_markup=keyboard)
    await update.message.reply_text("✅ تم إرسال الطلبية للمخزن.")
    return ConversationHandler.END

async def stockout_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[1])
    await context.bot.send_message(chat_id=user_id, text="⚠️ المخزون غير متوفر حالياً. سيتم إعلامك عند توفره.")
    await query.edit_message_reply_markup(reply_markup=None)

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    # التسجيل
    register_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cin)],
            WILAYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wilaya)],
            ID_CARD: [MessageHandler(filters.PHOTO, get_id_card)],
        },
        fallbacks=[]
    )

    # الطلبية
    order_conv = ConversationHandler(
        entry_points=[CommandHandler("order", order_start)],
        states={
            ORDER_NAME: [MessageHandler(filters.TEXT, order_name)],
            ORDER_PHONE: [MessageHandler(filters.TEXT, order_phone)],
            ORDER_CIN: [MessageHandler(filters.TEXT, order_cin)],
            ORDER_SIZE: [MessageHandler(filters.TEXT, order_size)],
            ORDER_COLOR: [MessageHandler(filters.TEXT, order_color)],
            ORDER_MODEL: [MessageHandler(filters.TEXT, order_model)],
            BUYER_NAME: [MessageHandler(filters.TEXT, buyer_name)],
            BUYER_PHONE: [MessageHandler(filters.TEXT, buyer_phone)],
            BUYER_ADDRESS: [MessageHandler(filters.TEXT, buyer_address)],
        },
        fallbacks=[]
    )

    app.add_handler(register_conv)
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(handle_decision, pattern="^(accept_|reject_)"))
    app.add_handler(CallbackQueryHandler(stockout_notify, pattern="^stockout_"))

    app.run_polling()
