"""
Admin Panel - License Management System
Manages the User Bot (8028150882...)
Accessible only to administrators
"""

import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()
logger = logging.getLogger(__name__)
SUPPORT_BOT = os.getenv("SUPPORT_BOT_USERNAME", "uppport_bot")
ADMIN_BOT_NAME = "cryptic01_bot"


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    admin_ids = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
    return user_id in admin_ids


# ==================== ADMIN MAIN MENU ====================

async def show_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel menu."""
    user = update.effective_user

    if not is_admin(user.id):
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ Access denied. Admin only.")
        else:
            await update.message.reply_text("❌ Access denied. Admin only.")
        return

    # Get statistics
    stats = {
        'total_licenses': len(db.get_all_licenses()),
        'active': len(db.get_all_licenses('active')),
        'inactive': len(db.get_all_licenses('inactive')),
        'expired': len(db.get_all_licenses('expired')),
        'revoked': len(db.get_all_licenses('revoked'))
    }

    # Escape underscores in usernames for Markdown
    admin_bot_escaped = ADMIN_BOT_NAME.replace('_', '\\_')

    menu_text = (
        f"🔐 *Admin Panel*\n"
        f"@{admin_bot_escaped}\n\n"
        f"👤 Admin: {user.first_name}\n"
        f"🤖 User Bot: @ven\\_userbot\n"
        f"📞 Support: @uppport\\_bot\n\n"
        f"📊 *License Statistics*\n"
        f"Total: {stats['total_licenses']}\n"
        f"✅ Active: {stats['active']}\n"
        f"⏹️ Inactive: {stats['inactive']}\n"
        f"⌛ Expired: {stats['expired']}\n"
        f"🚫 Revoked: {stats['revoked']}\n\n"
        f"Select an action:"
    )

    keyboard = [
        [
            InlineKeyboardButton("➕ Generate Key", callback_data='admin_generate'),
            InlineKeyboardButton("📋 List Keys", callback_data='admin_list_keys')
        ],
        [
            InlineKeyboardButton("🔍 Verify Payment", callback_data='admin_verify_payment'),
            InlineKeyboardButton("📊 Stats", callback_data='admin_stats')
        ],
        [
            InlineKeyboardButton("🚫 Revoke Key", callback_data='admin_revoke'),
            InlineKeyboardButton("👤 User Lookup", callback_data='admin_user_lookup')
        ],
        [
            InlineKeyboardButton("💰 Pricing", callback_data='admin_pricing'),
            InlineKeyboardButton("⚙️ Settings", callback_data='admin_settings')
        ],
        [InlineKeyboardButton("🔙 Back to Bot", callback_data='back_to_main')]
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


# ==================== ADMIN CALLBACK HANDLERS ====================

async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    """Handle admin panel callbacks. Returns True if handled."""

    if not is_admin(update.callback_query.from_user.id):
        await update.callback_query.answer("❌ Admin only!", show_alert=True)
        return True

    if data == 'admin_menu':
        await show_admin_menu(update, context)
        return True
    elif data == 'admin_generate':
        await admin_generate_prompt(update, context)
        return True
    elif data == 'admin_list_keys':
        await admin_list_keys(update, context)
        return True
    elif data == 'admin_verify_payment':
        await admin_verify_payment_prompt(update, context)
        return True
    elif data == 'admin_stats':
        await admin_stats(update, context)
        return True
    elif data == 'admin_revoke':
        await admin_revoke_prompt(update, context)
        return True
    elif data == 'admin_user_lookup':
        await admin_user_lookup_prompt(update, context)
        return True
    elif data == 'admin_pricing':
        await admin_pricing(update, context)
        return True
    elif data == 'admin_settings':
        await admin_settings(update, context)
        return True

    return False


# ==================== ADMIN FUNCTIONS ====================

async def admin_generate_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt to generate a license key."""
    query = update.callback_query
    await query.answer()

    text = (
        f"➕ *Generate License Key*\n\n"
        f"Command format:\n"
        f"`/generate <plan> <days> [activations]`\n\n"
        f"*Plans:*\n"
        f"• `standard` - 5 channels ($9.99)\n"
        f"• `premium` - 15 channels ($19.99)\n"
        f"• `lifetime` - 50 channels ($49.99)\n\n"
        f"*Examples:*\n"
        f"`/generate standard 30` - 30 days\n"
        f"`/generate premium 90` - 90 days\n"
        f"`/generate lifetime 0` - Lifetime\n"
        f"`/generate standard 30 3` - 3 activations"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List recent license keys."""
    query = update.callback_query
    await query.answer()

    licenses = db.get_all_licenses()[-10:]  # Last 10

    if not licenses:
        text = "📭 No licenses found."
    else:
        text = f"📋 *Recent Licenses (Last 10)*\n\n"
        for lic in licenses:
            status_emoji = {
                'active': '✅',
                'inactive': '⏹️',
                'expired': '⌛',
                'revoked': '🚫'
            }.get(lic.status, '⏹️')

            text += f"{status_emoji} `{lic.license_key[:12]}****`\n"
            text += f"   Plan: {lic.plan_type} | Status: {lic.status}\n"
            if lic.user_id:
                text += f"   User: {lic.username or lic.user_id}\n"
            text += "\n"

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_list_keys')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_verify_payment_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt to verify a payment."""
    query = update.callback_query
    await query.answer()

    text = (
        f"🔍 *Verify Payment*\n\n"
        f"To verify a payment and generate key:\n\n"
        f"1. Check your payment method (Crypto/PayPal)\n"
        f"2. Confirm payment received\n"
        f"3. Generate key with `/generate`\n"
        f"4. Send key to customer\n\n"
        f"*Support Bot:* @uppport_bot\n"
        f"_Customers contact here for purchases_\n\n"
        f"*Pending payments will appear here (feature coming)*"
    )

    keyboard = [
        [InlineKeyboardButton("➕ Generate Key", callback_data='admin_generate')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed statistics."""
    query = update.callback_query
    await query.answer()

    # Calculate revenue (mock - would need actual payment data)
    active_licenses = db.get_all_licenses('active')
    standard_count = sum(1 for l in active_licenses if l.plan_type == 'standard')
    premium_count = sum(1 for l in active_licenses if l.plan_type == 'premium')
    lifetime_count = sum(1 for l in active_licenses if l.plan_type == 'lifetime')

    estimated_revenue = (
        standard_count * 9.99 +
        premium_count * 19.99 +
        lifetime_count * 49.99
    )

    text = (
        f"📊 *Detailed Statistics*\n\n"
        f"*Active Licenses by Plan:*\n"
        f"💎 Standard: {standard_count}\n"
        f"👑 Premium: {premium_count}\n"
        f"🔥 Lifetime: {lifetime_count}\n\n"
        f"💰 *Estimated Revenue:* ${estimated_revenue:.2f}\n\n"
        f"*Total Licenses:* {len(db.get_all_licenses())}\n"
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Refresh", callback_data='admin_stats')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_revoke_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt to revoke a license."""
    query = update.callback_query
    await query.answer()

    text = (
        f"🚫 *Revoke License*\n\n"
        f"To revoke a license key:\n"
        f"`/revoke <key>`\n\n"
        f"This will immediately deactivate the license\n"
        f"and prevent further use.\n\n"
        f"⚠️ *Warning:* This action cannot be undone!"
    )

    keyboard = [
        [InlineKeyboardButton("📋 List Keys", callback_data='admin_list_keys')],
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_user_lookup_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt to look up a user."""
    query = update.callback_query
    await query.answer()

    text = (
        f"👤 *User Lookup*\n\n"
        f"Search for a user by:\n"
        f"• Telegram ID\n"
        f"• Username\n"
        f"• License Key\n\n"
        f"Command: `/lookup <user_id or @username>`\n\n"
        f"Shows user's license status, channels, and activity."
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_pricing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show/edit pricing."""
    query = update.callback_query
    await query.answer()

    text = (
        f"💰 *Current Pricing*\n\n"
        f"💎 *Standard*: $9.99/month\n"
        f"   • 5 channels\n"
        f"   • Basic auto-post\n"
        f"   • Standard support\n\n"
        f"👑 *Premium*: $19.99/month\n"
        f"   • 15 channels\n"
        f"   • Priority auto-post\n"
        f"   • Premium support\n\n"
        f"🔥 *Lifetime*: $49.99 one-time\n"
        f"   • 50 channels\n"
        f"   • Lifetime auto-post\n"
        f"   • VIP support\n\n"
        f"To change pricing, edit the bot configuration."
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin settings."""
    query = update.callback_query
    await query.answer()

    text = (
        f"⚙️ *Admin Settings*\n\n"
        f"*Payment Methods:*\n"
        f"Configure in .env file:\n"
        f"• Crypto wallet address\n"
        f"• PayPal email\n"
        f"• Other payment methods\n\n"
        f"*Anti-Ban Settings:*\n"
        f"• Min delay: 3 seconds\n"
        f"• Max delay: 8 seconds\n"
        f"• Cooldown: 5 minutes\n"
        f"• Max channels/hour: 10\n\n"
        f"*Support Bot:* @uppport_bot\n"
        f"_Users contact here for purchases_"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
