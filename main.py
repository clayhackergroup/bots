import logging
import time
import hashlib
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== CONFIG =====
TOKEN = "8745375280:AAGYHHSOZzT_zVaPSoE6hqs6BMcyeZ06Cpw"
ADMIN_ID = 8754040441  # apna telegram id

# ===== DATA (use MongoDB later) =====
users = {}          # fake_username -> user_id
user_data = {}      # user_id -> info
blocked_users = set()
pending_msgs = {}   # sender -> target

# ===== HELPERS =====
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if user.id in blocked_users:
        return await update.message.reply_text("❌ You are blocked.")

    # If opened via link
    if args:
        target_name = args[0]
        if target_name in users:
            pending_msgs[user.id] = users[target_name]
            return await update.message.reply_text("📩 Send your anonymous message:")

    await update.message.reply_text(
        "👋 Welcome to Dark Horizon Confess Bot\n\n"
        "Use:\n/setname <username>\n/setpass <password>"
    )

# ===== SET USERNAME =====
async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id in user_data:
        return await update.message.reply_text("⚠️ You already created account.")

    if not context.args:
        return await update.message.reply_text("Usage: /setname <username>")

    name = context.args[0].lower()

    if name in users:
        return await update.message.reply_text("❌ Username taken.")

    users[name] = user.id
    user_data[user.id] = {
        "fake": name,
        "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "password": None
    }

    link = f"https://t.me/{context.bot.username}?start={name}"

    await update.message.reply_text(f"✅ Username set!\nYour link:\n{link}")

# ===== SET PASSWORD =====
async def setpass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if user.id not in user_data:
        return await update.message.reply_text("❌ Set username first.")

    if not context.args:
        return await update.message.reply_text("Usage: /setpass <password>")

    user_data[user.id]["password"] = hash_pass(context.args[0])

    await update.message.reply_text("🔐 Password set successfully!")

# ===== HANDLE MESSAGE =====
async def handle_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    if user.id in blocked_users:
        return

    # anonymous sending
    if user.id in pending_msgs:
        target = pending_msgs[user.id]

        await context.bot.send_message(
            target,
            f"📩 Anonymous Message:\n\n{text}"
        )

        del pending_msgs[user.id]
        return await update.message.reply_text("✅ Message sent!")

# ===== ADMIN: CHECK =====
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    name = context.args[0]
    if name not in users:
        return await update.message.reply_text("❌ Not found")

    uid = users[name]
    u = user_data.get(uid, {})

    await update.message.reply_text(
        f"👤 Info\n\n"
        f"Fake: {name}\n"
        f"ID: {uid}\n"
        f"Created: {u.get('created')}"
    )

# ===== ADMIN: BLOCK =====
async def block(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    uid = int(context.args[0])
    blocked_users.add(uid)

    await update.message.reply_text("🚫 User blocked")

# ===== ADMIN: WARN =====
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    uid = int(context.args[0])
    msg = " ".join(context.args[1:])

    await context.bot.send_message(uid, f"⚠️ Warning:\n{msg}")
    await update.message.reply_text("✅ Warn sent")

# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("setname", setname))
app.add_handler(CommandHandler("setpass", setpass))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("block", block))
app.add_handler(CommandHandler("warn", warn))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))

print("Bot running...")
app.run_polling()
