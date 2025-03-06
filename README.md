# Discord Role Bot

A Discord bot that allows users to assign themselves roles by reacting to messages with specific emojis.

## Features

- Create role-reaction messages with custom emojis
- Automatically assign roles when users react to messages
- Remove roles when reactions are removed
- Admin commands to set up and manage role reactions

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Discord account
- A Discord server where you have admin permissions

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/rolebot.git
cd rolebot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a Discord bot:
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" tab and click "Add Bot"
   - Under the "Privileged Gateway Intents" section, enable:
     - Presence Intent
     - Server Members Intent
     - Message Content Intent
   - Under the "Bot Permissions" section, you can use the "Administrator" permission for simplicity, or select the following specific permissions:
     - Manage Roles
     - Read Messages/View Channels
     - Send Messages
     - Manage Messages
     - Embed Links
     - Add Reactions
     - Read Message History

4. Invite the bot to your server:
   - Go to the "OAuth2" tab in the Discord Developer Portal
   - Select the "bot" scope
   - Select the necessary permissions (same as above)
   - Copy the generated URL and paste it into your browser
   - Select your server and authorize the bot

5. Copy your bot token:
   - Go back to the "Bot" tab in the Discord Developer Portal
   - Click "Reset Token" if you need a new token
   - Click "Copy" to copy your bot token

6. Create a `.env` file in the root directory of the project:
   - Copy the content from `.env.example`
   - Replace `your_discord_bot_token_here` with your actual bot token

## Security Notice for Developers

This project uses environment variables to store sensitive information like the Discord bot token. When working with this code:

1. **NEVER commit your `.env` file to version control**
   - The `.gitignore` file is set up to exclude it
   - Only commit the `.env.example` template

2. **Keep your bot token secret**
   - Anyone with your token can control your bot
   - If you accidentally expose your token, reset it immediately in the Discord Developer Portal

3. **When deploying:**
   - Set environment variables directly on your hosting platform when possible
   - For VPS deployments, ensure the `.env` file has restricted permissions

## Usage

1. Run the bot:
```bash
python rolebot.py
```

2. Bot Commands:
   - `!setup_roles Role1:emoji1 Role2:emoji2 ...` - Creates a new role-reaction message
     - Example: `!setup_roles Admin:👑 Member:👋 Gamer:🎮`
   - `!show_mappings` - Shows all active role-emoji mappings

3. How it works:
   - When an admin uses the `!setup_roles` command, the bot creates a message with instructions
   - Users can click on the emoji reactions to get the corresponding role
   - If a user removes their reaction, the role is also removed

## Deployment Options

### Running on your local machine

- Keep the terminal/command prompt open
- The bot will run as long as your computer is on and connected to the internet

### Running on a VPS (Virtual Private Server)

1. Get a VPS from providers like DigitalOcean, AWS, Linode, etc.
2. Set up your VPS with SSH access
3. Upload your bot files to the server
4. Install Python and dependencies
5. Run the bot using a process manager like systemd, pm2, or screen:

Using systemd (recommended for Linux servers):
```bash
# Create a service file
sudo nano /etc/systemd/system/discordrolebot.service

# Add the following content (modify paths as needed)
[Unit]
Description=Discord Role Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/rolebot
ExecStart=/usr/bin/python3 /path/to/rolebot/rolebot.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start the service
sudo systemctl enable discordrolebot
sudo systemctl start discordrolebot

# Check status
sudo systemctl status discordrolebot
```

### Using a free hosting service

There are several free hosting services for Discord bots:
- [Replit](https://replit.com) - Free tier available
- [Heroku](https://heroku.com) - Free tier available for small projects
- [Railway](https://railway.app) - Offers free credits

For Replit specifically:
1. Create a Replit account
2. Create a new Python repl
3. Upload your bot files
4. Set up environment variables in the Replit dashboard
5. Use the Replit database to store your token securely
6. Set up a keep-alive mechanism for the free tier

## Tips for Operation

- Make sure your bot has a role that is higher in the hierarchy than any role it needs to assign
- The bot requires the "Manage Roles" permission to assign roles
- Users can only get roles that are lower in the hierarchy than the bot's highest role
- Use the `!show_mappings` command to see all active role-reaction messages

## Troubleshooting

- If the bot doesn't respond, check if it's online in your Discord server
- Ensure the bot has the necessary permissions
- Make sure your `.env` file contains the correct token
- Check the console/terminal for any error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 