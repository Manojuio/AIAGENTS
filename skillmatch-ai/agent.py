import os
import json
import requests
from datetime import datetime 
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import tiktoken

load_dotenv()

# --- Context Window Constants ---
MAX_CONTEXT_TOKENS = 131072  # Llama 3.3 128k context window limit

_groq_client = None
_tavily_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _groq_client

def get_tavily_client():
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily_client

def calculate_tokens(messages: list) -> int:
    """Accurately calculates total tokens in the message payload."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception:
        encoding = tiktoken.get_encoding("gpt-4")
        
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # Message formatting overhead
        
        if isinstance(message, dict):
            for key, value in message.items():
                if value:
                    num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += -1
        else:
            content = getattr(message, 'content', '') or ''
            role = getattr(message, 'role', '') or ''
            num_tokens += len(encoding.encode(str(content))) + len(encoding.encode(str(role)))
            
    num_tokens += 2  # Priming tokens
    return num_tokens

def get_system_prompt(resume_text=None):
    base_prompt = """You are a Job Hunter Agent. Your job is to help users find relevant job listings and prepare application materials.

When a user gives you a job search query, you follow this process:

STEP 0 - ANALYZE INTENT: If the user says something like "find jobs based on my resume" or "find jobs matching my skills" WITHOUT specifying a particular role, first use the extract_resume_keywords tool to identify their key skills, job titles, and industries from their resume. Then use those keywords to make 2-3 different search_jobs calls targeting different angles. If the user asks for a SPECIFIC role (like "find me AI engineer jobs"), skip this step and search directly.

STEP 1 - SEARCH: Use the search_jobs tool to find relevant job listings. If you extracted keywords from the resume, make 2-3 searches using different keyword combinations for broader coverage.

STEP 2 - READ: For the top 3-5 most promising results across all searches, use the read_job_posting tool to fetch the full job description from each URL. Skip URLs that look like job aggregator homepages.

STEP 3 - SCORE: For each job you successfully read, use the score_job_match tool to score it against the user's resume/profile.

STEP 4 - REPORT: Present a final ranked briefing. For EACH job include:
  - Job title and company
  - Link to the job posting (the actual URL)
  - Match score and why it's a good/bad fit
  - Key requirements from the posting
  - A short personalized cover letter draft (3-4 sentences)

IMPORTANT RULES:
- Always include the job posting URL/link for every job in the report.
- Always search first, then read, then score. Don't skip steps.
- If a URL fails to load, skip it and move to the next one.
- Be honest about match scores - don't inflate them.
- If no resume has been uploaded, tell the user to upload their resume as a PDF.
- CRITICAL FOR TOOL CALLING: When calling a tool, provide the tool name exactly as defined in the tools schema. Do not concatenate arguments into the tool name string. Provide the arguments purely within the designated parameters block.
"""
    if resume_text:
        base_prompt += f"\nUSER'S RESUME:\n---\n{resume_text}\n---\nUse this resume for scoring and cover letters.\n"
    else:
        base_prompt += "\nNOTE: No resume uploaded yet. Tell the user to upload their resume as a PDF.\n"
    return base_prompt

# --- Tool JSON Schemas for Groq ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "extract_resume_keywords",
            "description": "Extract key skills, job titles, and industries from the user's resume to generate smart job search queries. Use this FIRST when the user asks to find jobs based on my resume without specifying a particular role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "Key skills from the resume"},
                    "job_titles": {"type": "array", "items": {"type": "string"}, "description": "Relevant job titles based on experience"},
                    "industries": {"type": "array", "items": {"type": "string"}, "description": "Industries suited for"},
                    "experience_level": {"type": "string", "description": "junior, mid, senior, lead"}
                },
                "required": ["skills", "job_titles"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Search the web for job listings matching a query. Returns titles, snippets, and URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The job search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_job_posting",
            "description": "Fetch and read the full content of a job posting from its URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL of the job posting to read"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "score_job_match",
            "description": "Score how well a job matches the user's resume. Returns a score out of 100.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "required_skills": {"type": "array", "items": {"type": "string"}},
                    "user_skills": {"type": "array", "items": {"type": "string"}},
                    "nice_to_have_skills": {"type": "array", "items": {"type": "string"}},
                    "seniority_level": {"type": "string"},
                    "remote_friendly": {"type": "boolean"},
                    "job_type": {"type": "string"}
                },
                "required": ["job_title", "company", "required_skills", "user_skills"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# --- Core Tool Program Logic ---

def extract_resume_keywords(skills: list[str], job_titles: list[str], industries: list[str] = None, experience_level: str = "mid") -> str:
    search_queries = []
    for title in job_titles[:3]:
        search_queries.append(f"{title} remote 2026")
    if skills:
        top_skills = " ".join(skills[:3])
        search_queries.append(f"{top_skills} developer jobs remote")
    if industries:
        for industry in industries[:2]:
            search_queries.append(f"{job_titles[0] if job_titles else 'developer'} {industry} jobs")
    return json.dumps({
        "skills": skills, 
        "job_titles": job_titles, 
        "industries": industries or [], 
        "experience_level": experience_level, 
        "suggested_search_queries": search_queries
    }, indent=2)

def search_jobs(query: str) -> str:
    try:
        results = get_tavily_client().search(query=query + " job listing hiring", max_results=8, search_depth="advanced")
        formatted = []
        for r in results.get("results", []):
            formatted.append({"title": r.get("title", "No title"), "url": r.get("url", ""), "snippet": r.get("content", "")[:300]})
        return json.dumps(formatted, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})
    
def read_job_posting(url: str) -> str:
    try:
        result = get_tavily_client().extract(urls=[url])
        if result and result.get("results"):
            content = result["results"][0].get("raw_content", "")
            if len(content) > 4000:
                content = content[:4000] + "\n\n[Content truncated...]"
            return content if content else "Could not extract content from this URL."
        return "Could not extract content from this URL."
    except Exception as e:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            return resp.text[:4000]
        except Exception as e2:
            return f"Failed to read URL: {str(e2)}"

def score_job_match(job_title: str, company: str, required_skills: list[str], user_skills: list[str], nice_to_have_skills: list[str] = None, seniority_level: str = "mid", remote_friendly: bool = True, job_type: str = "full-time") -> str:
    skill_map = {
        "node js": "nodejs", "node": "nodejs", "node.js": "nodejs", "express js": "expressjs",
        "postgres": "postgresql", "postgresql": "postgresql", "mongo": "mongodb", "py": "python",
        "js": "javascript", "ts": "typescript",
    }

    def normalize(skill: str) -> str:
        skill = skill.lower().strip()
        return skill_map.get(skill, skill)

    user_skills_set = {normalize(skill) for skill in user_skills}
    required = [normalize(skill) for skill in required_skills]
    nice = [normalize(skill) for skill in (nice_to_have_skills or [])]

    default_weight = 5
    weights = {
        "python": 20, "java": 20, "javascript": 18, "typescript": 18,
        "nodejs": 15, "react": 15, "fastapi": 15, "django": 15,
        "spring boot": 15, "postgresql": 12, "mongodb": 12, "mysql": 10,
        "docker": 10, "aws": 12, "azure": 12, "git": 4,
    }

    matched_required = []
    missing_required = []
    total_weight = 0
    matched_weight = 0

    for skill in required:
        weight = weights.get(skill, default_weight)
        total_weight += weight
        if skill in user_skills_set:
            matched_required.append(skill)
            matched_weight += weight
        else:
            missing_required.append(skill)

    skill_score = ((matched_weight / total_weight) * 70 if total_weight > 0 else 0)

    critical_missing = 0
    for skill in required:
        if weights.get(skill, default_weight) >= 15 and skill not in user_skills_set:
            critical_missing += 1

    matched_nice = [s for s in nice if s in user_skills_set]
    nice_score = ((len(matched_nice) / len(nice)) * 5 if nice else 0)

    seniority_scores = {
        "entry": 10, "junior": 10, "mid": 8, "mid-level": 8,
        "senior": 5, "lead": 3, "staff": 2, "principal": 1,
    }
    experience_score = seniority_scores.get(seniority_level.lower(), 5)

    remote_score = 5 if remote_friendly else 2
    job_type_scores = {"full-time": 10, "contract": 8, "freelance": 8, "part-time": 6}
    job_type_score = job_type_scores.get(job_type.lower(), 5)

    total_score = skill_score + nice_score + experience_score + remote_score + job_type_score

    required_match_ratio = len(matched_required) / max(len(required), 1)
    if required_match_ratio < 0.5:
        total_score *= 0.5
    if critical_missing >= 2:
        total_score *= 0.6

    total_score = min(round(total_score), 100)

    return json.dumps({
        "score": total_score, "job_title": job_title, "company": company,
        "matched_skills": matched_required + matched_nice, "missing_skills": missing_required,
        "seniority_fit": seniority_level, "remote": remote_friendly, "job_type": job_type,
        "breakdown": {
            "required_skills": round(skill_score), "nice_to_have": round(nice_score),
            "experience_fit": experience_score, "remote_fit": remote_score, "job_type_fit": job_type_score,
            "critical_missing": critical_missing,
        },
    }, indent=2)

def get_datetime() -> str:
    now = datetime.now()
    return json.dumps({"date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M:%S"), "day": now.strftime("%A"), "formatted": now.strftime("%A, %B %d, %Y at %I:%M %p")})

TOOL_MAP = {
    "extract_resume_keywords": extract_resume_keywords,
    "search_jobs": search_jobs,
    "read_job_posting": read_job_posting,
    "score_job_match": score_job_match,
    "get_datetime": get_datetime
}

def run_agent(user_message, conversation_history=None, resume_text=None):
    if conversation_history is None:
        conversation_history = []

    client = get_groq_client()
    messages = [{"role": "system", "content": get_system_prompt(resume_text=resume_text)}]
    
    # Safely load background turns outside execution steps
    for turn in conversation_history:
        messages.append(turn)
        
    messages.append({"role": "user", "content": user_message})

    while True:
        # --- Programmatic Tracking of the Context Window Status ---
        current_tokens = calculate_tokens(messages)
        remaining_tokens = MAX_CONTEXT_TOKENS - current_tokens
        print(f"--- Context Monitor: Used {current_tokens:,} / Limit {MAX_CONTEXT_TOKENS:,} tokens. Remaining Window space: {remaining_tokens:,} tokens ---")

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.2
            )
            response_message = response.choices[0].message
            
        except json.JSONDecodeError as je:
            raise json.JSONDecodeError(f"JSON issues with structural response parsing: {str(je)}")
            
        except Exception as e:
            err_str = str(e)
            if "failed_generation" in err_str and "<function=" in err_str:
                print("  [System] Intercepted structural tool format error from Llama. Patching manually...")
                try:
                    raw_payload = err_str.split("<function=")[1].split("</function>")[0].strip()
                    func_name = raw_payload.split("{")[0].strip()
                    args_json_str = "{" + raw_payload.split("{", 1)[1]
                    function_args = json.loads(args_json_str)
                    
                    print(f"  Manually calling tool: {func_name}")
                    tool_func = TOOL_MAP.get(func_name)
                    
                    if tool_func:
                        functional_output = tool_func(**function_args)
                    else:
                        functional_output = json.dumps({"error": f"Unknown tool {func_name}"})
                        
                    fake_tool_id = "call_fallback_patch_" + datetime.now().strftime("%M%S")
                    
                    # FIXED: Use plain dictionaries instead of custom classes
                    fake_assistant_turn = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": fake_tool_id,
                                "type": "function",
                                "function": {
                                    "name": func_name,
                                    "arguments": args_json_str
                                }
                            }
                        ]
                    }
                    
                    messages.append(fake_assistant_turn)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": fake_tool_id,
                        "name": func_name,
                        "content": functional_output
                    })
                    continue
                except Exception as fallback_err:
                    raise Exception(f"Fallback parsing engine crashed: {str(fallback_err)}. Original error: {err_str}")
            else:
                raise e
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                print(f"  Calling tool: {function_name}")
                tool_func = TOOL_MAP.get(function_name)
                
                try:
                    function_args = json.loads(tool_call.function.arguments)
                    if tool_func:
                        functional_output = tool_func(**function_args)
                    else:
                        functional_output = json.dumps({"error": f"Unknown tool {function_name}"})
                except Exception as e:
                    functional_output = json.dumps({"error": str(e)})
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": functional_output
                })
        else:
            final_text = response_message.content
            
            # FIX: Ensure everything extracted into conversation_history is a primitive dict
            conversation_history.clear()
            for msg in messages[1:]: 
                role = None
                content = None
                
                if isinstance(msg, dict):
                    role = msg.get("role")
                    content = msg.get("content")
                elif hasattr(msg, 'role'):
                    role = msg.role
                    content = getattr(msg, 'content', '')
                
                # Strip raw tools/mock structures out of the saved session storage array
                if role in ["user", "assistant"] and content and isinstance(content, str):
                    conversation_history.append({
                        "role": str(role), 
                        "content": str(content)
                    })
                    
            conversation_history.append({"role": "assistant", "content": str(final_text)})
            return final_text

if __name__ == "__main__":
    print("Job Hunter Agent - Terminal Mode (Groq Powered)")
    print("Type your job search query (or 'quit' to exit)")
    history = []
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        if not user_input:
            continue
        print("\nThinking...\n")
        res = run_agent(user_input, history)
        print(f"\nAgent:\n{res}")