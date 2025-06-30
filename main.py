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

# --- Conversation Steps --- #
NAME, PHONE, CIN, WILAYA, ID_CARD = range(5)
ORDER_NAME, ORDER_PHONE, ORDER_CIN, ORDER_SIZE, ORDER_COLOR, ORDER_MODEL, BUYER_NAME, BUYER_PHONE, BUYER_ADDRESS = range(9)

# --- IDs --- #
ADMIN_IDS = [6244970377]  # Update with real admin ID
STOCK_OWNER_ID = 5501140465
OWNER_ID = 987654321
RULES_TEXT = """
قوانين العمل للبائعين:
- كل غياب فوق 48 ساعة دون سبب = حذف تلقائي.
- كل بائع يتلقى رسالة تحفيزية يومية + إحصائياته.
- كل ترويج غير جدي أو مخالف يُلغى احتسابه.
- عند الانضمام، تُرسل له القوانين:
  - طريقة البيع
  - طريقة تسجيل الزبون
  - كيفية التوصيل
  - أوقات الرد
  - أخلاقيات التعامل مع الزبائن
"""

# --- Start --- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/order"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("مرحبا بك! اضغط على /order لإرسال طلب جديد أو أدخل معلوماتك للبدء.", reply_markup=reply_markup)
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("أدخل رقم هاتفك:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("أدخل رقم بطاقة تعريفك:")
    return CIN

async def get_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cin"] = update.message.text
    await update.message.reply_text("أدخل ولايتك:")
    return WILAYA

async def get_wilaya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wilaya"] = update.message.text
    await update.message.reply_text("أرسل الآن صورة بطاقة تعريفك كصورة (وليس ملف).")
    return ID_CARD

async def get_id_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("من فضلك أرسل بطاقة التعريف على شكل صورة.")
        return ID_CARD

    photo_file = await update.message.photo[-1].get_file()
    context.user_data["photo"] = photo_file.file_id
    user_id = update.effective_user.id

    message = (
        f"طلب تسجيل جديد:\n"
        f"الاسم: {context.user_data['name']}\n"
        f"الهاتف: {context.user_data['phone']}\n"
        f"رقم التعريف: {context.user_data['cin']}\n"
        f"الولاية: {context.user_data['wilaya']}\n"
        f"user_id: {user_id}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("قبول", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("رفض", callback_data=f"reject_{user_id}")
        ]
    ])

    for admin_id in ADMIN_IDS:
        await context.bot.send_photo(chat_id=admin_id, photo=context.user_data["photo"], caption=message, reply_markup=keyboard)

    await update.message.reply_text("تم إرسال معلوماتك. سيتم الرد بعد مراجعتها.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="تم قبولك. هذه قوانين العمل:")
        await context.bot.send_message(chat_id=user_id, text=RULES_TEXT)
        await context.bot.send_message(chat_id=user_id, text="رابط المجموعة: https://t.me/mohamed789123")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("تم قبول البائع.")

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(chat_id=user_id, text="نعتذر، لم يتم قبول طلبك.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("تم رفض البائع.")

# --- Order Flow --- #
async def order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أدخل اسمك الكامل:")
    return ORDER_NAME

async def order_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_name"] = update.message.text
    await update.message.reply_text("أدخل رقم هاتفك:")
    return ORDER_PHONE

async def order_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_phone"] = update.message.text
    await update.message.reply_text("أدخل رقم بطاقة تعريفك:")
    return ORDER_CIN

async def order_cin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_cin"] = update.message.text
    await update.message.reply_text("ما هو المقاس:")
    return ORDER_SIZE

async def order_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_size"] = update.message.text
    await update.message.reply_text("ما هو اللون:")
    return ORDER_COLOR

async def order_color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_color"] = update.message.text
    await update.message.reply_text("رقم الموديل:")
    return ORDER_MODEL

async def order_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_model"] = update.message.text
    await update.message.reply_text("اسم المشتري:")
    return BUYER_NAME

async def buyer_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_name"] = update.message.text
    await update.message.reply_text("رقم هاتف المشتري:")
    return BUYER_PHONE

async def buyer_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_phone"] = update.message.text
    await update.message.reply_text("عنوان المشتري:")
    return BUYER_ADDRESS

async def buyer_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["buyer_address"] = update.message.text
    user_id = update.effective_user.id

    msg = (
        f"طلب جديد:\n"
        f"الاسم: {context.user_data['order_name']}\n"
        f"الهاتف: {context.user_data['order_phone']}\n"
        f"بطاقة التعريف: {context.user_data['order_cin']}\n"
        f"المقاس: {context.user_data['order_size']}\n"
        f"اللون: {context.user_data['order_color']}\n"
        f"الموديل: {context.user_data['order_model']}\n"
        f"اسم المشتري: {context.user_data['buyer_name']}\n"
        f"هاتف المشتري: {context.user_data['buyer_phone']}\n"
        f"العنوان: {context.user_data['buyer_address']}\n"
        f"ID البائع: {user_id}"
    )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("نفاد المخزون", callback_data=f"outofstock_{user_id}")]
    ])

    await context.bot.send_message(chat_id=STOCK_OWNER_ID, text=msg, reply_markup=reply_markup)
    await update.message.reply_text("تم إرسال الطلب.")
    return ConversationHandler.END

async def handle_outofstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[1])
    await context.bot.send_message(chat_id=user_id, text="نعتذر، المنتج الذي طلبته غير متوفر حالياً.")
    await query.edit_message_reply_markup(reply_markup=None)

# --- Main --- #
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    registration_conv = ConversationHandler(
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

    order_conv = ConversationHandler(
        entry_points=[CommandHandler("order", order_command)],
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
        fallbacks=[]
    )

    app.add_handler(registration_conv)
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(handle_decision, pattern="^(accept_|reject_)"))
    app.add_handler(CallbackQueryHandler(handle_outofstock, pattern="^outofstock_"))

    app.run_polling()
