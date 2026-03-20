# News Telegram Agent

An AI agent that fetches the latest news on a topic and sends it to your Telegram chat. Built with Groq’s LLM, NewsAPI, and Telegram Bot API.

## Features

- **Natural language queries** – Ask for news in plain English.
- **Real news fetching** – Uses NewsAPI to get current articles.
- **Telegram integration** – Sends the formatted news directly to your Telegram.
- **Fallback logic** – If the LLM doesn’t call the send tool, the agent still delivers the news via a simple global‑variable fallback.
- **Autonomous reasoning** – The agent decides when to fetch news and when to send.

## Architecture

The agent follows the **perceive → think → act → observe → repeat** loop:

1. User inputs a request (e.g., “top 5 news about Iran and Israel”).
2. The LLM (Groq) receives the prompt, conversation history, and tool definitions.
3. The LLM decides to call the `fetch_news` tool with the appropriate query.
4. The code executes `fetch_news`, which calls NewsAPI and returns formatted results.
5. The result is appended to the conversation, and the LLM produces a final answer (displayed in the CLI).
6. If the user later asks to send the news to Telegram, the fallback catches it and sends the stored news, bypassing the LLM for reliability.

## Tools Used

- **`fetch_news`** – calls NewsAPI and returns formatted article list.
- **`send_telegram_message`** – sends a text message via Telegram Bot API (used by fallback; the LLM currently does not call it).

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/news-telegram-agent.git
cd news-telegram-agent
2. Install dependencies
bash
pip install groq python-dotenv requests
3. Get API keys
Groq – Sign up at groq.com and get an API key.

NewsAPI – Register at newsapi.org (free tier).

Telegram – Create a bot with BotFather and get the token.
Find your chat ID by messaging the bot and visiting:
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates

4. Create a .env file
text
GROQ_API_KEY=your_groq_key
NEWS_API_KEY=your_newsapi_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
5. Run the agent
bash
python main.py
Usage
Ask for news
You: top 5 news about climate change

Send the last fetched news to Telegram
You: send that to telegram

Exit
You: exit

Example
text
Agent ready. Type 'exit' to quit.

You: top 3 news about AI

[Fetched News]
Top 3 news about 'AI':
1. ...
2. ...
3. ...

Agent: Here are the latest articles on AI...

You: send to telegram
Agent: Message sent successfully to Telegram.

Here is the news that was sent:
[Full news content]
File Structure
text
.
├── main.py            # Main agent code
├── .env               # Environment variables (ignored by git)
├── .gitignore         # Exclude .env and cache
└── README.md          # This file
Notes
The LLM is currently configured to use llama-3.1-70b-versatile (reliable for tool calls). You can change the model in the code.

The send_telegram_message tool is available but not actively used by the LLM due to the fallback. To enable full LLM‑driven sending, remove the fallback in run_agent and improve the system prompt.

Future Improvements
Let the LLM call send_telegram_message directly.

Add persistent memory (database) to remember past news across sessions.

Support multiple users with session management.

Add more tools (calculator, weather, etc.).


Acknowledgements
Groq for fast inference

NewsAPI for news data

Telegram Bot API

text

Make sure to replace `yourusername` with your actual GitHub username. Also, create a `.gitignore` file with at least:
.env
pycache/
*.pyc
.venv/

text

Then you can push to GitHub. Great work!
