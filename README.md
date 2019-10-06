# codex-prime
Discord bot for Warframe information and tracking world state status using https://github.com/WFCD/warframe-status

## Set up
1. Log into Discord Developer Portal (https://discordapp.com/developers)
2. Create new application
3. Navigate to Bot -> Add Bot -> Set icon and username
4. Copy the bot token and set DISCORD_TOKEN in config.py
5. Navigate to OAuth2 -> Check bot under Scopes and set permissions
6. Copy and paste link into browser to invite bot into server
7. Run bot.py
 * You can also create an executable using PyInstaller
   * Install PyInstaller by running "pip install pyinstaller" in command prompt
   * Once PyInstaller is installed, navigate to src folder
   * Run "pyinstaller --onefile -i "path_to_icon_file\icon.ico" bot.py"
   * Run the executable file which will be located in the dist folder

## Features
- **Cetus Day/Night Cycle**
  * Be alerted x minutes before the next Cetus day/night cycle

- **Fissure Missions**
  * Track and be alerted of fissure missions based on relic or mission type

- **Invasions**
  * Track and be alerted of invasion missions with a specific reward

- **Others**
  * Get current sortie mission information
  * Get average prices for a riven
