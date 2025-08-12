# Telegram Client Support Bot

A Telegram bot that acts as an intermediary between you (admin) and your clients. Clients can send messages to you through the bot, and you can reply back to them, with each user having separate chat sessions.

## Features

### For Clients:
- Send messages to the admin through the bot
- Receive replies from the admin
- Simple and user-friendly interface
- Support for text, photos, documents, and other media

### For Admin:
- View all active users
- Reply to specific users
- Broadcast messages to all users
- Block/unblock users
- View statistics
- Separate chat sessions for each user

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Bot
```bash
python bot.py
```

## Bot Commands

### Admin Commands:
- `/start` - Start the bot and see admin panel
- `/help` - Show admin help with all commands
- `/users` - View all active users
- `/stats` - View bot statistics
- `/reply <user_id> <message>` - Reply to a specific user
- `/broadcast <message>` - Send message to all users
- `/block <user_id>` - Block a user
- `/unblock <user_id>` - Unblock a user

### Client Commands:
- `/start` - Start the bot and get welcome message
- `/help` - Show help for clients

## How It Works

1. **Client sends message** → Bot forwards it to admin with user details
2. **Admin receives notification** → Can see user info and message
3. **Admin replies** → Bot sends reply back to the specific client
4. **Separate sessions** → Each client has their own chat history

## File Structure

- `bot.py` - Main bot script
- `config.py` - Configuration settings
- `database.py` - Database management for user sessions
- `requirements.txt` - Python dependencies
- `user_sessions.json` - User data storage (created automatically)

## Security Features

- Only the admin (ID: 8324487113) can access admin commands
- Users can be blocked/unblocked
- All messages are logged in the database
- Separate chat sessions prevent message mixing

## Usage Examples

### Admin replying to a user:
```
/reply 123456789 Hello! Thank you for your message. We'll help you soon.
```

### Broadcasting to all users:
```
/broadcast Important announcement: We'll be closed tomorrow for maintenance.
```

### Blocking a user:
```
/block 123456789
```

## Notes

- The bot uses a simple JSON file for data storage
- All user messages are saved with timestamps
- The bot automatically handles media messages
- Admin can see user statistics and manage users easily

## Troubleshooting

If the bot doesn't start:
1. Check if all dependencies are installed
2. Verify the bot token is correct
3. Make sure you have internet connection
4. Check if the bot token is valid and not revoked

## Support

For any issues or questions, please check the bot's `/help` command or refer to this README.
