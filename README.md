# League of Legends Coaching Bot

This project is a Discord bot designed to analyze a player's League of Legends performance. It fetches data from the last 20 matches using the Riot Games API and uses Google's Gemini AI to provide personalized coaching insights and advice for improvement.

## Features

- **Match Analysis**: Retrieves statistics from the last 20 matches for a specified player.
- **AI Coaching**: Uses Gemini AI to analyze performance metrics (KDA, CS/min, vision score, damage, etc.) and generate actionable advice.
- **Discord Integration**: Simple `/coach` command to trigger the analysis directly within Discord.
- **Data Export**: Includes a utility script (`export.py`) to export match data to CSV, JSON, and TOON formats.

## Prerequisites

Before running the bot, ensure you have the following:

- **Python 3.8+** installed.
- **Discord Bot Token**: Create a bot on the [Discord Developer Portal](https://discord.com/developers/applications).
- **Riot Games API Key**: Obtain a key from the [Riot Developer Portal](https://developer.riotgames.com/).
- **Gemini API Key**: Get an API key from [Google AI Studio](https://aistudio.google.com/).

## Installation

1.  **Clone the repository** (if applicable) or download the source code.

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Create a `.env` file in the root directory of the project and add your API keys and configuration:

```dotenv
DISCORD_BOT_TOKEN=your_discord_bot_token
RIOT_API_KEY=your_riot_api_key
GEMINI_API_KEY=your_gemini_api_key

# Optional defaults
DEFAULT_GAME_NAME=YourRiotName
DEFAULT_TAG_LINE=YourTagLine
REGION_ROUTING=europe # e.g., americas, asia, europe
GEMINI_MODEL=gemini-1.5-pro
PROMPT_PATH=prompt_lol.md
```

## Usage

### Running the Bot

Start the bot by running the `bot.py` script:

```bash
python bot.py
```

### Discord Command

Once the bot is online and invited to your server, use the slash command:

```
/coach [game_name] [tag_line]
```

- `game_name`: Your Riot Game Name (optional if default is set in `.env`).
- `tag_line`: Your Riot Tag Line (optional if default is set in `.env`).

The bot will analyze your last 20 matches and reply with a detailed coaching report.

### Data Export Utility

You can also use the `export.py` script to fetch and save match data locally:

```bash
python export.py
```
*Note: You may need to modify the `API_KEY`, `GAME_NAME`, and `TAG_LINE` variables directly in `export.py` or adapt it to use environment variables.*

## Note on Language

The current analysis prompt (`prompt_lol.md`) is in French. The bot's output will therefore be in French. You can modify this file to change the language or the focus of the coaching advice.
