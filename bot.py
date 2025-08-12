import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import UserDatabase
from config import BOT_TOKEN, ADMIN_USER_ID, DB_FILE

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = UserDatabase(DB_FILE)

# Store admin's current chat session
admin_current_chat = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    if user.id == ADMIN_USER_ID:
        # Admin commands
        await update.message.reply_text(
            "🛡️ Admin Panel\n\n"
            "Available commands:\n"
            "/users - View all users\n"
            "/stats - View statistics\n"
            "/help - Show help"
        )
    else:
        # Client welcome message
        db.add_user(user.id, user.username, user.first_name)
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n"
            "Welcome to our service. You can send me any message and I'll forward it to our team.\n"
            "We'll get back to you as soon as possible.\n\n"
            "Just type your message below 👇"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user = update.effective_user
    
    if user.id == ADMIN_USER_ID:
        await update.message.reply_text(
            "🛡️ Admin Help\n\n"
            "Commands:\n"
            "/users - View all users\n"
            "/stats - View statistics\n"
            "/reply <user_id> <message> - Reply to a specific user\n"
            "/broadcast <message> - Send message to all users\n"
            "/block <user_id> - Block a user\n"
            "/unblock <user_id> - Unblock a user"
        )
    else:
        await update.message.reply_text(
            "💬 Help\n\n"
            "Simply send me any message and I'll forward it to our team.\n"
            "We'll respond to you as soon as possible.\n\n"
            "You can send text, photos, documents, or any other type of message."
        )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    users = db.get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return
    
    message = "👥 Active Users:\n\n"
    for user in users:
        username = user.get('username', 'No username')
        first_name = user.get('first_name', 'Unknown')
        user_id = user['user_id']
        joined_date = user.get('joined_date', 'Unknown')
        
        message += f"🆔 ID: {user_id}\n"
        message += f"👤 Name: {first_name}\n"
        message += f"📝 Username: @{username}\n"
        message += f"📅 Joined: {joined_date[:10]}\n"
        message += f"💬 Messages: {len(user.get('messages', []))}\n"
        message += "─" * 30 + "\n"
    
    # Split message if too long
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await update.message.reply_text(message[x:x+4096])
    else:
        await update.message.reply_text(message)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    users = db.get_all_users()
    total_users = len(users)
    total_messages = sum(len(user.get('messages', [])) for user in users)
    
    await update.message.reply_text(
        f"📊 Statistics\n\n"
        f"👥 Total Users: {total_users}\n"
        f"💬 Total Messages: {total_messages}\n"
        f"📈 Average Messages per User: {total_messages/total_users if total_users > 0 else 0:.1f}"
    )

async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reply command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return
    
    try:
        target_user_id = int(context.args[0])
        reply_message = ' '.join(context.args[1:])
        
        # Send message to user
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"💬 Reply from our team:\n\n{reply_message}"
            )
            
            # Save message to database
            db.add_message(target_user_id, reply_message, is_from_admin=True)
            
            await update.message.reply_text(f"✅ Reply sent to user {target_user_id}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send message to user {target_user_id}: {str(e)}")
            
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a valid number.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    broadcast_message = ' '.join(context.args)
    users = db.get_all_users()
    
    success_count = 0
    failed_count = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user['user_id'],
                text=f"📢 Announcement:\n\n{broadcast_message}"
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to send broadcast to user {user['user_id']}: {e}")
    
    await update.message.reply_text(
        f"📢 Broadcast completed!\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed: {failed_count}"
    )

async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /block command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /block <user_id>")
        return
    
    try:
        target_user_id = int(context.args[0])
        db.deactivate_user(target_user_id)
        await update.message.reply_text(f"✅ User {target_user_id} has been blocked.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a valid number.")

async def unblock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unblock command - Admin only"""
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /unblock <user_id>")
        return
    
    try:
        target_user_id = int(context.args[0])
        db.activate_user(target_user_id)
        await update.message.reply_text(f"✅ User {target_user_id} has been unblocked.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a valid number.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    user = update.effective_user
    message = update.message
    
    if user.id == ADMIN_USER_ID:
        # Admin message handling
        await handle_admin_message(update, context)
    else:
        # Client message handling
        await handle_client_message(update, context)

async def handle_client_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from clients"""
    user = update.effective_user
    message = update.message
    
    # Check if user is blocked
    user_data = db.get_user(user.id)
    if not user_data or not user_data.get('is_active', True):
        await message.reply_text("❌ You have been blocked from using this bot.")
        return
    
    # Add user to database if not exists
    db.add_user(user.id, user.username, user.first_name)
    
    # Save message to database
    message_text = message.text or message.caption or "Media message"
    db.add_message(user.id, message_text, is_from_admin=False)
    
    # Forward message to admin
    try:
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"📨 New message from user:\n\n"
                 f"👤 User: {user.first_name} (@{user.username or 'No username'})\n"
                 f"🆔 ID: {user.id}\n"
                 f"💬 Message: {message_text}\n\n"
                 f"Reply with: /reply {user.id} <your message>"
        )
        
        # Send confirmation to client
        await message.reply_text("✅ Your message has been sent to our team. We'll get back to you soon!")
        
    except Exception as e:
        logger.error(f"Failed to forward message to admin: {e}")
        await message.reply_text("❌ Sorry, there was an error sending your message. Please try again later.")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from admin"""
    message = update.message
    
    # If admin sends a message without command, show quick reply options
    if not message.text.startswith('/'):
        users = db.get_all_users()
        if not users:
            await message.reply_text("No active users to reply to.")
            return
        
        # Create inline keyboard with recent users
        keyboard = []
        for user in users[-5:]:  # Show last 5 users
            keyboard.append([
                InlineKeyboardButton(
                    f"{user['first_name']} ({user['user_id']})", 
                    callback_data=f"reply_{user['user_id']}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(
            "Select a user to reply to:",
            reply_markup=reply_markup
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("reply_"):
        user_id = int(query.data.split("_")[1])
        global admin_current_chat
        admin_current_chat = user_id
        
        user_data = db.get_user(user_id)
        if user_data:
            await query.edit_message_text(
                f"💬 Replying to: {user_data['first_name']} (@{user_data.get('username', 'No username')})\n"
                f"🆔 ID: {user_id}\n\n"
                f"Type your reply message now, or use /reply {user_id} <message>"
            )
        else:
            await query.edit_message_text("User not found.")

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reply", reply_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("block", block_command))
    application.add_handler(CommandHandler("unblock", unblock_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("🤖 Bot is starting...")
    print(f"👤 Admin ID: {ADMIN_USER_ID}")
    print("✅ Bot is ready!")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
