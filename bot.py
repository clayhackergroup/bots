import logging
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- CONFIGURATION ---
TOKEN = "8590188368:AAH2hcDeaMH1JHtwIas88CCCQT72Ke8j4WM"
ADMIN_PASSWORD = "chiragenz"
UPI_IMAGE_PATH = "payment_qr.png"
TUTORIAL_VIDEO_PATH = "tutorial.mp4" 
ADMIN_USERNAME = "@Genzhub07" 
UPI_ID = "harshalvavale-1@oksbi"
DB_FILE = "database.json"
MY_ADMIN_ID = 6826886745 

ADMIN_AUTH = 0

# --- DATABASE LOGIC ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_db():
    with open(DB_FILE, "w") as f: json.dump(users_db, f)

users_db = load_db()

# --- PRICES (UPDATED AS REQUESTED) ---
PRICES = {
    "8BP_3D": 480, "8BP_10D": 1250, "8BP_30D": 2500,
    "Carom_3D": 230, "Carom_10D": 520, "Carom_30D": 1200,
    "Soccer_3D": 220, "Soccer_10D": 450, "Soccer_30D": 800,
    "Carrom Pass": 130, 
    "1Cr Coins": 250, 
    "5Cr Coins": 1200, 
    "10Cr Coins": 2500
}

# --- STOCK DATA ---
STOCK_TEXT = (
    "📦 <b>Stock Available:</b>\n\n"
    "🎮 <b>8 Ball Pool:</b>\n"
    "  - 3 din: 5 keys\n"
    "  - 10 din: 6 keys\n"
    "  - 30 din: 3 keys\n\n"
    "🎮 <b>Carrom Pool:</b>\n"
    "  - 3 din: 7 keys\n"
    "  - 10 din: 2 keys\n"
    "  - 30 din: 4 keys\n\n"
    "🎮 <b>Soccer Stars:</b>\n"
    "  - 3 din: 2 keys\n"
    "  - 10 din: 5 keys\n"
    "  - 30 din: 8 keys"
)

STRINGS = {
    "en": {
        "welcome": f"<b>👋 Welcome!</b>\n\nPurchase Snake Engine Subscriptions, Carrom Pass, and Coins at best prices. 🚀\n\nContact: {ADMIN_USERNAME}",
        "buy_3": "Purchase 3-Day", "buy_10": "Purchase 10-Day", "buy_30": "Purchase 30-Day",
        "coins_btn": "💰 Coins", "pass_btn": "🎟️ Carrom Pass", "stock_btn": "📦 Stock",
        "balance": "💰 Balance", "add_bal": "➕ Add", "proofs_btn": "✅ Proofs",
        "confirm": "Do You Want To Get {item} For ₹{price}.00 INR?",
        "success_key": "✅ Purchase completed! Please wait, your key will be delivered soon.\nIf you face any issues, you can contact the admin: {admin}\n\n🛒 <b>Purchased:</b> {item}\n💵 <b>Amount:</b> ₹{price}\n👤 <b>User ID:</b> <code>{uid}</code>",
        "success_order": "✅ Purchase completed! contact the admin and send your account ID and password to complete your order: {admin}\n\n🛒 <b>Purchased:</b> {item}\n💵 <b>Amount:</b> ₹{price}\n👤 <b>User ID:</b> <code>{uid}</code>",
        "ss_received": "Thank you! Your payment proof has been received🧾 The amount will be added to your balance after verification of payment✅",
        "pay_msg": "💳 आप QR कोड को स्कैन करके या UPI ID का उपयोग करके भुगतान कर सकते हैं।\n\n👇 UPI ID कॉपी करने के लिए क्लिक करें:\n<code>{upi}</code>\n\nभुगतान पूरा करने के बाद, कृपया भुगतान का स्क्रीनशॉट यहाँ भेजें📱\n\nसत्यापित होने के बाद, राशि आपके बैलेंस में जोड़ दी जाएगी✅\n\n<b>नोट:</b>\nट्रांजेक्शन ID (UTR) और राशि स्क्रीनशॉट में स्पष्ट रूप से दिखाई देनी चाहिए🧾",
        "proofs_text": "You can verify all proofs on my social platforms✅\nI have posted them on my Telegram channel and WhatsApp community🌟 \n\nTelegram Channel📡-https://t.me/genzcarromhub\n\nWhatsApp Group☎️-https://whatsapp.com/channel/0029VbBRKgp1t90TfztVel16\n\nYouTube Channel▶️-https://youtu.be/NsLwPYUWuro?si=KXqBlAGiFVGTmdM2"
    },
    "hi": {
        "welcome": f"<b>👋 स्वागत है!</b>\n\nस्नेक इंजन सब्सक्रिप्शन और सिक्के सबसे कम कीमत पर खरीदें। 🚀\n\nसंपर्क: {ADMIN_USERNAME}",
        "buy_3": "3-दिन प्लान", "buy_10": "10-दिन प्लान", "buy_30": "30-दिन प्लान",
        "coins_btn": "💰 सिक्के", "pass_btn": "🎟️ कैरम पास", "stock_btn": "📦 स्टॉक",
        "balance": "💰 बैलेंस", "add_bal": "➕ जोड़ें", "proofs_btn": "✅ प्रूफ",
        "confirm": "क्या आप ₹{price}.00 INR में {item} लेना चाहते हैं?",
        "success_key": "✅ Purchase completed! Please wait, your key will be delivered soon.\nIf you face any issues, you can contact the admin: {admin}\n\n🛒 <b>Purchased:</b> {item}\n💵 <b>Amount:</b> ₹{price}\n👤 <b>User ID:</b> <code>{uid}</code>",
        "success_order": "✅ Purchase completed! contact the admin and send your account ID and password to complete your order: {admin}\n\n🛒 <b>Purchased:</b> {item}\n💵 <b>Amount:</b> ₹{price}\n👤 <b>User ID:</b> <code>{uid}</code>",
        "ss_received": "धन्यवाद! आपका भुगतान प्रमाण प्राप्त हो गया है🧾\nभुगतान के सत्यापन के बाद राशि आपके बैलेंस में जोड़ दी जाएगी✅",
        "pay_msg": "💳 आप QR कोड को स्कैन करके या UPI ID का उपयोग करके भुगतान कर सकते हैं।\n\n👇 UPI ID कॉपी करने के लिए क्लिक करें:\n<code>{upi}</code>\n\nभुगतान पूरा करने के बाद, कृपया भुगतान का स्क्रीनशॉट यहाँ भेजें📱\n\nसत्यापित होने के बाद, राशि आपके बैलेंस में जोड़ दी जाएगी✅\n\n<b>नोट:</b>\nट्रांजेक्शन ID (UTR) और राशि स्क्रीनशॉट में स्पष्ट रूप से दिखाई देनी चाहिए🧾",
        "proofs_text": "You can verify all proofs on my social platforms✅\nI have posted them on my Telegram channel and WhatsApp community🌟 \n\nTelegram Channel📡-https://t.me/genzcarromhub\n\nWhatsApp Group☎️-https://whatsapp.com/channel/0029VbBRKgp1t90TfztVel16\n\nYouTube Channel▶️-https://youtu.be/NsLwPYUWuro?si=KXqBlAGiFVGTmdM2"
    }
}

def get_user(uid):
    uid_str = str(uid)
    if uid_str not in users_db:
        users_db[uid_str] = {"lang": "en", "balance": 0.0, "is_admin": False}
        save_db()
    return users_db[uid_str]

async def post_init(application: Application):
    await application.bot.set_my_commands([BotCommand("start", "Restart panel")])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; get_user(uid)
    if os.path.exists(TUTORIAL_VIDEO_PATH):
        try:
            with open(TUTORIAL_VIDEO_PATH, 'rb') as video:
                await update.message.reply_video(video=video, caption="📺 <b>Watch this Tutorial before starting!</b>", parse_mode="HTML")
        except Exception as e:
            logging.error(f"CRITICAL: Failed to send video file: {e}")
    else:
        logging.error(f"CRITICAL: {TUTORIAL_VIDEO_PATH} not found in directory!")

    kb = [[InlineKeyboardButton("English", callback_data='setlang_en'), InlineKeyboardButton("Hindi / हिंदी", callback_data='setlang_hi')]]
    await update.message.reply_text("Choose Language / भाषा चुनें:", reply_markup=InlineKeyboardMarkup(kb))

async def handle_ss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == MY_ADMIN_ID: return 
    try:
        await context.bot.send_message(chat_id=MY_ADMIN_ID, text=f"📥 <b>NEW PAYMENT SS</b>\n👤 From: {update.effective_user.mention_html()}\n🆔 ID: <code>{user_id}</code>", parse_mode="HTML")
        if update.message.photo: await context.bot.send_photo(chat_id=MY_ADMIN_ID, photo=update.message.photo[-1].file_id)
        elif update.message.document: await context.bot.send_document(chat_id=MY_ADMIN_ID, document=update.message.document.file_id)
        user = get_user(user_id)
        await update.message.reply_text(STRINGS[user['lang']]["ss_received"])
    except Exception as e: logging.error(f"Error: {e}")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; uid = str(query.from_user.id); data = query.data; await query.answer()
    user = get_user(uid); lang = user["lang"]; s = STRINGS[lang]

    if data.startswith("setlang_"):
        user["lang"] = data.split("_")[1]; save_db(); new_s = STRINGS[user["lang"]]
        kb = [[InlineKeyboardButton(new_s["buy_3"], callback_data="main_3D"), InlineKeyboardButton(new_s["buy_10"], callback_data="main_10D")],
            [InlineKeyboardButton(new_s["buy_30"], callback_data="main_30D")],
            [InlineKeyboardButton(new_s["coins_btn"], callback_data="menu_coins"), InlineKeyboardButton(new_s["pass_btn"], callback_data="menu_pass")],
            [InlineKeyboardButton(new_s["stock_btn"], callback_data="btn_stock")],
            [InlineKeyboardButton(new_s["balance"], callback_data="btn_bal"), InlineKeyboardButton(new_s["add_bal"], callback_data="btn_add"), InlineKeyboardButton(new_s["proofs_btn"], callback_data="btn_proofs")]]
        await query.edit_message_text(new_s["welcome"], reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")
    elif data == "btn_stock":
        await query.edit_message_text(STOCK_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"setlang_{lang}")]]), parse_mode="HTML")
    elif data == "btn_proofs":
        await query.edit_message_text(s["proofs_text"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"setlang_{lang}")]]), disable_web_page_preview=True)
    elif data == "btn_bal":
        await query.message.reply_text(f"💰 <b>Your Balance:</b> ₹{'{:.2f}'.format(user['balance'])} INR", parse_mode="HTML")
    elif data == "btn_add":
        cap = s["pay_msg"].format(upi=UPI_ID)
        try:
            with open(UPI_IMAGE_PATH, 'rb') as f: await query.message.reply_photo(f, caption=cap, parse_mode="HTML")
        except: await query.message.reply_text(cap, parse_mode="HTML")
    elif data == "menu_pass":
        p = PRICES["Carrom Pass"]
        await query.edit_message_text(f"🎟️ Carrom Pass - ₹{p}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data=f"buy_Carrom Pass_{p}")], [InlineKeyboardButton("🔙 Back", callback_data=f"setlang_{lang}")]]))
    elif data == "menu_coins":
        btns = [[InlineKeyboardButton("1Cr-₹250", callback_data="buy_1Cr Coins_250")], 
                [InlineKeyboardButton("5Cr-₹1200", callback_data="buy_5Cr Coins_1200")], 
                [InlineKeyboardButton("10Cr-₹2500", callback_data="buy_10Cr Coins_2500")], 
                [InlineKeyboardButton("🔙 Back", callback_data=f"setlang_{lang}")]]
        await query.edit_message_text("💎 Select Coins:", reply_markup=InlineKeyboardMarkup(btns))
    elif data.startswith("main_"):
        dur = data.split("_")[1]
        btns = [[InlineKeyboardButton("8BP", callback_data=f"gm_8BP_{dur}")], [InlineKeyboardButton("Carom", callback_data=f"gm_Carom_{dur}")], [InlineKeyboardButton("Soccer", callback_data=f"gm_Soccer_{dur}")]]
        await query.edit_message_text("🎮 Choose Game:", reply_markup=InlineKeyboardMarkup(btns))
    elif data.startswith("gm_"):
        _, g, d = data.split("_"); p = PRICES.get(f"{g}_{d}", 0)
        await query.edit_message_text(s["confirm"].format(item=f"{g} {d}", price=p), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirm", callback_data=f"buy_{g} {d}_{p}"), InlineKeyboardButton("❌ Cancel", callback_data=f"setlang_{lang}")]]), parse_mode="HTML")
    elif data.startswith("buy_"):
        parts = data.split("_"); item, p = parts[1], float(parts[2])
        if user["balance"] < p: 
            needed = p - user["balance"]
            error_msg = f"❌ Insufficient balance. You need to add ₹{'{:.2f}'.format(needed)}. Please restart the panel, click on “Add Money,” and proceed with the payment."
            await query.edit_message_text(error_msg)
        else:
            user["balance"] -= p; save_db()
            sale_notif = f"💰 <b>NEW SALE ALERT</b>\n\n👤 <b>User:</b> {query.from_user.mention_html()}\n🆔 <b>ID:</b> <code>{uid}</code>\n🛒 <b>Item:</b> {item}\n💵 <b>Price:</b> ₹{p}"
            await context.bot.send_message(chat_id=MY_ADMIN_ID, text=sale_notif, parse_mode="HTML")
            
            if "Coins" in item or "Pass" in item:
                success_msg = s["success_order"].format(admin=ADMIN_USERNAME, item=item, price=p, uid=uid)
            else:
                success_msg = s["success_key"].format(admin=ADMIN_USERNAME, item=item, price=p, uid=uid)
                
            await query.edit_message_text(success_msg, parse_mode="HTML")

async def admin_command(update, context): await update.message.reply_text("🔐 Password:"); return ADMIN_AUTH
async def admin_auth(update, context):
    if update.message.text == ADMIN_PASSWORD:
        user = get_user(update.effective_user.id); user["is_admin"] = True; save_db()
        await update.message.reply_text("✅ Admin Access Granted.\n/add ID AMT\n/key ID KEY TIME GAME\n/msg ID MESSAGE\n/broadcast MSG")
    return ConversationHandler.END

async def add_money(update, context):
    if not get_user(update.effective_user.id).get("is_admin"): return
    try:
        tid, amt = str(context.args[0]), float(context.args[1]); target = get_user(tid); target["balance"] += amt; save_db()
        await update.message.reply_text(f"✅ Added ₹{amt} to {tid}")
        await context.bot.send_message(chat_id=tid, text=f"💰 ₹{amt} added to your balance!")
    except: await update.message.reply_text("Usage: /add ID AMT")

async def send_key(update, context):
    if not get_user(update.effective_user.id).get("is_admin"): return
    try:
        tid, k, t, g = context.args[0], context.args[1], context.args[2], " ".join(context.args[3:])
        msg = (
            "Thank you for your purchase 🙏\n\n"
            "Please install the app and activate your key. If you face any problem, message @genzhub07 or call 982137811.\n\n"
            "<b>Snake Engine App 🐍</b>\nDownload Link:\nhttps://www.mediafire.com/file/puug7b8k7f49pl5/SE_2.0.13.apk/file\n\n"
            f"<b>{t} DAYS {g.upper()} Snake Engine Subscription 🔑</b>\nKEY: <code>{k}</code>\n\n"
            "<b>Steps to Activate:</b>\n1️⃣ Install the Snake Engine app.\n2️⃣ Open the app and go to the Profile section.\n3️⃣ Click on “Enter Key” and type your key.\n\n"
            "Your subscription will activate immediately.\nAfter activation, please send me a screenshot (SS)."
        )
        await context.bot.send_message(chat_id=tid, text=msg, parse_mode="HTML", disable_web_page_preview=True)
        await update.message.reply_text(f"✅ Sent to {tid}")
    except: await update.message.reply_text("Usage: /key ID KEY DAYS GAME")

async def send_private_msg(update, context):
    if not get_user(update.effective_user.id).get("is_admin"): return
    try:
        tid = context.args[0]
        msg_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=tid, text=msg_text, parse_mode="HTML")
        await update.message.reply_text(f"✅ Private message sent to {tid}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nUsage: /msg ID MESSAGE")

async def broadcast(update, context):
    if not get_user(update.effective_user.id).get("is_admin"): return
    msg_text = update.message.text[11:].strip() 
    if not msg_text:
        await update.message.reply_text("Usage: /broadcast YOUR MESSAGE")
        return
    count = 0
    for uid in users_db.keys():
        try: 
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>BROADCAST</b>\n\n{msg_text}", parse_mode="HTML")
            count += 1
        except: continue
    await update.message.reply_text(f"✅ Sent to {count} users.")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(ConversationHandler(entry_points=[CommandHandler('admin', admin_command)], states={ADMIN_AUTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_auth)]}, fallbacks=[]))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add_money))
    app.add_handler(CommandHandler("key", send_key))
    app.add_handler(CommandHandler("msg", send_private_msg))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & (~filters.COMMAND), handle_ss))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("Bot live..."); app.run_polling()

if __name__ == "__main__": main()
