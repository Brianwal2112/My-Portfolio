"""
Support Bot - Customer Service Bot
Handles customer inquiries, payment verification, and license requests
Connects users with admin for purchases and support
"""

import os
import logging
import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv
from database import Database

# Load environment variables FIRST
load_dotenv()

# Initialize database
db = Database()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get admin ID from environment
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "0")
logger.info(f"ADMIN_IDS from env: {ADMIN_IDS_STR}")

try:
    ADMIN_ID = int(ADMIN_IDS_STR.split(",")[0].strip())
    logger.info(f"Admin ID set to: {ADMIN_ID}")
except (ValueError, IndexError) as e:
    logger.error(f"Failed to parse ADMIN_ID: {e}")
    ADMIN_ID = 0

SUPPORT_BOT_USERNAME = os.getenv("SUPPORT_BOT_USERNAME", "uppport_bot")
# Remove @ if present for URL building, add it back for display
SUPPORT_BOT_HANDLE = SUPPORT_BOT_USERNAME.lstrip('@')

# Conversation states for payment setup and proof submission
WAITING_FOR_BTC_ADDRESS = 1
WAITING_FOR_ETH_ADDRESS = 2
WAITING_FOR_USDT_ADDRESS = 3
WAITING_FOR_PAYPAL_EMAIL = 4
WAITING_FOR_CARD_INFO = 5

# ETH address for payments (from .env or default)
ETH_PAYMENT_ADDRESS = os.getenv("ETH_PAYMENT_ADDRESS", "0xb3e5100AC212b1FAcC32Fd4dA6D387251D385C2f")

# ==================== START COMMAND ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command for support bot."""
    user = update.effective_user
    logger.info(f"Start command from user: {user.id} ({user.username or 'N/A'})")

    # Register user in database
    db.get_or_create_user(user.id, user.username, user.first_name)

    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        f"🤖 *ProfileShare Support*\n\n"
        f"How can I help you today?\n\n"
        f"*Quick Options:*"
    )

    keyboard = [
        [InlineKeyboardButton("💰 Buy License", callback_data='buy_license')],
        [InlineKeyboardButton("📸 Submit Proof", callback_data='submit_proof')],
        [InlineKeyboardButton("💳 Payment Methods", callback_data='payment_methods')],
        [InlineKeyboardButton("❓ General Question", callback_data='general_question')],
        [InlineKeyboardButton("🎫 Payment Issue", callback_data='payment_issue')],
        [InlineKeyboardButton("🔑 License Problem", callback_data='license_problem')],
        [InlineKeyboardButton("📋 View Pricing", callback_data='view_pricing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== BUTTON HANDLER ====================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user
    logger.info(f"Button pressed by {user.id}: {data}")

    try:
        if data == 'buy_license':
            await handle_buy_license(update, context)
        elif data == 'submit_proof':
            await proof_command(update, context)
        elif data == 'payment_methods':
            await handle_payment_methods(update, context)
        elif data == 'add_payment_method':
            await handle_add_payment_method(update, context)
        elif data == 'view_saved_methods':
            await handle_view_saved_methods(update, context)
        elif data == 'set_default_method':
            await handle_set_default_method(update, context)
        elif data.startswith('buy_plan_'):
            plan = data.replace('buy_plan_', '')
            await handle_buy_plan(update, context, plan)
        elif data.startswith('pay_'):
            # Handle pay_btc, pay_eth, pay_usdt, pay_paypal, pay_card
            await handle_payment_selection(update, context, data)
        elif data == 'general_question':
            await handle_general_question(update, context)
        elif data == 'payment_issue':
            await handle_payment_issue(update, context)
        elif data == 'license_problem':
            await handle_license_problem(update, context)
        elif data == 'view_pricing':
            await handle_view_pricing(update, context)
        elif data == 'back_to_menu':
            await start_from_callback(update, context)
        else:
            logger.warning(f"Unknown callback data: {data}")
    except Exception as e:
        logger.error(f"Error handling button {data}: {e}")
        try:
            await query.edit_message_text(
                "❌ An error occurred. Please try again or send a direct message.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')
                ]])
            )
        except:
            pass


async def start_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show start menu from callback (for back button)."""
    query = update.callback_query
    user = query.from_user

    welcome_text = (
        f"👋 Hello, {user.first_name}!\n\n"
        f"🤖 *ProfileShare Support*\n\n"
        f"How can I help you today?\n\n"
        f"*Quick Options:*"
    )

    keyboard = [
        [InlineKeyboardButton("💰 Buy License", callback_data='buy_license')],
        [InlineKeyboardButton("❓ General Question", callback_data='general_question')],
        [InlineKeyboardButton("💳 Payment Issue", callback_data='payment_issue')],
        [InlineKeyboardButton("🔑 License Problem", callback_data='license_problem')],
        [InlineKeyboardButton("📋 View Pricing", callback_data='view_pricing')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== TOPIC HANDLERS ====================

async def handle_buy_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle buy license request."""
    query = update.callback_query

    text = (
        "💰 *Purchase a License*\n\n"
        "*Choose your plan:*\n\n"
        "💎 *Standard - $9.99/month*\n"
        "• 5 channels\n"
        "• Auto-post included\n"
        "• Standard support\n\n"
        "👑 *Premium - $19.99/month*\n"
        "• 15 channels\n"
        "• Priority auto-post\n"
        "• Premium support\n\n"
        "🔥 *Lifetime - $49.99*\n"
        "• 50 channels (forever)\n"
        "• Lifetime auto-post\n"
        "• VIP support\n\n"
        "*Payment Methods:*\n"
        "• Bitcoin (BTC)\n"
        "• Ethereum (ETH)\n"
        "• USDT (TRC-20)\n"
        "• PayPal\n\n"
        "✏️ *Send me a message with:*\n"
        "1. Which plan you want\n"
        "2. Your preferred payment method\n"
        "3. Any questions you have\n\n"
        "_I'll connect you with an admin to complete your purchase._"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_general_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general question."""
    query = update.callback_query

    text = (
        "❓ *General Questions*\n\n"
        "*Common Questions:*\n\n"
        "*Q: What does ProfileShare Bot do?*\n"
        "A: It automatically shares your X and GitHub profiles to Telegram channels to help you gain followers.\n\n"
        "*Q: Is it safe to use?*\n"
        "A: Yes! It has anti-ban protection with random delays and message rotation.\n\n"
        "*Q: How many channels can I add?*\n"
        "A: Depends on your plan: 5 (Standard), 15 (Premium), or 50 (Lifetime).\n\n"
        "*Q: Can I share to any channel?*\n"
        "A: You need to be an admin of the channels you want to share to.\n\n"
        "✏️ *Have another question?*\n"
        "Just send me a message and I'll help you out!"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_payment_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment issue."""
    query = update.callback_query

    text = (
        "💳 *Payment Support*\n\n"
        "I'm here to help with payment issues!\n\n"
        "*Common Issues:*\n"
        "• Transaction not going through\n"
        "• Payment confirmation delays\n"
        "• Wrong amount sent\n"
        "• Refund requests\n\n"
        "✏️ *Please send me:*\n"
        "1. Your issue description\n"
        "2. Transaction ID (if available)\n"
        "3. Payment method used\n"
        "4. Amount sent\n\n"
        "_I'll connect you with support immediately._"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_license_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle license problem."""
    query = update.callback_query

    text = (
        "🔑 *License Support*\n\n"
        "Having trouble with your license?\n\n"
        "*Common Issues:*\n"
        "• Key not working\n"
        "• License expired early\n"
        "• Lost your license key\n"
        "• Need to transfer to new account\n"
        "• Activation failed\n\n"
        "✏️ *Please send me:*\n"
        "1. Your license key (or last 4 digits)\n"
        "2. Description of the problem\n"
        "3. When you purchased it\n\n"
        "_I'll help you resolve this quickly!_"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_view_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show pricing information."""
    query = update.callback_query

    text = (
        "📋 *ProfileShare Pricing*\n\n"
        "💎 *Standard Plan*\n"
        "Price: $9.99/month\n"
        "Channels: 5 max\n"
        "Auto-post: ✅\n"
        "Support: Standard\n\n"
        "👑 *Premium Plan*\n"
        "Price: $19.99/month\n"
        "Channels: 15 max\n"
        "Auto-post: ✅ Priority\n"
        "Support: Premium\n\n"
        "🔥 *Lifetime Plan*\n"
        "Price: $49.99 (one-time)\n"
        "Channels: 50 max\n"
        "Auto-post: ✅ Lifetime\n"
        "Support: VIP\n\n"
        "💳 *Accepted Payments:*\n"
        "• Bitcoin (BTC)\n"
        "• Ethereum (ETH)\n"
        "• USDT (TRC-20)\n"
        "• PayPal\n"
        "• Credit/Debit Card"
    )

    keyboard = [
        [InlineKeyboardButton("💰 Buy Now", callback_data='buy_license')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== PAYMENT METHODS ====================

async def handle_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show payment methods management."""
    query = update.callback_query
    user = query.from_user

    # Get user's saved payment methods
    credentials = db.get_user_payment_credentials(user.id)
    default_method = db.get_default_payment_method(user.id)

    text = (
        "💳 *Payment Methods*\n\n"
        "Manage your saved payment methods for faster checkout on future purchases.\n\n"
    )

    if credentials:
        text += "*Your Saved Methods:*\n"
        for cred in credentials:
            default_mark = " ✅ Default" if cred.is_default else ""
            if cred.payment_method == 'btc' and cred.btc_address:
                text += f"• ₿ Bitcoin: `{cred.btc_address[:8]}...{cred.btc_address[-8:]}`{default_mark}\n"
            elif cred.payment_method == 'eth' and cred.eth_address:
                text += f"• Ξ Ethereum: `{cred.eth_address[:8]}...{cred.eth_address[-8:]}`{default_mark}\n"
            elif cred.payment_method == 'usdt' and cred.usdt_address:
                text += f"• 💵 USDT: `{cred.usdt_address[:8]}...{cred.usdt_address[-8:]}`{default_mark}\n"
            elif cred.payment_method == 'paypal' and cred.paypal_email:
                text += f"• 💳 PayPal: `{cred.paypal_email}`{default_mark}\n"
            elif cred.payment_method == 'card' and cred.card_last_four:
                text += f"• 💳 Card: ****{cred.card_last_four}{default_mark}\n"
    else:
        text += "_No saved payment methods yet._\n"

    text += "\n*What would you like to do?*"

    keyboard = [
        [InlineKeyboardButton("➕ Add Payment Method", callback_data='add_payment_method')],
        [InlineKeyboardButton("👁 View Saved Methods", callback_data='view_saved_methods')],
        [InlineKeyboardButton("⭐ Set Default Method", callback_data='set_default_method')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_add_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show options to add a payment method."""
    query = update.callback_query

    text = (
        "➕ *Add Payment Method*\n\n"
        "Select the payment method you want to save:\n\n"
        "*Crypto (for refunds/verification):*\n"
        "• Bitcoin - Save your BTC wallet address\n"
        "• Ethereum - Save your ETH wallet address\n"
        "• USDT (TRC-20) - Save your USDT wallet address\n\n"
        "*Traditional:*\n"
        "• PayPal - Save your PayPal email\n"
        "• Card - Save last 4 digits for reference\n\n"
        "⚠️ *Note:* We only store partial info for security. "
        "Full payment details will be provided when you make a purchase."
    )

    keyboard = [
        [InlineKeyboardButton("₿ Bitcoin", callback_data='pay_setup_btc')],
        [InlineKeyboardButton("Ξ Ethereum", callback_data='pay_setup_eth')],
        [InlineKeyboardButton("💵 USDT (TRC-20)", callback_data='pay_setup_usdt')],
        [InlineKeyboardButton("💳 PayPal", callback_data='pay_setup_paypal')],
        [InlineKeyboardButton("💳 Credit/Debit Card", callback_data='pay_setup_card')],
        [InlineKeyboardButton("🔙 Back", callback_data='payment_methods')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_view_saved_methods(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed view of saved payment methods."""
    query = update.callback_query
    user = query.from_user

    credentials = db.get_user_payment_credentials(user.id)

    if not credentials:
        text = (
            "📭 *No Saved Payment Methods*\n\n"
            "You haven't saved any payment methods yet.\n\n"
            "Add a payment method to speed up future purchases!"
        )
        keyboard = [
            [InlineKeyboardButton("➕ Add Payment Method", callback_data='add_payment_method')],
            [InlineKeyboardButton("🔙 Back", callback_data='payment_methods')]
        ]
    else:
        text = "💳 *Your Saved Payment Methods*\n\n"

        for i, cred in enumerate(credentials, 1):
            default_mark = " ⭐ DEFAULT" if cred.is_default else ""
            text += f"*{i}. {cred.payment_method.upper()}{default_mark}*\n"

            if cred.payment_method == 'btc' and cred.btc_address:
                text += f"   Address: `{cred.btc_address[:12]}...{cred.btc_address[-12:]}`\n"
            elif cred.payment_method == 'eth' and cred.eth_address:
                text += f"   Address: `{cred.eth_address[:12]}...{cred.eth_address[-12:]}`\n"
            elif cred.payment_method == 'usdt' and cred.usdt_address:
                text += f"   Address: `{cred.usdt_address[:12]}...{cred.usdt_address[-12:]}`\n"
            elif cred.payment_method == 'paypal' and cred.paypal_email:
                text += f"   Email: `{cred.paypal_email}`\n"
            elif cred.payment_method == 'card' and cred.card_last_four:
                text += f"   Card: **** **** **** {cred.card_last_four}\n"

            if cred.notes:
                text += f"   Note: {cred.notes}\n"
            text += f"   Added: {cred.created_at.strftime('%Y-%m-%d')}\n\n"

        keyboard = [
            [InlineKeyboardButton("➕ Add Another", callback_data='add_payment_method')],
            [InlineKeyboardButton("⭐ Set Default", callback_data='set_default_method')],
            [InlineKeyboardButton("🔙 Back", callback_data='payment_methods')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_set_default_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show interface to set default payment method."""
    query = update.callback_query
    user = query.from_user

    credentials = db.get_user_payment_credentials(user.id)

    if not credentials:
        await query.edit_message_text(
            "📭 *No Saved Methods*\n\n"
            "You need to add a payment method first!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Payment Method", callback_data='add_payment_method')],
                [InlineKeyboardButton("🔙 Back", callback_data='payment_methods')]
            ]),
            parse_mode='Markdown'
        )
        return

    text = "⭐ *Set Default Payment Method*\n\nSelect your preferred method:"

    keyboard = []
    for cred in credentials:
        method_name = {
            'btc': '₿ Bitcoin',
            'eth': 'Ξ Ethereum',
            'usdt': '💵 USDT',
            'paypal': '💳 PayPal',
            'card': '💳 Card'
        }.get(cred.payment_method, cred.payment_method)

        default_mark = " ✅" if cred.is_default else ""
        keyboard.append([InlineKeyboardButton(
            f"{method_name}{default_mark}",
            callback_data=f'set_default_{cred.payment_method}'
        )])

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='payment_methods')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_set_default_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle setting default payment method."""
    query = update.callback_query
    user = query.from_user
    method = query.data.replace('set_default_', '')

    success = db.set_default_payment_method(user.id, method)

    if success:
        await query.answer(f"✅ {method.upper()} set as default!")
        await handle_set_default_method(update, context)
    else:
        await query.answer("❌ Failed to set default")


# ==================== BUY LICENSE FLOW ====================

async def handle_buy_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle buy license - show plans."""
    query = update.callback_query
    user = query.from_user

    # Log purchase intent
    db.log_user_action(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        action='purchase_intent'
    )

    # Notify admin
    if ADMIN_ID != 0:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🔔 *New Purchase Intent!*\n\n"
                    f"👤 User: {user.first_name}\n"
                    f"🆔 ID: `{user.id}`\n"
                    f"📱 @{user.username or 'N/A'}\n\n"
                    f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                ),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

    text = (
        "💰 *Purchase a License*\n\n"
        "Choose your plan:\n\n"
        "💎 *Standard - $9.99/month*\n"
        "• 5 channels\n"
        "• Standard auto-post\n"
        "• Standard support\n\n"
        "👑 *Premium - $19.99/month*\n"
        "• 15 channels\n"
        "• Priority auto-post\n"
        "• Premium support\n\n"
        "🔥 *Lifetime - $49.99*\n"
        "• 50 channels (forever)\n"
        "• Lifetime auto-post\n"
        "• VIP support"
    )

    keyboard = [
        [InlineKeyboardButton("💎 Standard - $9.99/mo", callback_data='buy_plan_standard')],
        [InlineKeyboardButton("👑 Premium - $19.99/mo", callback_data='buy_plan_premium')],
        [InlineKeyboardButton("🔥 Lifetime - $49.99", callback_data='buy_plan_lifetime')],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_buy_plan(update: Update, context: ContextTypes.DEFAULT_TYPE, plan: str) -> None:
    """Handle plan selection - show payment options."""
    query = update.callback_query
    user = query.from_user

    prices = {
        'standard': '$9.99/month',
        'premium': '$19.99/month',
        'lifetime': '$49.99 (one-time)'
    }
    plan_emoji = {'standard': '💎', 'premium': '👑', 'lifetime': '🔥'}

    # Log plan selection
    db.log_user_action(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        action='plan_selected',
        plan_type=plan,
        details=f"Price: {prices.get(plan)}"
    )

    # Check for saved payment methods
    default_cred = db.get_default_payment_method(user.id)

    text = (
        f"{plan_emoji.get(plan, '🛒')} *{plan.title()} Plan*\n\n"
        f"💰 Price: *{prices.get(plan)}*\n\n"
        "💳 *Select Payment Method:*\n"
        "Click a button below to view payment details."
    )

    if default_cred:
        text += f"\n\n⭐ *Your default: {default_cred.payment_method.upper()}*"

    keyboard = [
        [InlineKeyboardButton("₿ Bitcoin (BTC)", callback_data=f'pay_btc_{plan}')],
        [InlineKeyboardButton("Ξ Ethereum (ETH)", callback_data=f'pay_eth_{plan}')],
        [InlineKeyboardButton("💵 USDT (TRC-20)", callback_data=f'pay_usdt_{plan}')],
        [InlineKeyboardButton("💳 PayPal / Card", callback_data=f'pay_paypal_{plan}')],
        [InlineKeyboardButton("🔙 Back to Plans", callback_data='buy_license')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    """Handle payment method selection during purchase."""
    query = update.callback_query
    user = query.from_user

    # Parse payment data: pay_btc_standard, pay_eth_premium, etc.
    parts = data.split('_')
    method = parts[1]  # btc, eth, usdt, paypal
    plan = parts[2]    # standard, premium, lifetime

    prices = {
        'standard': '$9.99',
        'premium': '$19.99',
        'lifetime': '$49.99'
    }

    # Log payment method selection
    db.log_user_action(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        action='payment_method_selected',
        plan_type=plan,
        payment_method=method,
        details=f"Price: {prices.get(plan)}"
    )

    # Show payment instructions based on method
    if method == 'btc':
        text = (
            f"₿ *Bitcoin Payment*\n\n"
            f"Plan: *{plan.title()}*\n"
            f"Amount: *{prices.get(plan)}*\n\n"
            f"📤 *Send BTC to:*\n"
            f"`bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh`\n\n"
            f"⚠️ *Important:*\n"
            f"1. Send exact amount or slightly more\n"
            f"2. Take screenshot of payment\n"
            f"3. Send screenshot here with your TXID\n"
            f"4. License key sent within 10-30 min\n\n"
            f"💾 *Save your BTC address for faster checkout next time?*\n"
            f"Reply with your BTC wallet address (for refunds/verification) "
            f"or send 'skip' to continue without saving."
        )
    elif method == 'eth':
        text = (
            f"Ξ *Ethereum Payment*\n\n"
            f"Plan: *{plan.title()}*\n"
            f"Amount: *{prices.get(plan)}*\n\n"
            f"📤 *Send ETH to:*\n"
            f"`{ETH_PAYMENT_ADDRESS}`\n\n"
            f"⚠️ *Important:*\n"
            f"1. Send exact amount or slightly more\n"
            f"2. Take screenshot of payment\n"
            f"3. Send screenshot here with your TXID\n"
            f"4. License key sent within 10-30 min\n\n"
            f"💾 *Save your ETH address for faster checkout next time?*\n"
            f"Reply with your ETH wallet address (for refunds/verification) "
            f"or send 'skip' to continue without saving."
        )
    elif method == 'usdt':
        text = (
            f"💵 *USDT (TRC-20) Payment*\n\n"
            f"Plan: *{plan.title()}*\n"
            f"Amount: *{prices.get(plan)}*\n\n"
            f"📤 *Send USDT to:*\n"
            f"`TY7YdA6BqV9k8mM5pN3qR4sT6uV8wX9yZ2`\n\n"
            f"⚠️ *Important:*\n"
            f"1. Send on TRC-20 network only!\n"
            f"2. Take screenshot of payment\n"
            f"3. Send screenshot here with your TXID\n"
            f"4. License key sent within 10-30 min\n\n"
            f"💾 *Save your USDT address for faster checkout next time?*\n"
            f"Reply with your USDT wallet address (for refunds/verification) "
            f"or send 'skip' to continue without saving."
        )
    elif method == 'paypal':
        text = (
            f"💳 *PayPal / Card Payment*\n\n"
            f"Plan: *{plan.title()}*\n"
            f"Amount: *{prices.get(plan)}*\n\n"
            f"📧 *PayPal to:*\n"
            f"`payments@profileshare.bot`\n\n"
            f"🔗 *Or use PayPal link:*\n"
            f"[Click to Pay](https://paypal.me/profileshare)\n\n"
            f"⚠️ *Important:*\n"
            f"1. Select 'Goods & Services'\n"
            f"2. Add note: 'ProfileShare {plan}'\n"
            f"3. Take screenshot of payment\n"
            f"4. Send screenshot here\n"
            f"5. License key sent within 10-30 min\n\n"
            f"💾 *Save your PayPal email for faster checkout next time?*\n"
            f"Reply with your PayPal email or send 'skip' to continue without saving."
        )

    # Store current payment context for the conversation
    context.user_data['current_payment'] = {
        'method': method,
        'plan': plan,
        'price': prices.get(plan)
    }

    keyboard = [
        [InlineKeyboardButton("✅ I've Paid - Send Screenshot", callback_data=f'paid_{method}_{plan}')],
        [InlineKeyboardButton("🔙 Back", callback_data=f'buy_plan_{plan}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== MESSAGE FORWARDING ====================

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward user messages to admin and handle payment credential saving."""
    user = update.effective_user
    message = update.message

    logger.info(f"Message from {user.id} ({user.username or 'N/A'}): {message.text[:50]}...")

    if not message.text:
        await message.reply_text("❌ Please send text messages only.")
        return

    text = message.text.strip()

    # Check if user is providing payment credentials (in response to payment method selection)
    current_payment = context.user_data.get('current_payment')
    if current_payment and text.lower() != 'skip':
        # Try to save the payment credential
        method = current_payment.get('method')
        saved = False

        # Validate and save based on method
        if method in ['btc', 'eth', 'usdt']:
            # Validate crypto address (basic check for length)
            if len(text) >= 26:  # Most crypto addresses are at least 26 chars
                db.save_payment_credential(
                    user_id=user.id,
                    payment_method=method,
                    username=user.username,
                    first_name=user.first_name,
                    **{f'{method}_address': text}
                )
                saved = True
                await message.reply_text(
                    f"✅ *{method.upper()} address saved!*\n\n"
                    f"Your wallet address has been saved for future purchases.\n"
                    f"You can manage your payment methods anytime with /paymentmethods",
                    parse_mode='Markdown'
                )
            else:
                await message.reply_text(
                    "⚠️ That doesn't look like a valid wallet address.\n"
                    "Please provide a valid address or reply 'skip' to continue without saving."
                )
                return

        elif method == 'paypal':
            # Basic email validation
            if '@' in text and '.' in text:
                db.save_payment_credential(
                    user_id=user.id,
                    payment_method='paypal',
                    username=user.username,
                    first_name=user.first_name,
                    paypal_email=text
                )
                saved = True
                await message.reply_text(
                    f"✅ *PayPal email saved!*\n\n"
                    f"Your PayPal email has been saved for future purchases.\n"
                    f"You can manage your payment methods anytime with /paymentmethods",
                    parse_mode='Markdown'
                )
            else:
                await message.reply_text(
                    "⚠️ That doesn't look like a valid email.\n"
                    "Please provide a valid PayPal email or reply 'skip' to continue without saving."
                )
                return

        # Clear the current payment context after processing
        if saved or text.lower() == 'skip':
            context.user_data.pop('current_payment', None)
            if text.lower() == 'skip':
                await message.reply_text(
                    "👍 No problem! You can always save payment methods later with /paymentmethods\n\n"
                    "Send your payment screenshot whenever you're ready!"
                )

    # Format the forwarded message to admin
    forward_text = (
        f"📩 *New Support Message*\n\n"
        f"From: {user.first_name} (@{user.username or 'N/A'})\n"
        f"User ID: `{user.id}`\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Message:\n{message.text}"
    )

    # Forward to admin
    try:
        if ADMIN_ID == 0:
            logger.error("ADMIN_ID is not set! Cannot forward message.")
            await message.reply_text(
                "❌ Sorry, message forwarding is not configured properly.\n"
                "Please contact admin directly."
            )
            return

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=forward_text,
            parse_mode='Markdown'
        )
        logger.info(f"Message forwarded to admin {ADMIN_ID}")

        # Confirm to user
        await message.reply_text(
            "✅ *Message sent to support!*\n\n"
            "An admin will respond to you shortly.\n"
            "Please allow up to 24 hours for a response.\n\n"
            "In the meantime, you can use /start to see other options.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to forward message to admin {ADMIN_ID}: {e}")
        await message.reply_text(
            "❌ Sorry, I couldn't send your message.\n"
            "Please try again later or contact admin directly."
        )


# ==================== ADMIN REPLY ====================

async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allow admin to reply to users."""
    user = update.effective_user

    logger.info(f"Admin reply attempt from {user.id} (expected admin: {ADMIN_ID})")

    # Check if sender is admin
    if user.id != ADMIN_ID:
        logger.warning(f"Unauthorized /reply attempt from {user.id}")
        await update.message.reply_text("❌ This command is for admins only.")
        return

    # Check if this is a reply to a forwarded message
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "❌ To reply to a user:\n"
            "1. Reply to their forwarded message\n"
            "2. Type: `/reply your message here`"
        )
        return

    # Extract user ID from the forwarded message
    try:
        original_text = update.message.reply_to_message.text
        logger.info(f"Original message text: {original_text[:100]}...")

        # Find user ID in the forwarded message
        user_id_match = re.search(r'User ID: `(\d+)`', original_text)

        if not user_id_match:
            await update.message.reply_text(
                "❌ Could not find user ID in the forwarded message.\n"
                "Make sure you're replying to a support message."
            )
            return

        target_user_id = int(user_id_match.group(1))
        logger.info(f"Extracted target user ID: {target_user_id}")

        # Get the reply text (remove /reply command)
        reply_text = update.message.text.replace('/reply', '').strip()
        if not reply_text:
            await update.message.reply_text(
                "❌ Please provide a message to send.\n"
                "Usage: `/reply your message here`"
            )
            return

        # Send reply to user
        full_reply = (
            "📨 *Reply from Support*\n\n"
            f"{reply_text}\n\n"
            "_Reply to this chat if you need more help._"
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=full_reply,
            parse_mode='Markdown'
        )

        await update.message.reply_text(f"✅ Reply sent to user ({target_user_id})!")
        logger.info(f"Reply sent to user {target_user_id}")

    except Exception as e:
        logger.error(f"Failed to send reply: {e}")
        await update.message.reply_text(f"❌ Failed to send reply: {str(e)}")


# ==================== PROOF OF PAYMENT COMMAND ====================

async def proof_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Submit proof of payment command."""
    user = update.effective_user

    text = (
        "📸 *Submit Proof of Payment*\n\n"
        f"Send your payment screenshot here with the following details:\n\n"
        f"*Required:*\n"
        f"• Screenshot of payment\n"
        f"• TXID / Transaction Hash\n\n"
        f"*Optional but helpful:*\n"
        f"• Amount sent\n"
        f"• Which plan you bought\n"
        f"• Your sending wallet address\n\n"
        f"💡 *Tip:* You can also send a message like:\n"
        f"`/proof TXID: 0x123... Amount: 0.05 ETH Plan: Premium`\n\n"
        f"_All proofs are reviewed within 10-30 minutes._"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_proof_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment proof submission via message."""
    user = update.effective_user
    message = update.message

    # Check if message has a photo (screenshot)
    has_photo = message.photo and len(message.photo) > 0
    has_text = message.text and len(message.text.strip()) > 0

    if not has_photo and not has_text:
        await message.reply_text(
            "❌ Please send either:\n"
            "• A screenshot of your payment, OR\n"
            "• A message with your TXID and details\n\n"
            "Use /proof for more info."
        )
        return

    # Extract TXID and details from text
    txid = None
    amount = None
    plan = None
    from_address = None
    payment_method = 'eth'  # Default to ETH since the user specified ETH address

    text = message.text or message.caption or ""
    text_upper = text.upper()

    # Try to extract TXID (0x followed by hex, or various TXID patterns)
    import re
    txid_match = re.search(r'(0x[a-fA-F0-9]{64})', text)
    if txid_match:
        txid = txid_match.group(1)
    else:
        # Look for any TXID mention
        txid_patterns = [
            r'TXID[:\s]+([a-zA-Z0-9]+)',
            r'TRANSACTION[:\s]+([a-zA-Z0-9]+)',
            r'HASH[:\s]+([a-zA-Z0-9]+)',
            r'ID[:\s]+([a-zA-Z0-9]+)'
        ]
        for pattern in txid_patterns:
            match = re.search(pattern, text_upper)
            if match:
                txid = match.group(1)
                break

    # Extract amount
    amount_match = re.search(r'(\d+\.?\d*)\s*(BTC|ETH|USDT|USD|\$)', text_upper)
    if amount_match:
        amount = amount_match.group(0)

    # Extract plan
    for p in ['LIFETIME', 'PREMIUM', 'STANDARD']:
        if p in text_upper:
            plan = p.lower()
            break

    # Extract from address (if provided)
    addr_match = re.search(r'(FROM|WALLET|SENT FROM)[:\s]+(0x[a-fA-F0-9]{40,})', text_upper)
    if addr_match:
        from_address = addr_match.group(2)

    # Get photo file_id if present
    screenshot_file_id = None
    if has_photo:
        # Get the largest photo
        screenshot_file_id = message.photo[-1].file_id

    # Save proof to database
    proof_id = db.save_payment_proof(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        payment_method=payment_method,
        to_address=ETH_PAYMENT_ADDRESS,
        plan_type=plan,
        amount_sent=amount,
        transaction_id=txid,
        from_address=from_address,
        screenshot_path=screenshot_file_id,
        message_text=text
    )

    # Confirm to user
    confirm_text = (
        f"✅ *Proof Submitted!*\n\n"
        f"Proof ID: `#{proof_id}`\n"
    )
    if plan:
        confirm_text += f"Plan: {plan.title()}\n"
    if amount:
        confirm_text += f"Amount: {amount}\n"
    if txid:
        confirm_text += f"TXID: `{txid[:20]}...`\n"

    confirm_text += (
        f"\n📤 *Sent to ETH Address:*\n"
        f"`{ETH_PAYMENT_ADDRESS[:10]}...{ETH_PAYMENT_ADDRESS[-10:]}`\n\n"
        f"_Your payment will be verified within 10-30 minutes._\n"
        f"_You'll receive your license key once confirmed._"
    )

    await message.reply_text(confirm_text, parse_mode='Markdown')

    # Forward to admin
    if ADMIN_ID != 0:
        try:
            forward_text = (
                f"🆕 *New Payment Proof!*\n\n"
                f"Proof ID: `#{proof_id}`\n"
                f"From: {user.first_name} (@{user.username or 'N/A'})\n"
                f"User ID: `{user.id}`\n\n"
                f"💰 *Details:*\n"
                f"Plan: {plan or 'Not specified'}\n"
                f"Amount: {amount or 'Not specified'}\n"
                f"Method: ETH\n"
                f"TXID: `{txid or 'Not provided'}`\n\n"
                f"To Address:\n`{ETH_PAYMENT_ADDRESS}`\n\n"
                f"Message:\n{text[:200] if text else 'No message'}{'...' if text and len(text) > 200 else ''}\n\n"
                f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"Verify with: `/verify {proof_id}`\n"
                f"Reject with: `/reject {proof_id} [reason]`"
            )

            if screenshot_file_id:
                # Send photo with caption
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=screenshot_file_id,
                    caption=forward_text,
                    parse_mode='Markdown'
                )
            else:
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=forward_text,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Failed to forward proof to admin: {e}")


# ==================== ADMIN VERIFICATION COMMANDS ====================

async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to verify a payment proof."""
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/verify <proof_id> [notes]`\n\n"
            "Example: `/verify 123 Payment confirmed, key sent`"
        )
        return

    try:
        proof_id = int(context.args[0])
        notes = ' '.join(context.args[1:]) if len(context.args) > 1 else None
    except ValueError:
        await update.message.reply_text("❌ Proof ID must be a number.")
        return

    success = db.verify_payment_proof(proof_id, user.id, notes)

    if success:
        # Get proof details to notify user
        proof = db.get_payment_proof(proof_id)
        if proof:
            try:
                await context.bot.send_message(
                    chat_id=proof.user_id,
                    text=(
                        f"✅ *Payment Verified!*\n\n"
                        f"Your payment for {proof.plan_type or 'license'} has been confirmed.\n\n"
                        f"Proof ID: `#{proof_id}`\n\n"
                        f"_You should receive your license key shortly!_"
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify user of verification: {e}")

        await update.message.reply_text(f"✅ Proof #{proof_id} verified!")
    else:
        await update.message.reply_text(f"❌ Proof #{proof_id} not found.")


async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to reject a payment proof."""
    user = update.effective_user

    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Admin only.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/reject <proof_id> <reason>`\n\n"
            "Example: `/reject 123 TXID not found on blockchain`"
        )
        return

    try:
        proof_id = int(context.args[0])
        notes = ' '.join(context.args[1:]) if len(context.args) > 1 else None
    except ValueError:
        await update.message.reply_text("❌ Proof ID must be a number.")
        return

    success = db.reject_payment_proof(proof_id, user.id, notes)

    if success:
        # Notify user
        proof = db.get_payment_proof(proof_id)
        if proof:
            try:
                await context.bot.send_message(
                    chat_id=proof.user_id,
                    text=(
                        f"❌ *Payment Not Verified*\n\n"
                        f"Proof ID: `#{proof_id}`\n\n"
                        f"Reason: {notes or 'No reason provided'}\n\n"
                        f"Please contact support if you believe this is an error."
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to notify user of rejection: {e}")

        await update.message.reply_text(f"🚫 Proof #{proof_id} rejected.")
    else:
        await update.message.reply_text(f"❌ Proof #{proof_id} not found.")


# ==================== PAYMENT METHODS COMMAND ====================

async def paymentmethods_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's saved payment methods."""
    user = update.effective_user
    credentials = db.get_user_payment_credentials(user.id)

    if not credentials:
        text = (
            "📭 *No Saved Payment Methods*\n\n"
            "Save your payment methods for faster checkout!\n\n"
            "When you make a purchase, we'll ask if you want to save:\n"
            "• Your crypto wallet addresses (for refunds/verification)\n"
            "• Your PayPal email\n"
            "• Card last 4 digits (for reference)\n\n"
            "Start a purchase to save your first method:"
        )
        keyboard = [
            [InlineKeyboardButton("💰 Buy License", callback_data='buy_license')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
        ]
    else:
        text = "💳 *Your Saved Payment Methods*\n\n"
        default = db.get_default_payment_method(user.id)

        for i, cred in enumerate(credentials, 1):
            default_mark = " ⭐ DEFAULT" if cred.is_default else ""
            text += f"*{i}. {cred.payment_method.upper()}{default_mark}*\n"

            if cred.btc_address:
                text += f"   BTC: `{cred.btc_address[:10]}...{cred.btc_address[-10:]}`\n"
            if cred.eth_address:
                text += f"   ETH: `{cred.eth_address[:10]}...{cred.eth_address[-10:]}`\n"
            if cred.usdt_address:
                text += f"   USDT: `{cred.usdt_address[:10]}...{cred.usdt_address[-10:]}`\n"
            if cred.paypal_email:
                text += f"   PayPal: `{cred.paypal_email}`\n"
            if cred.card_last_four:
                text += f"   Card: **** {cred.card_last_four}\n"
            text += "\n"

        keyboard = [
            [InlineKeyboardButton("➕ Add Method", callback_data='add_payment_method')],
            [InlineKeyboardButton("⭐ Set Default", callback_data='set_default_method')],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# ==================== HELP COMMAND ====================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Help command."""
    text = (
        "🤖 *Support Bot Help*\n\n"
        "*Available Commands:*\n"
        "/start - Show main menu\n"
        "/paymentmethods - Manage your saved payment methods\n"
        "/proof - Submit proof of payment\n"
        "/help - Show this help\n\n"
        "*How to buy a license:*\n"
        "1. Click '💰 Buy License'\n"
        "2. Select your plan (Standard/Premium/Lifetime)\n"
        "3. Choose payment method (BTC/ETH/USDT/PayPal)\n"
        "4. Save your payment info (optional, for faster checkout)\n"
        "5. Send payment to the provided address\n"
        "6. Submit proof with /proof command\n"
        "7. Receive license key within 10-30 min\n\n"
        "*Submitting Proof of Payment:*\n"
        "• Send screenshot with TXID\n"
        "• Or use: /proof TXID: 0x... Amount: 0.05 ETH Plan: Premium\n"
        "• ETH payments go to:\n"
        f"`{ETH_PAYMENT_ADDRESS[:15]}...{ETH_PAYMENT_ADDRESS[-15:]}`\n\n"
        "*Saved Payment Methods:*\n"
        "• Store your crypto addresses for refunds\n"
        "• Save PayPal email for faster checkout\n"
        "• Set a default payment method\n"
        "Manage with: /paymentmethods\n\n"
        "*For admins:*\n"
        "Reply to forwarded messages with:\n"
        "`/reply your message here`\n"
        "Verify payment: `/verify <proof_id>`\n"
        "Reject payment: `/reject <proof_id> <reason>`"
    )

    await update.message.reply_text(text, parse_mode='Markdown')


# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again or contact us later."
        )


# ==================== MAIN ====================

def main() -> None:
    """Start the support bot."""
    token = os.getenv("SUPPORT_BOT_TOKEN")
    if not token:
        logger.error("SUPPORT_BOT_TOKEN not found in .env!")
        return

    logger.info(f"Starting Support Bot with admin ID: {ADMIN_ID}")
    logger.info(f"Support bot handle: @{SUPPORT_BOT_HANDLE}")

    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reply", admin_reply))
    application.add_handler(CommandHandler("paymentmethods", paymentmethods_command))
    application.add_handler(CommandHandler("proof", proof_command))
    application.add_handler(CommandHandler("verify", verify_command))
    application.add_handler(CommandHandler("reject", reject_command))

    # Callback handler - handle set_default callbacks separately first
    application.add_handler(CallbackQueryHandler(handle_set_default_callback, pattern='^set_default_'))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Message handlers
    # Check for payment proof submissions first (photos or text with TXID)
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.TEXT) & filters.Regex(r'(TXID|TRANSACTION|0x|PAID|PAYMENT)'),
        handle_proof_submission
    ))
    # Regular text messages go to admin
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))

    # Error handler
    application.add_error_handler(error_handler)

    logger.info("Support Bot started!")
    application.run_polling()


if __name__ == '__main__':
    main()
