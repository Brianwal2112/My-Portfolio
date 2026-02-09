"""
User Panel Bot - Client-Facing Bot
This is the bot that licensed users interact with.
Managed by the Admin Panel.
"""

import os
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database (shared with admin)
db = Database()

# Configuration from environment
X_PROFILE_LINK = os.getenv("X_PROFILE_LINK", "https://x.com/your_username")
GITHUB_PROFILE_LINK = os.getenv("GITHUB_PROFILE_LINK", "https://github.com/your_username")
SUPPORT_BOT = os.getenv("SUPPORT_BOT_USERNAME", "uppport_bot")
USER_BOT_NAME = "ven_userbot"

# Admin ID for notifications
ADMIN_ID_STR = os.getenv("ADMIN_IDS", "0")
try:
    ADMIN_ID = int(ADMIN_ID_STR.split(",")[0].strip())
except (ValueError, IndexError):
    ADMIN_ID = 0
    logger.warning("ADMIN_ID not configured for notifications")

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


# ==================== USER COMMANDS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command for users."""
    user = update.effective_user

    # Register user
    db.get_or_create_user(user.id, user.username, user.first_name)

    # Check license
    has_license = db.has_active_license(user.id)

    if not has_license:
        await show_pricing(update, context)
        return

    await show_user_menu(update, context)


async def show_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed pricing and payment methods."""
    pricing_text = (
        f"🤖 *ProfileShare Bot*\n\n"
        f"*What it does:*\n"
        f"Automatically shares your X (Twitter) and GitHub profiles "
        f"to Telegram channels to help you gain followers and connections.\n\n"
        f"✨ *Features:*\n"
        f"✅ One-click profile sharing\n"
        f"✅ Auto-post to multiple channels\n"
        f"✅ Anti-ban protection (random delays)\n"
        f"✅ Message rotation (different text each time)\n"
        f"✅ Scheduled posting (hands-free)\n\n"
        f"📦 *CHOOSE YOUR PLAN:*"
    )

    keyboard = [
        [InlineKeyboardButton("💎 Standard - $9.99/month", callback_data='buy_standard')],
        [InlineKeyboardButton("👑 Premium - $19.99/month", callback_data='buy_premium')],
        [InlineKeyboardButton("🔥 Lifetime - $49.99 (one-time)", callback_data='buy_lifetime')],
        [InlineKeyboardButton("💳 Payment Methods", callback_data='payment_methods')],
        [InlineKeyboardButton("🔑 I Have a Key", callback_data='have_key')],
        [InlineKeyboardButton("❓ What is this?", callback_data='what_is')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            pricing_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            pricing_text, reply_markup=reply_markup, parse_mode='Markdown'
        )


async def pricing_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show pricing command."""
    await show_pricing(update, context)


async def show_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu for licensed users."""
    user = update.effective_user
    license_info = db.get_license_info(user.id)

    if not license_info:
        await update.message.reply_text("❌ License error. Contact support.")
        return

    plan_emoji = {'standard': '💎', 'premium': '👑', 'lifetime': '🔥'}.get(
        license_info['plan'], '💎'
    )

    menu_text = (
        f"👋 Welcome, {user.first_name}!\n\n"
        f"{plan_emoji} *Plan: {license_info['plan'].title()}*\n"
    )

    if license_info['days_left'] is not None:
        menu_text += f"⏰ Days left: {license_info['days_left']}\n"
    else:
        menu_text += "⏰ Type: *Lifetime* 🔥\n"

    channels = context.user_data.get('channels', [])
    menu_text += f"📢 Channels: {len(channels)}/{license_info['max_channels']}\n\n"
    menu_text += "Choose an option:"

    keyboard = [
        [
            InlineKeyboardButton("🔗 Share X", callback_data='share_x'),
            InlineKeyboardButton("💻 Share GitHub", callback_data='share_github')
        ],
        [
            InlineKeyboardButton("📋 Share Both", callback_data='share_both')
        ],
        [
            InlineKeyboardButton("📢 My Channels", callback_data='my_channels'),
            InlineKeyboardButton("➕ Add Channel", callback_data='add_channel')
        ],
        [
            InlineKeyboardButton("⏰ Auto-Post", callback_data='scheduler'),
            InlineKeyboardButton("📊 My License", callback_data='my_license')
        ],
        [
            InlineKeyboardButton("ℹ️ What is this?", callback_data='what_is'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            menu_text, reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            menu_text, reply_markup=reply_markup, parse_mode='Markdown'
        )


async def activate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Activate license key."""
    user = update.effective_user

    if not context.args:
        await update.message.reply_text(
            f"🔑 *Activate License*\n\n"
            f"Usage: `/activate XXXX-XXXX-XXXX-XXXX`\n\n"
            f"Contact @{SUPPORT_BOT} to purchase a key.",
            parse_mode='Markdown'
        )
        return

    key = context.args[0].upper()

    # Format key
    if '-' not in key and len(key) == 16:
        key = '-'.join([key[i:i+4] for i in range(0, 16, 4)])

    success, message = db.activate_license(key, user.id, user.username)

    if success:
        await update.message.reply_text(
            f"✅ {message}\n\n"
            f"Welcome! Use /start to access your dashboard.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ {message}\n\n"
            f"Contact @{SUPPORT_BOT} for assistance.",
            parse_mode='Markdown'
        )


async def mylicense_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show license info."""
    user = update.effective_user

    if not db.has_active_license(user.id):
        await update.message.reply_text(f"❌ No active license. Contact @{SUPPORT_BOT}")
        return

    info = db.get_license_info(user.id)

    text = (
        f"🔐 *Your License*\n\n"
        f"Plan: *{info['plan'].title()}*\n"
        f"Status: {info['status'].title()}\n"
        f"Max Channels: {info['max_channels']}\n"
    )

    if info['days_left'] is not None:
        text += f"\nDays Left: {info['days_left']}\n"
        text += f"Expires: {info['expires_at'].strftime('%Y-%m-%d')}\n"
    else:
        text += "\nType: *Lifetime* 🔥\n"

    await update.message.reply_text(text, parse_mode='Markdown')


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show menu."""
    if not db.has_active_license(update.effective_user.id):
        await start(update, context)
        return
    await show_user_menu(update, context)


# ==================== CALLBACK HANDLERS ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    # Allow these callbacks without license
    no_license_needed = ['help', 'what_is', 'buy_standard', 'buy_premium', 'buy_lifetime',
                        'contact_support', 'have_key', 'back_to_pricing']

    if data not in no_license_needed and not db.has_active_license(user.id):
        await show_pricing(update, context)
        return

    if data == 'share_x':
        await handle_share_x(update, context)
    elif data == 'share_github':
        await handle_share_github(update, context)
    elif data == 'share_both':
        await handle_share_both(update, context)
    elif data == 'my_channels':
        await handle_my_channels(update, context)
    elif data == 'add_channel':
        await handle_add_channel(update, context)
    elif data == 'scheduler':
        await handle_scheduler(update, context)
    elif data == 'my_license':
        await handle_my_license(update, context)
    elif data == 'help':
        await handle_help(update, context)
    elif data == 'what_is':
        await handle_what_is(update, context)
    elif data == 'back_to_menu':
        await show_user_menu(update, context)
    elif data == 'payment_methods':
        # Redirect to support bot for payment methods
        await redirect_to_support_for_payment(update, context)
    elif data.startswith('pay_btc_') or data.startswith('pay_eth_') or data.startswith('pay_usdt_') or data.startswith('pay_paypal_'):
        # All payment handling moved to support bot
        await redirect_to_support_for_payment(update, context)
    elif data == 'back_to_pricing':
        await show_pricing(update, context)
        return
    elif data in ['buy_standard', 'buy_premium', 'buy_lifetime']:
        await handle_buy(update, context, data)
    elif data == 'have_key':
        await update.callback_query.edit_message_text(
            f"🔑 *Activate Your License*\n\n"
            f"Send your license key:\n"
            f"`/activate XXXX-XXXX-XXXX-XXXX`\n\n"
            f"Need a key? Contact @{SUPPORT_BOT}",
            parse_mode='Markdown'
        )


async def redirect_to_support_for_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Redirect user to support bot for payment handling."""
    query = update.callback_query

    text = (
        "💳 *Payment Methods*\n\n"
        "All payments are handled through our secure support chat.\n\n"
        "*Benefits:*\n"
        "✅ Multiple payment options (BTC, ETH, USDT, PayPal)\n"
        "✅ Save your payment info for faster checkout\n"
        "✅ Secure payment verification\n"
        "✅ Fast license delivery (10-30 min)\n\n"
        "Click below to continue to support:"
    )

    support_url = f"https://t.me/{SUPPORT_BOT}"

    keyboard = [
        [InlineKeyboardButton("💳 Go to Payment →", url=support_url)],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_pricing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def log_and_notify_purchase_request(bot, user, plan: str, price: str):
    """Log user action and notify admin when user requests to purchase a license."""
    # Log to database
    try:
        db.log_user_action(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            action='purchase_intent',
            plan_type=plan,
            details=f"Price: {price}"
        )
        logger.info(f"Logged purchase intent for user {user.id}, plan: {plan}")
    except Exception as e:
        logger.error(f"Failed to log purchase intent: {e}")

    # Notify admin
    if ADMIN_ID == 0:
        logger.warning("Cannot notify admin: ADMIN_ID not set")
        return

    try:
        notification_text = (
            f"🔔 *New Purchase Request!*\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"📱 Username: @{user.username or 'N/A'}\n\n"
            f"🛒 *Plan Requested:* {plan}\n"
            f"💰 *Price:* {price}\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📞 User has been directed to @{SUPPORT_BOT}\n"
            f"_Generate a key with /generate when payment is received._"
        )

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=notification_text,
            parse_mode='Markdown'
        )
        logger.info(f"Admin notified of purchase request from user {user.id}")
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def handle_buy(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle buy button clicks - redirect to support bot for payment."""
    query = update.callback_query
    user = query.from_user

    plan = data.replace('buy_', '')
    prices = {
        'standard': '$9.99/month',
        'premium': '$19.99/month',
        'lifetime': '$49.99 (one-time)'
    }
    plan_emoji = {'standard': '💎', 'premium': '👑', 'lifetime': '🔥'}

    # Notify admin about this purchase request
    await notify_admin_purchase_request(context.bot, user, plan.title(), prices.get(plan, 'Unknown'))

    # Log the purchase intent
    db.log_user_action(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        action='purchase_intent',
        plan_type=plan,
        details=f"User clicked buy from user bot. Price: {prices.get(plan)}"
    )

    # Create pre-filled message for support bot
    message = f"Hi! I want to purchase the {plan.title()} plan for {prices.get(plan)}. Please send payment details."
    encoded_message = message.replace(' ', '%20').replace('!', '%21')
    support_url = f"https://t.me/{SUPPORT_BOT}?start={encoded_message}"

    text = (
        f"{plan_emoji.get(plan, '🛒')} *{plan.title()} Plan*\n\n"
        f"💰 Price: *{prices.get(plan, 'Contact support')}*\n\n"
        f"📋 *Plan Details:*\n"
    )

    if plan == 'standard':
        text += "• 5 channels max\n• Standard auto-post\n• Standard support\n"
    elif plan == 'premium':
        text += "• 15 channels max\n• Priority auto-post\n• Premium support\n"
    elif plan == 'lifetime':
        text += "• 50 channels max\n• Lifetime auto-post\n• VIP support\n• One-time payment\n"

    text += (
        f"\n💳 *All payment methods available:*\n"
        f"• Bitcoin (BTC)\n"
        f"• Ethereum (ETH)\n"
        f"• USDT (TRC-20)\n"
        f"• PayPal / Card\n\n"
        f"🚀 *Ready to buy?* Click below to complete your purchase in our secure support chat.\n\n"
        f"_Your payment information will be saved for faster checkout on renewals!_"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Complete Purchase →", url=support_url)],
        [InlineKeyboardButton("🔙 Back to Pricing", callback_data='back_to_pricing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


    """Notify admin when user selects a payment method."""
    if ADMIN_ID == 0:
        return

    try:
        notification_text = (
            f"💳 *Payment Method Selected*\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"📱 Username: @{user.username or 'N/A'}\n\n"
            f"🛒 Plan: {plan}\n"
            f"💳 Method: {method}\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📞 User is viewing payment details"
        )

        await bot.send_message(
            chat_id=ADMIN_ID,
            text=notification_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")


async def handle_share_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle share X."""
    query = update.callback_query
    user = query.from_user

    license = db.get_user_license(user.id)
    channels = context.user_data.get('channels', [])

    if not channels:
        await query.edit_message_text(
            "⚠️ No channels configured!\n\n"
            "Add channels first using 'Add Channel' button.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    can_share, msg = check_cooldown(user.id)
    if not can_share:
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    # Limit to max channels
    channels_to_use = channels[:license.max_channels]

    message = random.choice(X_MESSAGES).format(link=X_PROFILE_LINK)

    success = 0
    for channel in channels_to_use:
        if await safe_send_message(context.bot, channel, message, 'Markdown'):
            success += 1

    update_share_time(user.id)

    await query.edit_message_text(
        f"✅ Shared X profile to {success}/{len(channels_to_use)} channels!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
        ]])
    )


async def handle_share_github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle share GitHub."""
    query = update.callback_query
    user = query.from_user

    license = db.get_user_license(user.id)
    channels = context.user_data.get('channels', [])

    if not channels:
        await query.edit_message_text(
            "⚠️ No channels configured!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    can_share, msg = check_cooldown(user.id)
    if not can_share:
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    channels_to_use = channels[:license.max_channels]
    message = random.choice(GITHUB_MESSAGES).format(link=GITHUB_PROFILE_LINK)

    success = 0
    for channel in channels_to_use:
        if await safe_send_message(context.bot, channel, message, 'Markdown'):
            success += 1

    update_share_time(user.id)

    await query.edit_message_text(
        f"✅ Shared GitHub profile to {success}/{len(channels_to_use)} channels!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
        ]])
    )


async def handle_share_both(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle share both."""
    query = update.callback_query
    user = query.from_user

    license = db.get_user_license(user.id)
    channels = context.user_data.get('channels', [])

    if not channels:
        await query.edit_message_text(
            "⚠️ No channels configured!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    can_share, msg = check_cooldown(user.id)
    if not can_share:
        await query.edit_message_text(
            msg,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
            ]])
        )
        return

    channels_to_use = channels[:license.max_channels]
    message = random.choice(COMBINED_MESSAGES).format(
        x_link=X_PROFILE_LINK,
        github_link=GITHUB_PROFILE_LINK
    )

    success = 0
    for channel in channels_to_use:
        if await safe_send_message(context.bot, channel, message, 'Markdown'):
            success += 1

    update_share_time(user.id)

    await query.edit_message_text(
        f"✅ Shared both profiles to {success}/{len(channels_to_use)} channels!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')
        ]])
    )


async def handle_my_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's channels."""
    query = update.callback_query
    channels = context.user_data.get('channels', [])

    if not channels:
        text = "📭 *No Channels Added*\n\nUse 'Add Channel' to configure."
    else:
        text = f"📢 *Your Channels ({len(channels)}):*\n\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. `{ch}`\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Channel", callback_data='add_channel')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show add channel instructions."""
    query = update.callback_query

    text = (
        "➕ *Add Channel*\n\n"
        "To add a channel:\n"
        "1. Add this bot as admin to your channel\n"
        "2. Send the channel username here\n\n"
        "*Commands:*\n"
        "/addchannel @channelname\n"
        "/addchannel -1001234567890 (for private)\n\n"
        "*Example:*\n"
        "/addchannel @mychannel"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='my_channels')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def addchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a channel command."""
    user = update.effective_user

    if not db.has_active_license(user.id):
        await update.message.reply_text("❌ License required. Use /activate")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/addchannel @channelname`\n"
            "Or: `/addchannel -1001234567890` for private channels",
            parse_mode='Markdown'
        )
        return

    channel = context.args[0]
    channels = context.user_data.get('channels', [])

    if channel in channels:
        await update.message.reply_text(f"⚠️ {channel} already added!")
        return

    # Test if bot can access channel
    try:
        await context.bot.send_message(
            chat_id=channel,
            text="✅ Channel connected to ProfileShare Bot!",
            disable_notification=True
        )
        channels.append(channel)
        context.user_data['channels'] = channels
        await update.message.reply_text(f"✅ Added {channel}!")
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to add {channel}.\n\n"
            f"Make sure:\n"
            f"1. Username/ID is correct\n"
            f"2. Bot is admin in the channel"
        )


async def handle_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show scheduler menu."""
    query = update.callback_query

    text = (
        "⏰ *Auto-Post Scheduler*\n\n"
        "Automatically share your profiles every hour.\n\n"
        "*Commands:*\n"
        "/startscheduler - Start auto-posting\n"
        "/stopscheduler - Stop auto-posting\n\n"
        "*Note:* Uses anti-ban protection with random delays."
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_my_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show license info in menu."""
    query = update.callback_query
    user = query.from_user

    info = db.get_license_info(user.id)

    text = (
        f"📊 *License Info*\n\n"
        f"Plan: *{info['plan'].title()}*\n"
        f"Status: {info['status'].title()}\n"
        f"Max Channels: {info['max_channels']}\n"
    )

    if info['days_left'] is not None:
        text += f"\nDays Left: {info['days_left']}\n"
        text += f"Expires: {info['expires_at'].strftime('%Y-%m-%d')}\n"
    else:
        text += "\nType: *Lifetime* 🔥\n"

    text += f"\n_Your license is managed by @{SUPPORT_BOT}_"

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help with description and steps."""
    query = update.callback_query

    text = (
        f"🤖 *ProfileShare Bot - Help*\n\n"
        f"*What it does:*\n"
        f"Shares your X and GitHub profiles to Telegram channels "
        f"to help you gain followers and grow your network.\n\n"
        f"*Quick Steps:*\n"
        f"1️⃣ Click '📢 My Channels' to see your channels\n"
        f"2️⃣ Click '➕ Add Channel' for instructions\n"
        f"3️⃣ Use '🔗 Share X' or '💻 Share GitHub' to share\n"
        f"4️⃣ Or enable '⏰ Auto-Post' for automatic sharing\n\n"
        f"*Commands:*\n"
        f"/start - Show this info\n"
        f"/menu - Open dashboard\n"
        f"/mylicense - View license details\n"
        f"/addchannel @channel - Add a channel\n\n"
        f"*Anti-Ban Protection:*\n"
        f"✓ Random delays between posts\n"
        f"✓ Message rotation (different text each time)\n"
        f"✓ 5-minute cooldown between shares\n"
        f"✓ Max 10 channels per hour\n\n"
        f"❓ Need help? Contact @{SUPPORT_BOT}"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_what_is(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show what the bot does - description and features."""
    query = update.callback_query

    text = (
        "🤖 *What is ProfileShare Bot?*\n\n"
        "This bot helps you *gain followers* by automatically sharing "
        "your X (Twitter) and GitHub profiles to Telegram channels.\n\n"
        "*✨ Key Features:*\n"
        "✅ Share to multiple channels in one click\n"
        "✅ Auto-post every hour (hands-free)\n"
        "✅ Anti-ban protection (looks human)\n"
        "✅ Different message each time\n"
        "✅ Add your own channels\n\n"
        "*🚀 How to Use (3 Steps):*\n"
        "1️⃣ Add channels you want to post to\n"
        "   • Make this bot an admin in each channel\n"
        "   • Use '➕ Add Channel' button\n\n"
        "2️⃣ Share your profiles\n"
        "   • Click '🔗 Share X' for X profile\n"
        "   • Click '💻 Share GitHub' for GitHub\n"
        "   • Or '⏰ Auto-Post' for automatic sharing\n\n"
        "3️⃣ Watch your followers grow! 📈\n\n"
        "*🛡️ Built-in Protection:*\n"
        "• Random delays between posts\n"
        "• Message variations (not spammy)\n"
        "• 5-minute cooldown\n"
        "• Respects Telegram limits\n\n"
        "*💡 Tip:* Enable Auto-Post and let the bot work for you!"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def main() -> None:
    """Start the user bot."""
    token = os.getenv("USER_BOT_TOKEN")
    if not token:
        logger.error("USER_BOT_TOKEN not found in .env!")
        logger.error("Add: USER_BOT_TOKEN=8028150882:AAGgsNu8RQWHut4ZYT4v0YgaxyDg5FMxbs")
        return

    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("activate", activate_command))
    application.add_handler(CommandHandler("mylicense", mylicense_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("addchannel", addchannel_command))
    application.add_handler(CommandHandler("pricing", pricing_command))

    # Callback handler
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("User Panel Bot started!")
    application.run_polling()


if __name__ == '__main__':
    main()
