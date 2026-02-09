"""
ProfileShare Bot - Professional Edition
Main entry point with separated User and Admin panels
"""

import os
import logging
import random
import asyncio
import secrets
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Import panels
from database import Database
from user_panel import show_user_menu, handle_user_callback
from admin_panel import show_admin_menu, handle_admin_callback, is_admin

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Configuration
X_PROFILE_LINK = os.getenv("X_PROFILE_LINK", "https://x.com/your_username")
GITHUB_PROFILE_LINK = os.getenv("GITHUB_PROFILE_LINK", "https://github.com/your_username")

# Anti-ban settings
MIN_DELAY = 3
MAX_DELAY = 8
COOLDOWN_MINUTES = 5
last_share_time = {}

# Messages for sharing
X_MESSAGES = [
    "🐦 Check out my X profile!\n\n{link}\n\nFollow for tech updates! 👆\n\n#X #Tech #Follow",
    "🚀 Let's connect on X!\n\n{link}\n\nCoding tips & tech news! 💻\n\n#X #Developer",
    "📱 Follow me on X\n\n{link}\n\nJoin the conversation! 🗣️\n\n#X #Tech",
]

GITHUB_MESSAGES = [
    "💻 Check out my GitHub!\n\n{link}\n\nStar my repos! ⭐\n\n#GitHub #OpenSource",
    "🚀 Explore my projects\n\n{link}\n\nContributions welcome! 🤝\n\n#GitHub #Developer",
    "📂 My code lives here:\n\n{link}\n\nFeel free to fork! 🍴\n\n#GitHub #Code",
]

COMBINED_MESSAGES = [
    "🔗 Connect with me!\n\n🐦 X: {x_link}\n💻 GitHub: {github_link}\n\nLet's grow! 🚀\n\n#X #GitHub",
    "📱 Follow my journey!\n\nX: {x_link}\nGitHub: {github_link}\n\nTech & code! 💡\n\n#Developer",
]


# ==================== UTILITY FUNCTIONS ====================

def check_cooldown(user_id: int) -> tuple[bool, str]:
    """Check cooldown for user."""
    last_time = last_share_time.get(user_id)
    if not last_time:
        return True, ""
    elapsed = datetime.now() - last_time
    if elapsed < timedelta(minutes=COOLDOWN_MINUTES):
        remaining = COOLDOWN_MINUTES - int(elapsed.total_seconds() / 60)
        return False, f"⏳ Please wait {remaining} minutes before sharing again."
    return True, ""


def update_share_time(user_id: int):
    """Update share timestamp."""
    last_share_time[user_id] = datetime.now()


async def random_delay():
    """Random delay for anti-ban."""
    await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


async def safe_send_message(bot, chat_id: str, text: str, parse_mode: str = None) -> bool:
    """Send message with safety measures."""
    try:
        await random_delay()
        await bot.send_chat_action(chat_id=chat_id, action='typing')
        await asyncio.sleep(random.uniform(1, 2))
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, disable_web_page_preview=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send to {chat_id}: {e}")
        return False


# ==================== MAIN ENTRY POINTS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command - routes to appropriate panel."""
    user = update.effective_user

    # Register/update user in database
    db.get_or_create_user(user.id, user.username, user.first_name)

    # Check if admin
    if is_admin(user.id):
        # Show admin menu
        await show_admin_menu(update, context)
        return

    # Check if has license
    has_license = db.has_active_license(user.id)

    if has_license:
        # Show user panel
        await show_user_menu(update, context)
    else:
        # Show purchase menu
        await show_purchase_menu(update, context)


async def show_purchase_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show purchase options to non-licensed users."""
    user = update.effective_user

    welcome_text = (
        f"👋 Welcome, {user.first_name}!\n\n"
        f"🤖 *ProfileShare Bot*\n\n"
        f"Automatically share your X and GitHub profiles "
        f"to Telegram channels with anti-ban protection.\n\n"
        f"✨ *Features:*\n"
        f"• Auto-post to multiple channels\n"
        f"• Anti-ban protection\n"
        f"• Message rotation\n"
        f"• Scheduled posting\n\n"
        f"📦 *Choose a Plan:*"
    )

    keyboard = [
        [InlineKeyboardButton("💎 Standard - $9.99/mo", callback_data='plan_standard')],
        [InlineKeyboardButton("👑 Premium - $19.99/mo", callback_data='plan_premium')],
        [InlineKeyboardButton("🔥 Lifetime - $49.99", callback_data='plan_lifetime')],
        [InlineKeyboardButton("🔑 I have a key", callback_data='activate_key')],
        [InlineKeyboardButton("📞 Support", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            welcome_text, reply_markup=reply_markup, parse_mode='Markdown'
        )


# ==================== CALLBACK ROUTER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callbacks to appropriate panel."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    # Admin panel callbacks
    if data.startswith('admin_') or data == 'back_to_main':
        handled = await handle_admin_callback(update, context, data)
        if handled:
            return

    # User panel callbacks
    if data.startswith('user_') or data in ['user_menu', 'user_renew']:
        handled = await handle_user_callback(update, context, data)
        if handled:
            return

    # Purchase flow callbacks
    if data.startswith('plan_'):
        plan = data.replace('plan_', '')
        await show_payment_info(update, context, plan)
        return

    if data == 'activate_key':
        await query.edit_message_text(
            "🔑 *Activate Your License*\n\n"
            "Send your license key:\n"
            "`/activate XXXX-XXXX-XXXX-XXXX`\n\n"
            "Need a key? Contact @YourSupport",
            parse_mode='Markdown'
        )
        return

    if data == 'support':
        await query.edit_message_text(
            "📞 *Support*\n\n"
            "For assistance, contact: @YourSupport\n\n"
            "For payment proof, use /proof command.",
            parse_mode='Markdown'
        )
        return

    if data == 'back_to_purchase':
        await show_purchase_menu(update, context)
        return

    logger.warning(f"Unhandled callback: {data}")


async def show_payment_info(update: Update, context: ContextTypes.DEFAULT_TYPE, plan: str) -> None:
    """Show payment information for a plan."""
    prices = {'standard': 9.99, 'premium': 19.99, 'lifetime': 49.99}
    price = prices.get(plan, 9.99)

    features = {
        'standard': "5 channels, Auto-post, Standard support",
        'premium': "15 channels, Priority auto-post, Premium support",
        'lifetime': "50 channels, Lifetime auto-post, VIP support"
    }

    text = (
        f"💳 *Purchase {plan.title()} Plan*\n\n"
        f"Price: *${price}*\n\n"
        f"Features:\n"
        f"• {features.get(plan, 'Basic features')}\n\n"
        f"*Payment Methods:*\n"
        f"• Crypto: `0xYourWalletAddress`\n"
        f"• PayPal: your.email@example.com\n\n"
        f"After payment, contact @YourSupport with proof."
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Plans", callback_data='back_to_purchase')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='Markdown'
    )


# ==================== COMMANDS ====================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command."""
    user = update.effective_user

    # Check if admin
    if is_admin(user.id):
        await show_admin_menu(update, context)
        return

    # Check if licensed
    if db.has_active_license(user.id):
        await show_user_menu(update, context)
        return

    # Unlicensed help
    help_text = (
        "🤖 *ProfileShare Bot*\n\n"
        "*Getting Started:*\n"
        "1. Purchase a license or enter your key\n"
        "2. Add channels you want to post to\n"
        "3. Start sharing or enable auto-post\n\n"
        "*Commands:*\n"
        "/start - Main menu\n"
        "/activate - Activate license key\n"
        "/help - Show this help\n\n"
        "Need a key? Click 'Support' in the menu."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Activate license command."""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            "🔑 *Activate License*\n\n"
            "Enter your license key:\n"
            "`/activate XXXX-XXXX-XXXX-XXXX`\n\n"
            "Don't have a key? Use /start to purchase.",
            parse_mode='Markdown'
        )
        return

    key = context.args[0].upper()

    # Validate format
    if len(key.replace('-', '')) != 16:
        await update.message.reply_text(
            "❌ Invalid key format. Use: `XXXX-XXXX-XXXX-XXXX`",
            parse_mode='Markdown'
        )
        return

    # Add dashes if missing
    if '-' not in key:
        key = '-'.join([key[i:i+4] for i in range(0, 16, 4)])

    # Activate
    success, message = db.activate_license(key, user.id, user.username)

    if success:
        await update.message.reply_text(
            f"✅ {message}\n\n"
            f"Your license is now active!\n"
            f"Use /start to access the bot.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ {message}\n\n"
            f"Contact support if you need help.",
            parse_mode='Markdown'
        )


async def generate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate license key (admin only)."""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin only.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/generate <plan> <days> [activations]`\n\n"
            "Plans: standard, premium, lifetime\n"
            "Days: 30, 90, 365, 0 (lifetime)\n\n"
            "Example: `/generate standard 30`",
            parse_mode='Markdown'
        )
        return

    plan = context.args[0].lower()
    days = int(context.args[1])
    activations = int(context.args[2]) if len(context.args) > 2 else 1

    if plan not in ['standard', 'premium', 'lifetime']:
        await update.message.reply_text("❌ Invalid plan.")
        return

    key = db.generate_license_key(plan, days if days > 0 else None, activations)

    await update.message.reply_text(
        f"✅ *License Key Generated*\n\n"
        f"Key: `{key}`\n"
        f"Plan: {plan.title()}\n"
        f"Duration: {days if days > 0 else 'Lifetime'} days\n"
        f"Activations: {activations}\n\n"
        f"Send this key to the customer.",
        parse_mode='Markdown'
    )


async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Revoke license key (admin only)."""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin only.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/revoke <key>`")
        return

    key = context.args[0].upper()
    if db.revoke_license(key):
        await update.message.reply_text(f"✅ License `{key}` has been revoked.", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ License not found.")


async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Look up user by ID, username, or license key (admin only)."""
    user = update.effective_user

    if not is_admin(user.id):
        await update.message.reply_text("❌ Admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "🔍 *User Lookup*\n\n"
            "Usage: `/lookup <user_id or @username or license_key>`\n\n"
            "Examples:\n"
            "`/lookup 123456789`\n"
            "`/lookup @username`\n"
            "`/lookup ABCD-1234-EFGH-5678`",
            parse_mode='Markdown'
        )
        return

    search_term = context.args[0]
    found = False

    # Search by user ID
    if search_term.isdigit():
        user_id = int(search_term)
        user_data = db.get_or_create_user(user_id, None, None)
        license_info = db.get_license_info(user_id)

        if license_info:
            found = True
            text = (
                f"👤 *User Found*\n\n"
                f"ID: `{user_id}`\n"
                f"Username: @{user_data.username or 'N/A'}\n"
                f"Name: {user_data.first_name or 'N/A'}\n\n"
                f"🔐 *License Info*\n"
                f"Plan: {license_info['plan'].title()}\n"
                f"Status: {license_info['status'].title()}\n"
                f"Max Channels: {license_info['max_channels']}\n"
            )
            if license_info['days_left'] is not None:
                text += f"Days Left: {license_info['days_left']}\n"
                text += f"Expires: {license_info['expires_at'].strftime('%Y-%m-%d')}\n"
            else:
                text += "Type: Lifetime 🔥\n"

            await update.message.reply_text(text, parse_mode='Markdown')

    # Search by license key
    elif '-' in search_term or len(search_term.replace('-', '')) == 16:
        key = search_term.upper()
        if '-' not in key:
            key = '-'.join([key[i:i+4] for i in range(0, 16, 4)])

        license = db.get_license_by_key(key)
        if license:
            found = True
            user_data = db.get_or_create_user(license.user_id, None, None) if license.user_id else None

            text = (
                f"🔐 *License Found*\n\n"
                f"Key: `{key[:12]}****`\n"
                f"Plan: {license.plan_type.title()}\n"
                f"Status: {license.status.title()}\n"
                f"Activations: {license.activations_used}/{license.max_activations}\n"
            )

            if license.user_id:
                text += f"\n👤 *Assigned to:*\n"
                text += f"ID: `{license.user_id}`\n"
                text += f"Username: @{license.username or 'N/A'}\n"
                if user_data:
                    text += f"Name: {user_data.first_name or 'N/A'}\n"
            else:
                text += "\n📭 *Not yet activated*\n"

            text += f"\nCreated: {license.created_at.strftime('%Y-%m-%d')}\n"
            if license.expires_at:
                text += f"Expires: {license.expires_at.strftime('%Y-%m-%d')}\n"
            else:
                text += "Type: Lifetime 🔥\n"

            await update.message.reply_text(text, parse_mode='Markdown')

    # Search by username
    elif search_term.startswith('@'):
        username = search_term[1:]
        # Search all licenses for this username
        all_licenses = db.get_all_licenses()
        user_licenses = [l for l in all_licenses if l.username and l.username.lower() == username.lower()]

        if user_licenses:
            found = True
            license = user_licenses[0]
            text = (
                f"👤 *User Found*\n\n"
                f"Username: @{username}\n"
                f"User ID: `{license.user_id}`\n\n"
                f"🔐 *License Info*\n"
                f"Plan: {license.plan_type.title()}\n"
                f"Status: {license.status.title()}\n"
            )
            if license.expires_at:
                text += f"Expires: {license.expires_at.strftime('%Y-%m-%d')}\n"
            else:
                text += "Type: Lifetime 🔥\n"

            await update.message.reply_text(text, parse_mode='Markdown')

    if not found:
        await update.message.reply_text(
            f"❌ No user or license found for: `{search_term}`\n\n"
            f"Try searching by:\n"
            f"• User ID (numbers)\n"
            f"• @username\n"
            f"• License key",
            parse_mode='Markdown'
        )


# ==================== MAIN ====================

def main() -> None:
    """Start the bot."""
    token = os.getenv("ADMIN_BOT_TOKEN")
    if not token:
        logger.error("ADMIN_BOT_TOKEN not found in .env!")
        return

    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CommandHandler("generate", generate_command))
    application.add_handler(CommandHandler("revoke", revoke_command))
    application.add_handler(CommandHandler("lookup", lookup_command))

    # Callback handler
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot started with User and Admin panels!")
    application.run_polling()


if __name__ == '__main__':
    main()
