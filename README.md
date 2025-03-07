# Discord Role Bot for Render.com

A Discord bot that allows users to assign themselves roles by reacting to messages with specific emojis.

## Features

- Create role-reaction messages with custom emojis
- Automatically assign roles when users react to messages
- Remove roles when reactions are removed
- Admin commands to set up and manage role reactions

## Prerequisites

- A Discord bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
- A Render.com account

## Deployment to Render.com

### Step 1: Prepare Your Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select your existing one
3. Go to the "Bot" tab and click "Add Bot"
4. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
   - Presence Intent
5. Copy your bot token (you'll need it for Render.com)
6. Go to the OAuth2 tab, select "bot" scope and appropriate permissions
7. Copy the generated URL and use it to invite the bot to your server

### Step 2: Deploy to Render.com

1. Fork or clone this repository to your GitHub account
2. Log in to [Render.com](https://render.com)
3. Click "New" and select "Blueprint" or "Web Service"
4. Connect your GitHub account and select this repository
5. Choose "Python" as the environment
6. Set the following configuration:
   - **Name**: discord-rolebot (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python rolebot.py`
   
7. Add the following environment variable:
   - **Key**: `DISCORD_TOKEN`
   - **Value**: Your Discord bot token

8. Click "Create Web Service"

Render will automatically deploy your bot and keep it running 24/7.

## Local Development

To run the bot locally for development:

1. Clone the repository
2. Create a `.env` file in the root directory with:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```
3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```
   python rolebot.py
   ```

## Bot Commands

- `!setup_roles Role1:emoji1 Role2:emoji2 ...` - Create a new role-reaction message
  - Example: `!setup_roles Admin:👑 Member:👋 Gamer:🎮`
- `!show_mappings` - Show all active role-emoji mappings

## License

MIT License - See LICENSE file for details. 
