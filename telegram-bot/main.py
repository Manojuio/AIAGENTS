import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- Global storage for the latest news ----------
last_news = None

# ---------- Tool 1: Fetch news ----------
def fetch_news(query, num_results=5):
    global last_news
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return "Error: NEWS_API_KEY not set."

    url = f"https://newsapi.org/v2/everything?q={query}&pageSize={num_results}&apiKey={api_key}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            return f"API error: {data.get('message')}"
        articles = data.get("articles", [])
        if not articles:
            return f"No news found for '{query}'."

        # Build a nicely formatted string
        lines = [f"Top {len(articles)} news about '{query}':\n"]
        for i, art in enumerate(articles, 1):
            title = art.get("title", "No title")
            desc = art.get("description", "No description")
            link = art.get("url", "")
            lines.append(f"{i}. {title}")
            lines.append(f"   {desc}")
            lines.append(f"   {link}\n")
        result = "\n".join(lines).strip()
        last_news = result
        print("News "+result)   # store for later sending
        return result
    except Exception as e:
        return f"Error fetching news: {e}"

# ---------- Tool 2: Send Telegram message ----------
def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return "Error: Telegram credentials missing."
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return "Message sent successfully to Telegram."
    except Exception as e:
        return f"Telegram error: {e}"

# ---------- Tool definitions (JSON) ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_news",
            "description": "Fetch recent news articles about a given topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Topic to search for (e.g., 'war', 'technology')"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of articles to return (default 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_telegram_message",
            "description": "Send a text message to a Telegram chat.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message content to send"
                    }
                },
                "required": ["message"]
            }
        }
    }
]

# ---------- Agent loop ----------
def run_agent(user_input):
    global last_news

    # Quick fallback: if the user explicitly says "send to telegram" and we have stored news,
    # send it directly without involving the LLM. This guarantees the sending works.
    if any(word in user_input.lower() for word in ["send", "telegram"]) and last_news:
        result = send_telegram_message(last_news)
        return f"{result}\n\nHere is the news that was sent:\n{last_news}"

    messages = [
       {"role": "system", "content": (
    "You are an AI assistant with two tools: fetch_news and send_telegram_message.\n\n"
    "**Rules:**\n"
    "- If the user asks for news, call fetch_news with the appropriate query. After you get the result, simply show it to the user. Do NOT call send_telegram_message unless the user explicitly says 'send' or 'telegram'.\n"
    "- If the user asks to send news to Telegram (e.g., 'send that to telegram'), then call send_telegram_message with the full news content (the same text you previously displayed) as the message.\n"
    "- Never call send_telegram_message on your own.\n"
)},
        {"role": "user", "content": user_input}
    ]

    max_iterations = 5
    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # reliable model for tool calling
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        # If no tool call, this is the final answer
        if not msg.tool_calls:
            return msg.content

        # There may be multiple tool calls; handle the first one for simplicity
        tool_call = msg.tool_calls[0]
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        # Execute the tool
        if func_name == "fetch_news":
            result = fetch_news(args["query"], args.get("num_results", 5))
        elif func_name == "send_telegram_message":
            result = send_telegram_message(args["message"])
        else:
            result = f"Unknown tool: {func_name}"

        # Append assistant's tool call message and the tool result
        messages.append(msg)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    return "Max iterations reached without final answer."

# ---------- Main interaction loop ----------
def main():
    print("Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
        answer = run_agent(user_input)
        print(f"Agent: {answer}")

if __name__ == "__main__":
    main()