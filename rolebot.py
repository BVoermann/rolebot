import os
import json
import discord
import traceback
import logging
import time
import sys
from discord.ext import commands, tasks
from dotenv import load_dotenv
import atexit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("rolebot")

# Check if running on Replit
ON_REPLIT = 'REPLIT_DB_URL' in os.environ

# Import keep_alive if on Replit
if ON_REPLIT:
    try:
        from keep_alive import keep_alive
        logger.info("Running on Replit, keep_alive module imported")
        
        # Also import the self-pinger
        try:
            from replit_ping import start_self_pinger
            logger.info("Self-pinger module imported")
        except ImportError:
            logger.warning("Self-pinger module not found. Bot may go to sleep on Replit.")
    except ImportError:
        logger.warning("Warning: keep_alive module not found. Bot may go to sleep on Replit.")

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    load_dotenv()
    logger.info("Loaded environment from .env file")

# Bot configuration
intents = discord.Intents.default()
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.message_content = True  # This is a privileged intent
intents.members = True  # Enable members intent to access the member list

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store role-emoji mappings
# Format: {message_id: {emoji_id: role_id}}
role_mappings = {}

# File to save/load role mappings
MAPPINGS_FILE = "role_mappings.json"

# Load role mappings from file
def load_role_mappings():
    global role_mappings
    try:
        if os.path.exists(MAPPINGS_FILE):
            with open(MAPPINGS_FILE, 'r') as f:
                # JSON loads message_id as string, need to convert back to int
                data = json.load(f)
                role_mappings = {int(k): v for k, v in data.items()}
                logger.info(f"Loaded role mappings: {role_mappings}")
        else:
            logger.info(f"No mappings file found at {MAPPINGS_FILE}")
    except Exception as e:
        logger.error(f"Error loading role mappings: {e}")
        traceback.print_exc()

# Save role mappings to file
def save_role_mappings():
    try:
        with open(MAPPINGS_FILE, 'w') as f:
            # Convert message_id to string for JSON
            json.dump({str(k): v for k, v in role_mappings.items()}, f, indent=4)
            logger.info(f"Saved role mappings to {MAPPINGS_FILE}")
    except Exception as e:
        logger.error(f"Error saving role mappings: {e}")
        traceback.print_exc()

@tasks.loop(minutes=10)
async def status_update():
    """Periodically update bot status and log memory usage to keep it active"""
    try:
        guild_count = len(bot.guilds)
        member_count = sum(len(guild.members) for guild in bot.guilds)
        
        # Update bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{guild_count} servers | !setup_roles"
        )
        await bot.change_presence(activity=activity)
        
        # Log some stats to keep the bot active
        logger.info(f"Status update: {guild_count} guilds, {member_count} members")
        
        # Log memory usage if on Replit
        if ON_REPLIT:
            try:
                memory_usage = os.popen('ps -o rss= -p ' + str(os.getpid())).read().strip()
                memory_usage_mb = round(int(memory_usage) / 1024, 2)
                logger.info(f"Memory usage: {memory_usage_mb} MB")
                
                # If memory usage is getting high, log a warning
                if memory_usage_mb > 400:  # 400MB is getting close to the 512MB limit
                    logger.warning(f"High memory usage: {memory_usage_mb} MB")
            except:
                pass
    except Exception as e:
        logger.error(f"Error in status update: {e}")

@bot.event
async def on_ready():
    logger.info(f'{bot.user.name} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Load the role mappings when the bot starts
    load_role_mappings()
    
    # Start the status update task
    status_update.start()

@bot.command(name='setup_roles')
@commands.has_permissions(administrator=True)
async def setup_roles(ctx, *, role_emoji_pairs=None):
    """
    Set up a reaction role message.
    Usage: !setup_roles Role1:emoji1 Role2:emoji2 ...
    Example: !setup_roles Admin:👑 Member:👋 Gamer:🎮
    """
    if role_emoji_pairs is None:
        await ctx.send("Please provide role-emoji pairs. Example: `!setup_roles Admin:👑 Member:👋`")
        return

    pairs = role_emoji_pairs.split()
    embed = discord.Embed(
        title="Role Assignment",
        description="React to get roles:",
        color=discord.Color.blue()
    )
    
    role_emojis = {}
    
    print(f"Processing role-emoji pairs: {pairs}")
    
    for pair in pairs:
        if ":" not in pair:
            await ctx.send(f"Invalid format for pair: {pair}. Use Role:emoji")
            continue
            
        role_name, emoji = pair.split(":", 1)
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if role is None:
            await ctx.send(f"Role '{role_name}' not found.")
            print(f"Role '{role_name}' not found in guild. Available roles: {[r.name for r in ctx.guild.roles]}")
            continue
            
        embed.add_field(name=role.name, value=f"React with {emoji} to get the {role.name} role", inline=False)
        role_emojis[emoji] = role.id
        print(f"Added mapping: {emoji} -> {role.name} (ID: {role.id})")
    
    if not role_emojis:
        await ctx.send("No valid role-emoji pairs provided.")
        return
        
    message = await ctx.send(embed=embed)
    
    # Store the role mappings for this message
    role_mappings[message.id] = role_emojis
    print(f"Created role-reaction message with ID: {message.id}")
    print(f"Current role_mappings: {role_mappings}")
    
    # Save the updated mappings
    save_role_mappings()
    
    # Add reactions to the message
    for emoji in role_emojis.keys():
        await message.add_reaction(emoji)
        print(f"Added reaction {emoji} to message")
    
    await ctx.message.delete()

@bot.command(name='show_mappings')
@commands.has_permissions(administrator=True)
async def show_mappings(ctx):
    """Show the current role-emoji mappings."""
    if not role_mappings:
        await ctx.send("No role mappings have been set up.")
        return
    
    # Print the mappings to the console for debugging
    print(f"Current mappings: {role_mappings}")
    
    embed = discord.Embed(
        title="Current Role Mappings",
        description="The following role-emoji mappings are active:",
        color=discord.Color.green()
    )
    
    for message_id, emojis in role_mappings.items():
        message_link = f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message_id}"
        field_value = ""
        
        for emoji, role_id in emojis.items():
            role = ctx.guild.get_role(role_id)
            role_name = role.name if role else "Unknown Role"
            field_value += f"{emoji} → {role_name}\n"
            
        embed.add_field(
            name=f"Message: [Jump to message]({message_link})",
            value=field_value,
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.event
async def on_raw_reaction_add(payload):
    # Ignore bot's own reactions
    if payload.user_id == bot.user.id:
        return
        
    try:
        # Check if the reacted message is one of our role messages
        if payload.message_id in role_mappings:
            emoji = str(payload.emoji)
            emoji_mappings = role_mappings[payload.message_id]
            
            print(f"Reaction added - Message ID: {payload.message_id}, Emoji: {emoji}")
            print(f"Available emojis for this message: {list(emoji_mappings.keys())}")
            
            # Check if the emoji is one we're tracking
            if emoji in emoji_mappings:
                role_id = emoji_mappings[emoji]
                guild = bot.get_guild(payload.guild_id)
                
                if guild is None:
                    print(f"Error: Could not find guild with ID {payload.guild_id}")
                    return
                    
                role = guild.get_role(role_id)
                
                if role is None:
                    print(f"Error: Could not find role with ID {role_id}")
                    return
                
                # Try to get member from cache first, then try to fetch if not found
                member = guild.get_member(payload.user_id)
                if member is None:
                    try:
                        print(f"Member not in cache, attempting to fetch member {payload.user_id}")
                        member = await guild.fetch_member(payload.user_id)
                    except discord.errors.NotFound:
                        print(f"Error: Could not find member with ID {payload.user_id} even after fetching")
                        return
                    except Exception as e:
                        print(f"Error fetching member: {e}")
                        return
                
                print(f"Attempting to add role '{role.name}' to user '{member.display_name}'")
                await member.add_roles(role)
                print(f"Role '{role.name}' added to '{member.display_name}' successfully")
            else:
                print(f"Emoji {emoji} not found in mappings for message {payload.message_id}")
    except Exception as e:
        print(f"Error in on_raw_reaction_add: {e}")
        traceback.print_exc()

@bot.event
async def on_raw_reaction_remove(payload):
    try:
        # Check if the reacted message is one of our role messages
        if payload.message_id in role_mappings:
            emoji = str(payload.emoji)
            emoji_mappings = role_mappings[payload.message_id]
            
            print(f"Reaction removed - Message ID: {payload.message_id}, Emoji: {emoji}")
            
            # Check if the emoji is one we're tracking
            if emoji in emoji_mappings:
                role_id = emoji_mappings[emoji]
                guild = bot.get_guild(payload.guild_id)
                
                if guild is None:
                    print(f"Error: Could not find guild with ID {payload.guild_id}")
                    return
                    
                role = guild.get_role(role_id)
                
                if role is None:
                    print(f"Error: Could not find role with ID {role_id}")
                    return
                
                # Try to get member from cache first, then try to fetch if not found
                member = guild.get_member(payload.user_id)
                if member is None:
                    try:
                        print(f"Member not in cache, attempting to fetch member {payload.user_id}")
                        member = await guild.fetch_member(payload.user_id)
                    except discord.errors.NotFound:
                        print(f"Error: Could not find member with ID {payload.user_id} even after fetching")
                        return
                    except Exception as e:
                        print(f"Error fetching member: {e}")
                        return
                
                print(f"Attempting to remove role '{role.name}' from user '{member.display_name}'")
                await member.remove_roles(role)
                print(f"Role '{role.name}' removed from '{member.display_name}' successfully")
            else:
                print(f"Emoji {emoji} not found in mappings for message {payload.message_id}")
    except Exception as e:
        print(f"Error in on_raw_reaction_remove: {e}")
        traceback.print_exc()

# Also ensure we save any changes to role mappings when the bot stops 
atexit.register(save_role_mappings)

# Reconnect handler
@bot.event
async def on_resumed():
    logger.info("Bot resumed connection with Discord")

# Error handler for the bot
@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Error in event {event}: {sys.exc_info()[1]}")
    traceback.print_exc()

# Run the bot
if __name__ == "__main__":
    # Try to get token from environment variables (works with both .env and Replit secrets)
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        logger.error("No Discord token found. Make sure to set DISCORD_TOKEN in your .env file or Replit secrets.")
        logger.info("\nIf you're using Replit, add your token as a secret:")
        logger.info("1. Click on 'Tools' in the left sidebar")
        logger.info("2. Select 'Secrets'")
        logger.info("3. Add a new secret with key 'DISCORD_TOKEN' and your bot token as the value")
    else:
        try:
            logger.info("Starting bot...")
            
            # Start the keep_alive server if on Replit
            if ON_REPLIT:
                try:
                    keep_alive_thread = keep_alive()
                    logger.info("Keep alive server started")
                    
                    # Also start the self-pinger
                    try:
                        pinger_thread = start_self_pinger(interval_seconds=240)  # ping every 4 minutes
                        logger.info("Self-pinger started")
                    except Exception as e:
                        logger.error(f"Could not start self-pinger: {e}")
                except Exception as e:
                    logger.error(f"Could not start keep_alive server: {e}")
            
            # Run the bot with automatic reconnects enabled
            bot.run(TOKEN, reconnect=True)
        except discord.errors.PrivilegedIntentsRequired:
            logger.error("\n===== ERROR: PRIVILEGED INTENTS REQUIRED =====")
            logger.error("You need to enable privileged intents in the Discord Developer Portal.")
            logger.error("\nPlease follow these steps:")
            logger.error("1. Go to https://discord.com/developers/applications/")
            logger.error("2. Select your bot application")
            logger.error("3. Go to the 'Bot' tab")
            logger.error("4. Scroll down to 'Privileged Gateway Intents'")
            logger.error("5. Enable 'MESSAGE CONTENT INTENT'")
            logger.error("6. Click 'Save Changes'")
            logger.error("7. Restart the bot")
            logger.error("\nIf you don't want to enable these intents, you will need to modify the code to not use them.")
            logger.error("===============================================")
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            traceback.print_exc() 