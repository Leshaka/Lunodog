# LunoDog
LunoDog is a multi-purpose discord bot with modular design made for #promode.ru community.
### Features
  - Web interface
  - Quake servers querier
  - Twitch streams notifications and summary
  - Greetings for new server members / goodbyes for left members
  - Role subsribtions via reactions and /slash commands
  - Customizable server info board with autocompletion
  - Server members profiler, statuses / messages / reactions stats
  - Translate messages by rigth-click -> apps -> Translate
  - Role-based server moderation via /isolator command
  - Roll a random anime image from danbooru with tags
### Public instance
https://lunodog.leshaka.xyz

# Hosting locally
#### Requirements
- mysql-compatible database
- python3.11+
- npm

#### Setting up database
```
sudo mysql

CREATE USER 'lduser'@'localhost' IDENTIFIED BY 'insert-a-password-here';
CREATE DATABASE lddb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL ON lddb.* TO 'lduser'@'localhost';
GRANT FILE ON *.* TO 'lduser'@'localhost';
exit;

sudo mysql lddb < sql/create_tables.sql
```
#### Setting up the bot
```
# fill the bot configuration file with your bot account credentials
# may set API_NO_AUTH to True to disable discord oauth2 authorization for the web api routes
cp config.example.py config.py
nano config.py
# install required python packages
python -m pip install -r requirements.txt
# register bot /slash commands to the discord API
python register_slash_commands.py
# launch the bot
python LunoDog.py
```
#### Setting up web interface
```
cd LunoDog-UI
# configure vite web server
cp vite.config.example.js vite.config.js
nano vite.config.js
# configure web app
cp src/config.example.js src/config.js
nano src/config.js
# install npm packages
npm install
# run the webserver
npm run dev
```
