import os
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Profile links from environment variables
X_PROFILE_LINK = os.getenv("X_PROFILE_LINK", "https://x.com/your_username")
GITHUB_PROFILE_LINK = os.getenv("GITHUB_PROFILE_LINK", "https://github.com/your_username")

# Parse target channels and admin IDs
TARGET_CHANNELS = [ch.strip() for ch in os.getenv("TARGET_CHANNELS", "").split(",") if ch.strip()]
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Anti-ban settings
MIN_DELAY = 3  # Minimum seconds between messages
MAX_DELAY = 8  # Maximum seconds between messages
MAX_CHANNELS_PER_HOUR = 10  # Limit channels to avoid spam detection
COOLDOWN_MINUTES = 5  # Cooldown between manual shares

# Track last share time for cooldown
last_share_time = None


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS or len(ADMIN_IDS) == 0


def check_cooldown() -> tuple[bool, str]:
    """Check if enough time has passed since last share."""
    global last_share_time
    if last_share_time is None:
        return True, ""

    elapsed = datetime.now() - last_share_time
    if elapsed < timedelta(minutes=COOLDOWN_MINUTES):
        remaining = COOLDOWN_MINUTES - int(elapsed.total_seconds() / 60)
        return False, f"⏳ Please wait {remaining} minutes before sharing again."
    return True, ""


def update_share_time():
    """Update the last share timestamp."""
    global last_share_time
    last_share_time = datetime.now()


async def random_delay():
    """Add random delay to simulate human behavior."""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    await asyncio.sleep(delay)


async def safe_send_message(bot, chat_id: str, text: str, parse_mode: str = None) -> bool:
    """Send message with anti-ban safety measures."""
    try:
        # Random delay before sending
        await random_delay()

        # Send with typing action (human-like)
        await bot.send_chat_action(chat_id=chat_id, action='typing')
        await asyncio.sleep(random.uniform(1, 2))

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=False
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send to {chat_id}: {e}")
        return False


# Messages for auto-posting with rotation
X_MESSAGES = [
    "🐦 Check out my X profile!\n\n{link}\n\nFollow for tech updates, insights, and more! 👆\n\n#X #Twitter #Tech #Follow",
    "🚀 Let's connect on X!\n\n{link}\n\nI share coding tips, projects, and tech news! 💻\n\n#X #Developer #Code",
    "📱 Follow me on X\n\n{link}\n\nJoin the conversation! 🗣️\n\n#X #SocialMedia #Tech",
    "💡 Looking for dev content?\n\nFollow me on X: {link}\n\n#Developer #Programming #X",
]

GITHUB_MESSAGES = [
    "💻 Check out my GitHub!\n\n{link}\n\nStar my repos and let's build something together! ⭐\n\n#GitHub #OpenSource #Code",
    "🚀 Explore my projects on GitHub\n\n{link}\n\nContributions welcome! 🤝\n\n#GitHub #Developer #Programming",
    "📂 My code lives here:\n\n{link}\n\nFeel free to fork and collaborate! 🍴\n\n#GitHub #DevLife #Code",
    "🔧 Open source projects:\n\n{link}\n\nCheck them out and show some love! ❤️\n\n#OpenSource #GitHub #Dev",
]

COMBINED_MESSAGES = [
    "🔗 Connect with me!\n\n🐦 X: {x_link}\n💻 GitHub: {github_link}\n\nLet's grow together! 🚀\n\n#X #GitHub #Follow #Developer",
    "📱 Follow my journey!\n\nX: {x_link}\nGitHub: {github_link}\n\nTech, code, and more! 💡\n\n#Tech #Code #Developer",
    "🚀 Let's link up!\n\n🐦 X: {x_link}\n💻 GitHub: {github_link}\n\nFollow for content! 📈\n\n#Follow #X #GitHub",
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("🔗 X Profile", callback_data='x_profile'),
            InlineKeyboardButton("💻 GitHub", callback_data='github_profile')
        ],
        [
            InlineKeyboardButton("📋 Both Profiles", callback_data='both_profiles')
        ]
    ]

    # Add admin menu button if user is admin
    if is_admin(user.id):
        keyboard.append([InlineKeyboardButton("⚙️ Admin Menu", callback_data='admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f'Hi {user.first_name}! 👋\n\n'
        'I share profile links for X and GitHub.\n\n'
        'Choose an option:'
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin submenu."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("📤 Share X", callback_data='admin_share_x'),
            InlineKeyboardButton("📤 Share GitHub", callback_data='admin_share_github')
        ],
        [
            InlineKeyboardButton("📤 Share Both", callback_data='admin_share_all')
        ],
        [
            InlineKeyboardButton("📢 Channels", callback_data='admin_channels'),
            InlineKeyboardButton("⏰ Scheduler", callback_data='admin_scheduler')
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "⚙️ *Admin Menu*\n\nSelect an action:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def channels_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show channels submenu."""
    query = update.callback_query
    await query.answer()

    channels_text = "📢 *Configured Channels*\n\n"
    if TARGET_CHANNELS:
        channels_text += "\n".join([f"• `{ch}`" for ch in TARGET_CHANNELS])
    else:
        channels_text += "No channels configured yet."

    keyboard = [
        [InlineKeyboardButton("➕ Add Channel", callback_data='admin_add_channel')],
        [InlineKeyboardButton("🔄 Refresh List", callback_data='admin_channels')],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        channels_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def scheduler_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show scheduler submenu."""
    query = update.callback_query
    await query.answer()

    # Check scheduler status
    jobs = context.application.job_queue.jobs()
    is_running = len(list(jobs)) > 0

    status = "✅ RUNNING" if is_running else "⏹️ STOPPED"

    keyboard = [
        [
            InlineKeyboardButton("▶️ Start", callback_data='scheduler_start'),
            InlineKeyboardButton("⏹️ Stop", callback_data='scheduler_stop')
        ],
        [InlineKeyboardButton("🔄 Check Status", callback_data='admin_scheduler')],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data='admin_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"⏰ *Scheduler Status: {status}*\n\n"
        f"Auto-posts every hour to {len(TARGET_CHANNELS)} channel(s).\n\n"
        f"Schedule:\n"
        f"• X Profile: Every hour\n"
        f"• GitHub: 20 min past\n"
        f"• Both: 40 min past",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    # Admin menu actions
    if query.data == 'admin_menu':
        await admin_menu(update, context)
        return
    elif query.data == 'admin_channels':
        await channels_menu(update, context)
        return
    elif query.data == 'admin_scheduler':
        await scheduler_menu(update, context)
        return
    elif query.data == 'back_to_main':
        await start(update, context)
        return

    # Admin share actions
    if query.data == 'admin_share_x':
        await query.edit_message_text("📤 Sharing X profile...")
        await share_x_to_channels(update, context, from_button=True)
        return
    elif query.data == 'admin_share_github':
        await query.edit_message_text("📤 Sharing GitHub profile...")
        await share_github_to_channels(update, context, from_button=True)
        return
    elif query.data == 'admin_share_all':
        await query.edit_message_text("📤 Sharing both profiles...")
        await share_all_to_channels(update, context, from_button=True)
        return

    # Scheduler actions
    if query.data == 'scheduler_start':
        await start_scheduler_button(update, context)
        return
    elif query.data == 'scheduler_stop':
        await stop_scheduler_button(update, context)
        return

    # Regular profile buttons
    if query.data == 'x_profile':
        message = (
            "🐦 *X Profile*\n\n"
            f"Check out my X profile: [Link]({X_PROFILE_LINK})\n\n"
            "#X #SocialMedia #Profile"
        )
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    elif query.data == 'github_profile':
        message = (
            "💻 *GitHub Profile*\n\n"
            f"Check out my GitHub profile: [Link]({GITHUB_PROFILE_LINK})\n\n"
            "Explore my projects and contributions!\n\n"
            "#GitHub #Development #Code"
        )
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
    elif query.data == 'both_profiles':
        message = (
            "🔗 *My Profiles*\n\n"
            f"🐦 X: [Link]({X_PROFILE_LINK})\n\n"
            f"💻 GitHub: [Link]({GITHUB_PROFILE_LINK})\n\n"
            "Feel free to connect with me on both platforms!"
        )
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        '🤖 *Profile Share Bot*\n\n'
        '*User Commands:*\n'
        '/start - Start the bot\n'
        '/help - Show this help\n'
        '/profiles - Get both profile links\n'
        '/x - Get X profile\n'
        '/github - Get GitHub\n'
        '/menu - Open menu\n'
    )

    if is_admin(update.effective_user.id):
        help_text += (
            '\n*Admin Commands:*\n'
            '/sharex - Share X to channels\n'
            '/sharegithub - Share GitHub to channels\n'
            '/shareall - Share both to channels\n'
            '/addchannel - Add target channel\n'
            '/listchannels - List channels\n'
            '/startscheduler - Start auto-post\n'
            '/stopscheduler - Stop auto-post\n'
            '/status - Check status\n'
            '\n*Anti-Ban Features:*\n'
            '• Random delays between posts\n'
            '• Message rotation\n'
            '• Hourly limits\n'
            '• Cooldown periods'
        )

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show interactive menu."""
    await start(update, context)


async def profiles_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send both profile links."""
    message = (
        "🔗 *My Profiles*\n\n"
        f"🐦 X: [Link]({X_PROFILE_LINK})\n\n"
        f"💻 GitHub: [Link]({GITHUB_PROFILE_LINK})\n\n"
        "Feel free to connect with me on both platforms!"
    )
    await update.message.reply_text(
        text=message,
        parse_mode='Markdown',
        disable_web_page_preview=False
    )


async def x_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send X profile link."""
    message = (
        "🐦 *X Profile*\n\n"
        f"Check out my X profile: [Link]({X_PROFILE_LINK})\n\n"
        "#X #SocialMedia #Profile"
    )
    await update.message.reply_text(
        text=message,
        parse_mode='Markdown',
        disable_web_page_preview=False
    )


async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send GitHub profile link."""
    message = (
        "💻 *GitHub Profile*\n\n"
        f"Check out my GitHub profile: [Link]({GITHUB_PROFILE_LINK})\n\n"
        "Explore my projects and contributions!\n\n"
        "#GitHub #Development #Code"
    )
    await update.message.reply_text(
        text=message,
        parse_mode='Markdown',
        disable_web_page_preview=False
    )


async def share_x_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE, from_button: bool = False) -> None:
    """Share X profile to all target channels with anti-ban measures."""
    user = update.effective_user if not from_button else update.callback_query.from_user

    if not is_admin(user.id):
        if not from_button:
            await update.message.reply_text("❌ You don't have permission.")
        return

    if not TARGET_CHANNELS:
        if not from_button:
            await update.message.reply_text("⚠️ No target channels configured.")
        return

    # Check cooldown
    can_share, msg = check_cooldown()
    if not can_share:
        if not from_button:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    # Limit channels per hour to avoid ban
    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]

    message_template = random.choice(X_MESSAGES)
    message = message_template.format(link=X_PROFILE_LINK)

    success_count = 0
    failed_channels = []

    for channel in channels_to_share:
        success = await safe_send_message(context.bot, channel, message, 'Markdown')
        if success:
            success_count += 1
        else:
            failed_channels.append(channel)

    update_share_time()

    status_msg = f"✅ Shared X to {success_count} channel(s)."
    if failed_channels:
        status_msg += f"\n❌ Failed: {', '.join(failed_channels)}"
    if len(TARGET_CHANNELS) > MAX_CHANNELS_PER_HOUR:
        status_msg += f"\n⚠️ Limited to {MAX_CHANNELS_PER_HOUR} channels/hour for safety."

    if not from_button:
        await update.message.reply_text(status_msg)
    else:
        await update.callback_query.edit_message_text(status_msg)


async def share_github_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE, from_button: bool = False) -> None:
    """Share GitHub profile to all target channels with anti-ban measures."""
    user = update.effective_user if not from_button else update.callback_query.from_user

    if not is_admin(user.id):
        if not from_button:
            await update.message.reply_text("❌ You don't have permission.")
        return

    if not TARGET_CHANNELS:
        if not from_button:
            await update.message.reply_text("⚠️ No target channels configured.")
        return

    can_share, msg = check_cooldown()
    if not can_share:
        if not from_button:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]

    message_template = random.choice(GITHUB_MESSAGES)
    message = message_template.format(link=GITHUB_PROFILE_LINK)

    success_count = 0
    failed_channels = []

    for channel in channels_to_share:
        success = await safe_send_message(context.bot, channel, message, 'Markdown')
        if success:
            success_count += 1
        else:
            failed_channels.append(channel)

    update_share_time()

    status_msg = f"✅ Shared GitHub to {success_count} channel(s)."
    if failed_channels:
        status_msg += f"\n❌ Failed: {', '.join(failed_channels)}"
    if len(TARGET_CHANNELS) > MAX_CHANNELS_PER_HOUR:
        status_msg += f"\n⚠️ Limited to {MAX_CHANNELS_PER_HOUR} channels/hour for safety."

    if not from_button:
        await update.message.reply_text(status_msg)
    else:
        await update.callback_query.edit_message_text(status_msg)


async def share_all_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE, from_button: bool = False) -> None:
    """Share both profiles to all target channels with anti-ban measures."""
    user = update.effective_user if not from_button else update.callback_query.from_user

    if not is_admin(user.id):
        if not from_button:
            await update.message.reply_text("❌ You don't have permission.")
        return

    if not TARGET_CHANNELS:
        if not from_button:
            await update.message.reply_text("⚠️ No target channels configured.")
        return

    can_share, msg = check_cooldown()
    if not can_share:
        if not from_button:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]

    message_template = random.choice(COMBINED_MESSAGES)
    message = message_template.format(x_link=X_PROFILE_LINK, github_link=GITHUB_PROFILE_LINK)

    success_count = 0
    failed_channels = []

    for channel in channels_to_share:
        success = await safe_send_message(context.bot, channel, message, 'Markdown')
        if success:
            success_count += 1
        else:
            failed_channels.append(channel)

    update_share_time()

    status_msg = f"✅ Shared both profiles to {success_count} channel(s)."
    if failed_channels:
        status_msg += f"\n❌ Failed: {', '.join(failed_channels)}"
    if len(TARGET_CHANNELS) > MAX_CHANNELS_PER_HOUR:
        status_msg += f"\n⚠️ Limited to {MAX_CHANNELS_PER_HOUR} channels/hour for safety."

    if not from_button:
        await update.message.reply_text(status_msg)
    else:
        await update.callback_query.edit_message_text(status_msg)


async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a target channel (admin only)."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/addchannel <channel_id or @username>`\n\n"
            "Examples:\n"
            "`/addchannel @mychannel`\n"
            "`/addchannel -1001234567890`\n\n"
            "To get channel ID, add @userinfobot to your channel.",
            parse_mode='Markdown'
        )
        return

    channel = context.args[0]

    if channel in TARGET_CHANNELS:
        await update.message.reply_text(f"⚠️ {channel} is already in the list.")
        return

    # Test if bot can send message to channel
    try:
        await context.bot.send_message(
            chat_id=channel,
            text="🤖 Bot connected! Ready for sharing.",
            disable_notification=True
        )
        TARGET_CHANNELS.append(channel)
        await update.message.reply_text(f"✅ Added {channel} to target channels!")
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to add {channel}.\n\n"
            f"Make sure:\n"
            f"1. Channel ID/username is correct\n"
            f"2. Bot is an admin in that channel\n"
            f"3. For private channels, use ID (starts with -100)"
        )


async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all target channels."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission.")
        return

    if not TARGET_CHANNELS:
        await update.message.reply_text("📭 No target channels configured.")
        return

    channels_list = "\n".join([f"• `{ch}`" for ch in TARGET_CHANNELS])
    await update.message.reply_text(
        f"📢 *Target Channels ({len(TARGET_CHANNELS)}):*\n\n{channels_list}",
        parse_mode='Markdown'
    )


async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the user's Telegram ID."""
    user = update.effective_user
    await update.message.reply_text(
        f"👤 Your Info:\n\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'N/A'}\n"
        f"User ID: `{user.id}`\n\n"
        f"Add this ID to ADMIN_IDS in .env for admin access.",
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot status."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission.")
        return

    jobs = list(context.application.job_queue.jobs())
    is_running = len(jobs) > 0

    status_text = (
        "📊 *Bot Status*\n\n"
        f"Channels: {len(TARGET_CHANNELS)}\n"
        f"Auto-post: {'✅ ON' if is_running else '⏹️ OFF'}\n"
        f"Max channels/hour: {MAX_CHANNELS_PER_HOUR}\n"
        f"Cooldown: {COOLDOWN_MINUTES} minutes\n"
    )

    if last_share_time:
        elapsed = datetime.now() - last_share_time
        minutes_ago = int(elapsed.total_seconds() / 60)
        status_text += f"\nLast share: {minutes_ago} min ago"

    await update.message.reply_text(status_text, parse_mode='Markdown')


# Scheduler functions
async def scheduled_share_x(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automatically share X profile with anti-ban measures."""
    if not TARGET_CHANNELS:
        return

    # Limit channels and add random delays
    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]
    message_template = random.choice(X_MESSAGES)
    message = message_template.format(link=X_PROFILE_LINK)

    for channel in channels_to_share:
        await safe_send_message(context.bot, channel, message, 'Markdown')
        # Extra delay between scheduled posts
        await asyncio.sleep(random.uniform(5, 15))


async def scheduled_share_github(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automatically share GitHub profile with anti-ban measures."""
    if not TARGET_CHANNELS:
        return

    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]
    message_template = random.choice(GITHUB_MESSAGES)
    message = message_template.format(link=GITHUB_PROFILE_LINK)

    for channel in channels_to_share:
        await safe_send_message(context.bot, channel, message, 'Markdown')
        await asyncio.sleep(random.uniform(5, 15))


async def scheduled_share_all(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Automatically share both profiles with anti-ban measures."""
    if not TARGET_CHANNELS:
        return

    channels_to_share = TARGET_CHANNELS[:MAX_CHANNELS_PER_HOUR]
    message_template = random.choice(COMBINED_MESSAGES)
    message = message_template.format(x_link=X_PROFILE_LINK, github_link=GITHUB_PROFILE_LINK)

    for channel in channels_to_share:
        await safe_send_message(context.bot, channel, message, 'Markdown')
        await asyncio.sleep(random.uniform(5, 15))


async def start_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the auto-posting scheduler."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission.")
        return

    scheduler = context.application.job_queue

    # Remove existing jobs first
    for job in list(scheduler.jobs()):
        job.schedule_removal()

    # Schedule with random intervals (not exactly hourly to avoid patterns)
    scheduler.run_repeating(
        scheduled_share_x,
        interval=3600,
        first=random.randint(30, 120),
        name="x_post"
    )

    scheduler.run_repeating(
        scheduled_share_github,
        interval=3600,
        first=random.randint(1230, 1320),
        name="github_post"
    )

    scheduler.run_repeating(
        scheduled_share_all,
        interval=3600,
        first=random.randint(2430, 2520),
        name="combined_post"
    )

    await update.message.reply_text(
        "✅ Auto-posting started!\n\n"
        "📢 Schedule (approx every hour):\n"
        "• X Profile: Random time\n"
        "• GitHub: 20 min later\n"
        "• Both: 40 min later\n\n"
        "🛡️ Anti-ban: Random delays, message rotation"
    )


async def stop_scheduler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop the auto-posting scheduler."""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission.")
        return

    scheduler = context.application.job_queue
    for job in list(scheduler.jobs()):
        job.schedule_removal()

    await update.message.reply_text("🛑 Auto-posting stopped.")


async def start_scheduler_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start scheduler from button."""
    query = update.callback_query

    scheduler = context.application.job_queue

    for job in list(scheduler.jobs()):
        job.schedule_removal()

    scheduler.run_repeating(scheduled_share_x, interval=3600, first=random.randint(30, 120), name="x_post")
    scheduler.run_repeating(scheduled_share_github, interval=3600, first=random.randint(1230, 1320), name="github_post")
    scheduler.run_repeating(scheduled_share_all, interval=3600, first=random.randint(2430, 2520), name="combined_post")

    await query.edit_message_text("✅ Auto-posting started! Check /status for details.")


async def stop_scheduler_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop scheduler from button."""
    query = update.callback_query

    scheduler = context.application.job_queue
    for job in list(scheduler.jobs()):
        job.schedule_removal()

    await query.edit_message_text("🛑 Auto-posting stopped.")


def main() -> None:
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found!")
        return

    application = Application.builder().token(token).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("profiles", profiles_command))
    application.add_handler(CommandHandler("x", x_command))
    application.add_handler(CommandHandler("github", github_command))
    application.add_handler(CommandHandler("sharex", share_x_to_channels))
    application.add_handler(CommandHandler("sharegithub", share_github_to_channels))
    application.add_handler(CommandHandler("shareall", share_all_to_channels))
    application.add_handler(CommandHandler("addchannel", add_channel))
    application.add_handler(CommandHandler("listchannels", list_channels))
    application.add_handler(CommandHandler("getmyid", get_my_id))
    application.add_handler(CommandHandler("startscheduler", start_scheduler))
    application.add_handler(CommandHandler("stopscheduler", stop_scheduler))
    application.add_handler(CommandHandler("status", status_command))

    # Callback handler
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == '__main__':
    main()
