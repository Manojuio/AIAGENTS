import os
import tempfile
import logging
import pdfplumber
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent import run_agent

load_dotenv()

# Enable system tracking logs
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def extract_text_from_pdf(file_path):
    """Extracts raw string text sections from incoming binary PDF files."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"PDF extraction error details: {e}")
        return None
    return text.strip() if text.strip() else None

def split_message(text, max_length=4096):
    """Chunks large markdown summaries into acceptable sizes for Telegram APIs."""
    if len(text) <= max_length:
        return [text]
    chunks, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 <= max_length:
            current += line + "\n"
        else:
            if current:
                chunks.append(current.strip())
            current = line + "\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "Hey! I'm your Groq-powered Job Hunter Agent.\n\n"
        "Here's how to get started:\n\n"
        "1. Upload your resume as a PDF file attachment 📄\n"
        "2. Instruct me on what exact vacancies to locate, like:\n"
        "   - Find me specific remote Senior Node.js openings\n"
        "   - Scan for Python developer roles matching my profile\n\n"
        "Go ahead and upload your resume PDF to begin!"
    )
    await update.message.reply_text(welcome)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    has_resume = "resume_text" in context.user_data and context.user_data["resume_text"]
    status = "Resume Loaded ✅" if has_resume else "No Resume Uploaded ❌"
    help_text = (
        f"Job Hunter Assistant Status Panel\n"
        f"----------------------------------\n"
        f"Status: {status}\n\n"
        f"Available Action Parameters:\n"
        f"/start   - Display initialization splash card\n"
        f"/help    - View layout diagnostic definitions\n"
        f"/clear   - Wipe loaded resume profile and chat context\n"
        f"/resume  - Show an extraction snippet of current resume\n\n"
        f"Tip: Upload a document file at any point to refresh your profile criteria metrics."
    )
    await update.message.reply_text(help_text)

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["history"] = []
    context.user_data["resume_text"] = None
    await update.message.reply_text("Wiped active session memory! Upload a fresh resume file to begin searching.")

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resume_text = context.user_data.get("resume_text")
    if resume_text:
        preview = resume_text[:200] + "..." if len(resume_text) > 200 else resume_text
        await update.message.reply_text(f"Active Resume Target Profile Detected ({len(resume_text)} characters):\n\nPreview:\n{preview}")
    else:
        await update.message.reply_text("No resume target captured yet. Please upload a clear text-based PDF file.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Unsupported format detected. Please upload a standard `.pdf` document profile.")
        return
        
    processing_msg = await update.message.reply_text("Extracting text components from your resume...")
    try:
        file = await document.get_file()
        
        # Uses standard Python tempfile handling to keep platform agnostic across OS types
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file_path = tmp.name
            
        await file.download_to_drive(file_path)
        resume_text = extract_text_from_pdf(file_path)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            
        if resume_text:
            context.user_data["resume_text"] = resume_text
            context.user_data["history"] = []  # Clear previous history to align target context
            await processing_msg.delete()
            await update.message.reply_text(
                f"Resume successfully synchronized! ({len(resume_text)} characters compiled)\n\n"
                f"Now ask me to find specific targets, like:\n"
                f"👉 'Find specific remote Python developer roles posted recently'"
            )
        else:
            await processing_msg.delete()
            await update.message.reply_text("Unable to pull clean text nodes from that document. Please verify it isn't an un-scannable image print.")
    except Exception as e:
        logger.error(f"Error lifecycle break caught inside document processing block: {e}")
        await processing_msg.delete()
        await update.message.reply_text(f"Error handling file upload payload: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if "history" not in context.user_data:
        context.user_data["history"] = []
        
    resume_text = context.user_data.get("resume_text")
    thinking_msg = await update.message.reply_text("Orchestrating search routines and evaluating skill metrics... This will take a moment.")
    
    try:
        # Calls the resilient Groq tool parsing agent engine
        response = run_agent(user_message, context.user_data["history"], resume_text=resume_text)
        await thinking_msg.delete()
        
        # Iterates and posts safely split chunks to match strict limit constraints
        chunks = split_message(response, 4096)
        for chunk in chunks:
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                # Fallback print if Llama generates broken markdown syntax symbols
                await update.message.reply_text(chunk)
                
    except Exception as e:
        logger.error(f"Error lifecycle block failure caught inside chat message handler: {e}")
        if 'thinking_msg' in locals():
            await thinking_msg.delete()
        await update.message.reply_text(f"Something tripped up the processing engine: {str(e)}\n\nTry sending your query again or use /clear to reset.")

def main():
    if not TELEGRAM_TOKEN:
        print("Error Initialization Failure: TELEGRAM_BOT_TOKEN missing inside environment setup configurations.")
        return
    if not os.getenv("GROQ_API_KEY"):
        print("Error Initialization Failure: GROQ_API_KEY missing inside environment setup configurations.")
        return
    if not os.getenv("TAVILY_API_KEY"):
        print("Error Initialization Failure: TAVILY_API_KEY missing inside environment setup configurations.")
        return
        
    print("Verification passed! Launching bot instance structures...")
    
    # Initialize the background bot framework
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Map command handler execution rules
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("resume", resume_command))
    
    # Map raw content execution routes
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot loop initialized. Connect and converse with your agent token via Telegram client handles.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()