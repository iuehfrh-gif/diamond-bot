import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ---------------- CONFIGURATION ----------------
BOT_TOKEN = "8921000285:AAHlcIO8HVdDdNbw-gCLm36ICnvJkg35INc"
ADMIN_ID = 8665365934
ADMIN_USERNAME = "@minkhant460"

# KPay Info
KPAY_NAME = "Aye Thin"
KPAY_PHONE = "09976215768"

# Diamond Prices Setup (Diamond Amount / Weekly Pass: Price in MMK)
DIAMOND_PRICES = {
    "55": 4000,
    "86": 5400,
    "172": 10700,
    "257": 15000,
    "706": 42000,
    "2195": 150000,
    "weeklypass": 6800,
}

# Conversation States
WAITING_GAME_ID, WAITING_RECEIPT = range(2)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ---------------- BOT HANDLERS ----------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start နှိပ်ပါက စျေးနှုန်း Menu ပြသပေးခြင်း (Admin ဖြစ်နေပါက လုံးဝပိတ်ရန်)"""
    user = update.effective_user

    if user.id == ADMIN_ID:
        admin_msg = "⚠️ **Admin အကောင့်ဖြစ်သောကြောင့် ဤဘော့တ်မှတစ်ဆင့် ဝယ်ယူ၍ မရပါ။**"
        if update.message:
            await update.message.reply_text(admin_msg, parse_mode="Markdown")
        else:
            await update.callback_query.message.reply_text(
                admin_msg, parse_mode="Markdown"
            )
        return ConversationHandler.END

    keyboard = []
    row = []
    for diamond, price in DIAMOND_PRICES.items():
        if diamond == "weeklypass":
            button_text = f"💎 Weekly Pass - {price:,} MMK"
        else:
            button_text = f"💎 {int(diamond):,} Dia - {price:,} MMK"

        row.append(InlineKeyboardButton(button_text, callback_data=f"dia_{diamond}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "💎 **Diamond Online Shop မှ ကြိုဆိုပါသည်** 💎\n\n"
        "ကျေးဇူးပြု၍ ဝယ်ယူလိုသော ပမာဏကို ရွေးချယ်ပေးပါနော်။"
    )

    if update.message:
        await update.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )
    else:
        await update.callback_query.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
        )

    return ConversationHandler.END


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ခလုတ်နှိပ်ပါက Admin ဟုတ်မဟုတ် စစ်ဆေးပြီး Game ID နှင့် Game Name တောင်းဆိုခြင်း"""
    query = update.callback_query
    user = update.effective_user

    if user.id == ADMIN_ID:
        await query.answer("⚠️ Admin အကောင့်ဖြင့် ဝယ်ယူခွင့်မရှိပါ။", show_alert=True)
        return ConversationHandler.END

    await query.answer()

    diamond = query.data.replace("dia_", "")
    price = DIAMOND_PRICES[diamond]

    context.user_data["selected_diamond"] = diamond
    context.user_data["selected_price"] = price

    item_name = (
        "Weekly Pass" if diamond == "weeklypass" else f"{int(diamond):,} Diamond"
    )

    await query.message.reply_text(
        f"✅ သင်ရွေးချယ်ထားသော ပမာဏ - **{item_name}** ({price:,} MMK)\n\n"
        "ကျေးဇူးပြု၍ သင်၏ **Game ID (Server ID) နှင့် Game Name** ကို တစ်ခါတည်း ရေးပြီး ပို့ပေးပါနော်။\n"
        "ဥပမာ - `12345678 (1234) - PlayerName`",
        parse_mode="Markdown",
    )
    return WAITING_GAME_ID


async def get_game_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Game ID နှင့် Game Name ရရှိပါက KPay အချက်အလက်များပြသခြင်း"""
    game_info = update.message.text
    context.user_data["game_info"] = game_info

    diamond = context.user_data.get("selected_diamond")
    price = context.user_data["selected_price"]

    item_display = "Weekly Pass" if diamond == "weeklypass" else f"{int(diamond):,} Dia"

    msg = (
        f"📝 **အော်ဒါ အသေးစိတ်**\n"
        f"• ဝယ်ယူမှု: **{item_display}**\n"
        f"• စုစုပေါင်း ကျသင့်ငွေ: **{price:,} MMK**\n"
        f"• Game ID & Name: `{game_info}`\n\n"
        f"💳 **ငွေလွှဲရမည့် KPay အကောင့် အချက်အလက်**\n"
        f"• Name: **{KPAY_NAME}**\n"
        f"• Phone: `{KPAY_PHONE}`\n\n"
        "ငွေလွှဲပြီးပါက **KPay ငွေလွှဲပြေစာ Screenshot (ပုံ)** ကိုသာ တိကျစွာ ပို့ပေးပါခင်ဗျ။"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")
    return WAITING_RECEIPT


async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ပြေစာပုံ ရရှိပါက ဝယ်သူထံ စာပို့ပြီး Admin ထံ Done ခလုတ်ပါသော Screenshot ပို့မည်"""
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ ကျေးဇူးပြု၍ **KPay ငွေလွှဲပြေစာ Screenshot (ပုံ)** ကိုသာ ပို့ပေးပါခင်ဗျ။"
        )
        return WAITING_RECEIPT

    photo_file = update.message.photo[-1].file_id

    user = update.effective_user
    game_info = context.user_data.get("game_info")
    diamond = context.user_data.get("selected_diamond")
    price = context.user_data["selected_price"]

    item_display = "Weekly Pass" if diamond == "weeklypass" else f"{int(diamond):,} Dia"

    # ဝယ်သူဆီ ပြန်ပေးမည့် စာ
    await update.message.reply_text(
        f"✅ **ပြေစာ လက်ခံရရှိပါသည်။ Admin မှ စစ်ဆေးနေပါသည် ခဏစောင့်ပေးပါခင်ဗျာ။ အဆင်မပြေပါက Admin ({ADMIN_USERNAME}) သို့ တိုက်ရိုက်ဆက်သွယ်ဝယ်ယူနိုင်ပါသည်ခင်ဗျ။**",
        parse_mode="Markdown",
    )

    # Admin ထံ ပို့မည့် အကြောင်းကြားစာ
    admin_caption = (
        f"📥 **KPay ပြေစာအသစ် ရောက်ရှိလာပါသည်။**\n\n"
        f"👤 ဝယ်သူအကောင့်: {user.mention_markdown()} (ID: `{user.id}`)\n"
        f"💎 ဝယ်ယူမှု: **{item_display}**\n"
        f"💰 ကျသင့်ငွေ: **{price:,} MMK**\n"
        f"🎮 Game ID & Name: `{game_info}`"
    )

    # Admin အတွက် Done ခလုတ်ဖန်တီးခြင်း
    admin_keyboard = [
        [
            InlineKeyboardButton(
                "✅ Done (ထည့်ပြီးပါပြီ)", callback_data=f"done_{user.id}"
            )
        ]
    ]
    admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)

    try:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_file,
            caption=admin_caption,
            reply_markup=admin_reply_markup,
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Failed to send alert to admin: {e}")

    return ConversationHandler.END


async def done_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin မှ Done ခလုတ်နှိပ်ပါက ဝယ်သူဆီသို့ အောင်မြင်ကြောင်း စာပို့ပေးခြင်း"""
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("⚠️ ဤခလုတ်ကို Admin သာ နှိပ်ခွင့်ရှိပါသည်။", show_alert=True)
        return

    data = query.data  # ဥပမာ - done_123456789
    customer_id = int(data.replace("done_", ""))

    # ဝယ်သူဆီသို့ အောင်မြင်ကြောင်း စာပို့ခြင်း
    try:
        await context.bot.send_message(
            chat_id=customer_id,
            text="💎 **သင့် acc ထဲသို့ ဖြည့်သွင်းပြီးပါပြီ။ ဝယ်ယူမှုအတွက် ကျေးဇူးတင်ပါသည်။** 🙏",
            parse_mode="Markdown",
        )
    except Exception as e:
        logging.error(f"Failed to send success message to customer {customer_id}: {e}")

    # Admin ရဲ့ မက်ဆေ့ချ်ကို ပြီးစီးကြောင်း ပြောင်းလဲပေးခြင်း
    original_caption = query.message.caption
    updated_caption = original_caption + "\n\n✅ **[အော်ဒါ ပြီးစီးပါပြီ]**"

    await query.edit_message_caption(
        caption=updated_caption, reply_markup=None, parse_mode="Markdown"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အော်ဒါ ပယ်ဖျက်ခြင်း"""
    await update.message.reply_text(
        "အော်ဒါ ဆောင်ရွက်မှုကို ပယ်ဖျက်လိုက်ပါပြီ။ /start ဖြင့် ပြန်စနိုင်ပါသည်။"
    )
    return ConversationHandler.END


async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """အခြားစာများ ပို့လာပါက တုံ့ပြန်ရန်"""
    user = update.effective_user
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "⚠️ **Admin အကောင့်ဖြစ်သောကြောင့် ဤဘော့တ်မှတစ်ဆင့် ဝယ်ယူ၍မရပါ။**",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"မင်္ဂလာပါခင်ဗျာ 🙏 ထပ်မံဝယ်ယူလိုပါက **/start** ကို နှိပ်ပြီး အော်ဒါအသစ် ပြန်တင်နိုင်ပါတယ်ခင်ဗျ။ အဆင်မပြေပါက Admin ({ADMIN_USERNAME}) သို့ တိုက်ရိုက်ဆက်သွယ်နိုင်ပါသည်။",
        parse_mode="Markdown",
    )


# ---------------- MAIN APPLICATION ----------------


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_click, pattern="^dia_")],
        states={
            WAITING_GAME_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_game_id)
            ],
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO, get_receipt),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    lambda u, c: u.message.reply_text(
                        "⚠️ ကျေးဇူးပြု၍ **KPay ငွေလွှဲပြေစာ Screenshot ပုံ** ကိုသာ ပို့ပေးပါခင်ဗျ။",
                        parse_mode="Markdown",
                    ),
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(done_button_click, pattern="^done_"))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages)
    )

    print("Bot is successfully running...")
    app.run_polling()


if __name__ == "__main__":
    main()
