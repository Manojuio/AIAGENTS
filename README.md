# ⚡ BUGRAY 

A production-ready, asynchronous CLI debugging engine powered by Gemini LLMs. Built with a modular **Folder-by-Feature (Mono-Feature)** architecture, Bugray functions as an autonomous terminal agent. It utilizes native tool-calling capabilities to actively inspect local filesystems, execute debugging tests in isolated environments, and triage stack traces directly from your command line.

---

## 🏗️ System Architecture

Bugray rejects standard beginner folder-by-type structures in favor of an enterprise-ready, modular **Folder-by-Feature** layout. This ensures the entire core engine loop can be dropped cleanly into any interface provider (CLI, Slack, or Telegram bot gateways) without modifying core orchestration workflows.

```text
BUGRAY/
├── 📁 agent/                  # Core Feature Domain
│   ├── 📁 tools/              # Autonomous Agent Execution Capabilities
│   │   ├── 🐍 __init__.py     # Tool Registration Manifest
│   │   ├── 🐍 filesystem.py   # Secure File Reads, Writes, & Diff Scans
│   │   └── 🐍 terminal.py     # Local Isolated Subprocess Command Executor
│   ├── 🐍 orchestrator.py     # Asynchronous Multi-Turn Thought/Action Loop
│   └── 🐍 system_prompt.py    # Strategic Debugging Guardrails & System Persona
├── ⚙️ .gitignore               # Blocks tracking of heavy local environments & keys
├── 🐍 config.py               # Application Constants & Gemini Clients Initialization
├── 🐍 main.py                 # Core CLI Loop & Global Parameter Gateway
├── ⚙️ pyproject.toml           # Unified Project Manifest (uv standards)
└── 📄 uv.lock                 # Deterministic Dependency Tree Lockfile
⚡ Core Features
Autonomous Tool-Use (Function Calling): The agent does not simply suggest fixes; it actively inspects files via the filesystem tool and validates syntax execution using the terminal tool.

Deterministic Environment Management: Powered by uv for package indexing and workspace locking, guaranteeing absolute zero package drift across different development machines.

Granular Multi-Turn Logic: Features a stateful memory execution thread inside orchestrator.py that continuously processes error diagnostics until a precise patch sequence is achieved.

Secure-by-Default Infrastructure: Explicit sandbox constraints built into system prompts with strict automated .env masking to safeguard localized environment variables.

🛠️ Installation & Workspace Setup
Prerequisites
Ensure you have uv (the fast Python package manager) installed on your machine:

PowerShell
powershell -c "irm uv.pub/install.ps1 | iex"
1. Clone & Navigate
Navigate into your unified portfolio workspace root:

DOS
cd C:\Users\undra\OneDrive\aiagents\BUGRAY
2. Configure Environment Secrets
Create your localized workspace .env file to map your API credentials securely:

DOS
echo GEMINI_API_KEY="your_actual_gemini_api_key_here" > .env
(Note: .env is automatically ignored by Git rules and will never be exposed to public code streams).

3. Initialize the Locked Environment
Sync and install the complete deterministic dependency manifest using the uv lock controller:

DOS
uv sync
🚀 Execution & Shorthand Integration
You can execute queries directly inside the virtual environment by targeting the root execution module:

DOS
uv run python main.py "Uncaught TypeError inside server.js on line 24"
💻 Setting up the Global Terminal Shortcut
To fire up the engine instantly from any active root directory on your system, add a permanent wrapper shortcut alias directly to your shell profile layout:

Open your PowerShell profile manifest:

PowerShell
   notepad $PROFILE
Append this operational alias layout to the bottom of your configuration matrix:

PowerShell
   function bugray_cmd {
       param([string]$query)
       uv run --project "C:\Users\undra\OneDrive\aiagents\BUGRAY" "C:\Users\undra\OneDrive\aiagents\BUGRAY\main.py" $query
   }
   Set-Alias bugray bugray_cmd
Reload your active profile instance or restart the host terminal window.

Now, call your debugging assistant seamlessly across any target codebase on your local system:

PowerShell
bugray "My express server is crashing with JWT verification errors, investigate"
🧪 License
Distributed under the MIT License. See LICENSE for more details.


---

### 📤 Update GitHub with Your New README

Now that you've generated the file, push it straight up to your live remote page so your repository home looks professional:

```cmd
git add BUGRAY/README.md
git commit -m "docs: generate comprehensive modular overview readme for bugray engine"
git push origin main
