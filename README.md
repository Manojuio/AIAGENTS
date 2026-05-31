# 🤖 AI Agents Monorepo

A collection of three specialized AI agents built with modern Python tooling:

- **[BUGRAY](BUGRAY/)** – Asynchronous CLI debugging engine powered by Gemini LLMs.
- **[skillmatch-ai](skillmatch-ai/)** – Intelligent job matching agent using Groq and Tavily.
- **[telegram-bot](telegram-bot/)** – Telegram interface for interacting with the skillmatch-ai agent.

Each project is self-contained with its own dependencies and entry points, making it easy to develop, run, and deploy independently.

---

## 📁 Project Structure
aiagents/
├── BUGRAY/ # CLI Debugging Agent
│ ├── agent/ # Core agent logic & tools
│ ├── main.py # CLI entry point
│ └── pyproject.toml # uv-managed dependencies
├── skillmatch-ai/ # Job Matching Agent
│ ├── agent.py # Agent core & tool definitions
│ ├── main.py # Terminal entry point
│ └── pyproject.toml # uv-managed dependencies
├── telegram-bot/ # Telegram Bot Interface
│ ├── main.py # Bot handler & message processing
│ └── pyproject.toml # uv-managed dependencies
└── README.md # This file

text

---

## 🛠️ Prerequisites

- **Python 3.11+** (all projects share this requirement)
- **uv** – Fast Python package and project manager
- API keys for the services you intend to use:
  - BUGRAY → Gemini API
  - skillmatch-ai → Groq API, Tavily API
  - telegram-bot → Telegram Bot Token, Groq API, Tavily API

Install **uv** if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
🚀 Getting Started
Each project is entirely independent — navigate to the corresponding folder and follow its specific setup instructions.

1. Clone the Repository
bash
git clone https://github.com/Manojuio/aiagents.git
cd aiagents
2. Choose & Set Up a Project
🔧 BUGRAY – CLI Debugging Agent
bash
cd BUGRAY
echo 'GEMINI_API_KEY="your_gemini_api_key_here"' > .env
uv sync
uv run python main.py "Your debugging query"
🧩 skillmatch-ai – Job Matching Agent
bash
cd skillmatch-ai
echo 'GROQ_API_KEY="your_groq_api_key_here"' > .env
echo 'TAVILY_API_KEY="your_tavily_api_key_here"' >> .env
uv sync
uv run python main.py
📱 telegram-bot – Telegram Bot Interface
bash
cd telegram-bot
echo 'GROQ_API_KEY="your_groq_api_key_here"' > .env
echo 'TAVILY_API_KEY="your_tavily_api_key_here"' >> .env
echo 'TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"' >> .env
uv sync
uv run python main.py
🔑 Environment Variables
Project	Variable	Description
BUGRAY	GEMINI_API_KEY	Google Gemini API key
skillmatch-ai	GROQ_API_KEY	Groq Cloud API key
skillmatch-ai	TAVILY_API_KEY	Tavily Search API key
telegram-bot	TELEGRAM_BOT_TOKEN	Telegram Bot token (from @BotFather)
telegram-bot	GROQ_API_KEY	Groq Cloud API key (for agent calls)
telegram-bot	TAVILY_API_KEY	Tavily Search API key (for agent calls)
⚠️ Never commit .env files. Each project includes a .gitignore that blocks them automatically.

💡 Usage Examples
BUGRAY – Debugging
bash
uv run python main.py "Uncaught TypeError inside server.js on line 24"
The agent inspects files, runs diagnostic commands, and suggests fixes.

skillmatch-ai – Job Search (Terminal)
bash
uv run python main.py
Then type queries like:

"Find remote Python developer jobs"

"Find jobs matching my resume" (after uploading a PDF)

telegram-bot – Job Search via Telegram
Start the bot, send /start, upload your resume as a PDF, and chat naturally:

"Find me Node.js backend roles"

"Score my fit for this job"

📄 Documentation
Each subproject contains its own README.md with detailed instructions, architecture notes, and API references.

BUGRAY README

skillmatch-ai README

telegram-bot README

🤝 Contributing
Contributions are welcome! To keep the monorepo clean:

Fork the repository.

Create a feature branch (git checkout -b feature/amazing-feature).

Make your changes within the appropriate subproject folder.

Ensure each subproject remains independent (no cross‑imports between folders).

Submit a pull request.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

🙏 Acknowledgements
Groq – Ultra‑fast LLM inference

Tavily – AI‑powered search

Gemini – Google's LLM family

python-telegram-bot – Telegram Bot API wrapper

uv – Fast Python package manager

*Built with ❤️ using Python 3.11+ and uv.*

text

Just copy this Markdown into a new `README.md` file at the root of your repository. Then, to make the documentation even clearer, it would be helpful to add a short `README.md` inside each subfolder (for example, a brief description of what the project does and how to run it).
