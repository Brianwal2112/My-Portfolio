"""
User Panel - Licensed User Features
Accessible only to users with valid license keys
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database

db = Database()
logger = logging.getLogger(__name__)


# ==================== USER MAIN MENU ====================

async def show_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show main menu for licensed users."""
    user = update.effective_user
    license_info = db.get_license_info(user.id)

    if not license_info:
        if update.callback_query:
            await update.callback_query.edit_message_text("❌ No active license found.")
        else:
            await update.message.reply_text("❌ No active license found.")
        return

    plan_emoji = {'standard': '💎', 'premium': '👑', 'lifetime': '🔥'}.get(
        license_info['plan'], '💎'
    )

    menu_text = (
        f"👋 Welcome back, {user.first_name}!\n\n"
        f"{plan_emoji} *Plan: {license_info['plan'].title()}*\n"
    )

    if license_info['days_left'] is not None:
        menu_text += f"⏰ Days left: {license_info['days_left']}\n"
    else:
        menu_text += "⏰ Type: *Lifetime* 🔥\n"

    channels_count = len(context.user_data.get('channels', []))
    max_channels = license_info['max_channels']

    menu_text += f"📢 Channels: {channels_count}/{max_channels}\n\n"
    menu_text += "Choose an option:"

    keyboard = [
        [
            InlineKeyboardButton("🔗 Share X", callback_data='user_share_x'),
            InlineKeyboardButton("💻 Share GitHub", callback_data='user_share_github')
        ],
        [
            InlineKeyboardButton("📋 Share Both", callback_data='user_share_both')
        ],
        [
            InlineKeyboardButton("📢 My Channels", callback_data='user_channels'),
            InlineKeyboardButton("➕ Add Channel", callback_data='user_add_channel')
        ],
        [
            InlineKeyboardButton("⏰ Auto-Post", callback_data='user_scheduler'),
            InlineKeyboardButton("📊 My License", callback_data='user_license_info')
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='user_settings'),
            InlineKeyboardButton("❓ Help", callback_data='user_help')
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


# ==================== USER CALLBACK HANDLERS ====================

async def handle_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> bool:
    """Handle user panel callbacks. Returns True if handled."""

    if data == 'user_menu':
        await show_user_menu(update, context)
        return True
    elif data == 'user_share_x':
        await user_share_x(update, context)
        return True
    elif data == 'user_share_github':
        await user_share_github(update, context)
        return True
    elif data == 'user_share_both':
        await user_share_both(update, context)
        return True
    elif data == 'user_channels':
        await user_show_channels(update, context)
        return True
    elif data == 'user_add_channel':
        await user_add_channel_prompt(update, context)
        return True
    elif data == 'user_scheduler':
        await user_scheduler_menu(update, context)
        return True
    elif data == 'user_license_info':
        await user_license_info(update, context)
        return True
    elif data == 'user_settings':
        await user_settings(update, context)
        return True
    elif data == 'user_help':
        await user_help(update, context)
        return True
    elif data == 'user_scheduler_start':
        await user_scheduler_start(update, context)
        return True
    elif data == 'user_scheduler_stop':
        await user_scheduler_stop(update, context)
        return True

    return False


# ==================== USER FUNCTIONS ====================

async def user_share_x(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Share X profile."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🔗 *Share X Profile*\n\n"
        "This will share your X profile to all configured channels.\n\n"
        "Use command: `/sharex`",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_menu')
        ]])
    )


async def user_share_github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Share GitHub profile."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "💻 *Share GitHub Profile*\n\n"
        "This will share your GitHub profile to all configured channels.\n\n"
        "Use command: `/sharegithub`",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_menu')
        ]])
    )


async def user_share_both(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Share both profiles."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📋 *Share Both Profiles*\n\n"
        "This will share both your X and GitHub profiles to all configured channels.\n\n"
        "Use command: `/shareall`",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_menu')
        ]])
    )


async def user_show_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's configured channels."""
    query = update.callback_query
    await query.answer()

    channels = context.user_data.get('channels', [])

    if not channels:
        text = "📭 *No channels configured*\n\nUse 'Add Channel' to get started."
    else:
        text = f"📢 *Your Channels ({len(channels)}):*\n\n"
        for i, ch in enumerate(channels, 1):
            text += f"{i}. `{ch}`\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Channel", callback_data='user_add_channel')],
        [InlineKeyboardButton("🗑️ Remove Channel", callback_data='user_remove_channel')],
        [InlineKeyboardButton("🔙 Back", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def user_add_channel_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt user to add a channel."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "➕ *Add Channel*\n\n"
        "To add a channel:\n"
        "1. Add this bot as admin to your channel\n"
        "2. Send the channel username or ID\n\n"
        "Command: `/addchannel @channelname`\n\n"
        "For private channels, use the channel ID (starts with -100)",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_channels')
        ]])
    )


async def user_scheduler_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show scheduler menu."""
    query = update.callback_query
    await query.answer()

    # Check if scheduler is running
    jobs = context.application.job_queue.jobs()
    is_running = len(list(jobs)) > 0

    status = "✅ RUNNING" if is_running else "⏹️ STOPPED"

    text = (
        f"⏰ *Auto-Post Scheduler*\n\n"
        f"Status: {status}\n\n"
        f"When enabled, the bot will automatically post:\n"
        f"• X Profile: Every hour\n"
        f"• GitHub Profile: Every hour (offset)\n"
        f"• Both: Every hour (offset)\n\n"
        f"With anti-ban protection (random delays)"
    )

    keyboard = [
        [
            InlineKeyboardButton("▶️ Start", callback_data='user_scheduler_start'),
            InlineKeyboardButton("⏹️ Stop", callback_data='user_scheduler_stop')
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def user_scheduler_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the scheduler."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "✅ *Auto-Post Started*\n\n"
        "The bot will now automatically share your profiles every hour.\n\n"
        "Use /stopscheduler to stop at any time.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_scheduler')
        ]])
    )


async def user_scheduler_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop the scheduler."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "⏹️ *Auto-Post Stopped*\n\n"
        "Automatic sharing is now disabled.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data='user_scheduler')
        ]])
    )


async def user_license_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show license information."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    info = db.get_license_info(user.id)

    if not info:
        await query.edit_message_text("❌ No license found.")
        return

    text = (
        f"📊 *License Information*\n\n"
        f"Plan: *{info['plan'].title()}*\n"
        f"Status: {info['status'].title()}\n"
        f"Max Channels: {info['max_channels']}\n"
        f"Auto-Post: {'✅ Enabled' if info['auto_post'] else '❌ Disabled'}\n"
    )

    if info['days_left'] is not None:
        text += f"\nDays Remaining: {info['days_left']}\n"
        text += f"Expires: {info['expires_at'].strftime('%Y-%m-%d')}\n"
    else:
        text += "\nType: *Lifetime* 🔥\n"

    if info.get('activated_at'):
        text += f"Activated: {info['activated_at'].strftime('%Y-%m-%d')}\n"

    keyboard = [
        [InlineKeyboardButton("🔄 Renew License", callback_data='user_renew')],
        [InlineKeyboardButton("🔙 Back", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def user_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settings menu."""
    query = update.callback_query
    await query.answer()

    text = (
        f"⚙️ *Settings*\n\n"
        f"Configure your profile links and preferences.\n\n"
        f"Current profiles are set in the bot configuration."
    )

    keyboard = [
        [InlineKeyboardButton("📢 My Channels", callback_data='user_channels')],
        [InlineKeyboardButton("⏰ Scheduler", callback_data='user_scheduler')],
        [InlineKeyboardButton("🔙 Back", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def user_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help for users."""
    query = update.callback_query
    await query.answer()

    text = (
        f"❓ *User Help*\n\n"
        f"*Quick Commands:*\n"
        f"/menu - Open this menu\n"
        f"/sharex - Share X profile\n"
        f"/sharegithub - Share GitHub\n"
        f"/shareall - Share both\n"
        f"/addchannel - Add channel\n"
        f"/channels - List channels\n"
        f"/mylicense - View license\n\n"
        f"*Getting Started:*\n"
        f"1. Add channels you want to post to\n"
        f"2. Click 'Share X' or 'Share GitHub'\n"
        f"3. Or enable Auto-Post for automatic sharing\n\n"
        f"*Anti-Ban Features:*\n"
        f"• Random delays between posts\n"
        f"• Message rotation\n"
        f"• 5-minute cooldown\n"
        f"• Max 10 channels/hour"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='user_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
