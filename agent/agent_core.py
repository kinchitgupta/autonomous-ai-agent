import requests
import json
import re
from agent.tools import TOOLS

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:3b"


# -------------------------
# BASIC CONVERSATION HANDLER
# -------------------------
def basic_conversation(task: str):
    msg = task.lower().strip()

    responses = {
        "hi": "Hello 👋",
        "hy": "Hello 👋",
        "hello": "Hi there 👋",
        "hey": "Hey 👋",
        "who made you": "I was built by Kinchit Gupta.",
        "who created you": "I was developed by Kinchit Gupta.",
        "what is your hobby": "I enjoy solving problems and assisting with development tasks.",
        "how are you": "I am functioning optimally.",
        "what is your name": "I am your Autonomous AI Agent.",
        "who are you": "I am an Autonomous AI Agent designed to execute tools intelligently."
    }

    for key in responses:
        if key in msg:
            return responses[key]

    return None


# -------------------------
# INPUT VALIDATION
# -------------------------
def is_invalid_input(task: str):
    task = task.strip()
    if not task:
        return True
    if re.fullmatch(r"[^\w\s]+", task):
        return True
    return False


# -------------------------
# ⚡ FAST RULE-BASED ROUTING
# Bypasses LLM entirely for deterministic tasks
# -------------------------
VOWEL_PATTERNS    = [r"count vowels?\s+in\b", r"how many vowels?\s+in\b", r"vowels?\s+count"]
DIGIT_PATTERNS    = [r"count digits?\s+in\b", r"how many digits?\s+in\b", r"digits?\s+count"]
WORD_PATTERNS     = [r"count words?\s+in\b", r"how many words?\s+in\b", r"word\s+count"]
PLAN_PATTERNS     = [r"\b(plan|roadmap|steps|strategy|guide)\b"]
SUMMARY_PATTERNS  = [r"\b(summarize|summary)\b"]
UPPER_PATTERNS    = [r"\b(uppercase|upper case|to upper)\b"]
LOWER_PATTERNS    = [r"\b(lowercase|lower case|to lower)\b"]
REVERSE_PATTERNS  = [r"\b(reverse)\b"]
PALINDROME_PATS   = [r"\b(palindrome)\b"]


def _match_any(patterns, text):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _extract_quoted_or_after(task: str, keywords: list[str]) -> str:
    """Pull text from quotes or after a keyword like 'in '."""
    quoted = re.findall(r'["\'](.+?)["\']', task)
    if quoted:
        return quoted[0]
    for kw in keywords:
        m = re.search(rf"{kw}\s+(.+)", task, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return task


def fast_route(task: str):
    """
    Returns (tool_name, tool_input) if a rule matches, else None.
    No LLM involved — instant response.
    """
    t = task.strip()


    if re.fullmatch(r"[0-9.+\-*/()\s]+", t):
        return "calculator", t


    calc_match = re.search(
        r"(calculate|compute|what is|evaluate|solve)\s+([\d\s\+\-\*\/\(\)\.]+)",
        t, re.IGNORECASE
    )
    if calc_match:
        expr = calc_match.group(2).strip()
        return "calculator", expr


    if _match_any(VOWEL_PATTERNS, t):
        return "count_vowels", _extract_quoted_or_after(t, ["in", "of"])


    if _match_any(DIGIT_PATTERNS, t):
        return "count_digits", _extract_quoted_or_after(t, ["in", "of"])


    if _match_any(WORD_PATTERNS, t):
        return "word_count", _extract_quoted_or_after(t, ["in", "of"])


    if _match_any(SUMMARY_PATTERNS, t):
        text = _extract_quoted_or_after(t, ["summarize", "summary of"])
        return "summarize", text


    if _match_any(PLAN_PATTERNS, t):
        return "planner", t


    if _match_any(UPPER_PATTERNS, t):
        return "to_uppercase", _extract_quoted_or_after(t, ["uppercase", "upper"])
    if _match_any(LOWER_PATTERNS, t):
        return "to_lowercase", _extract_quoted_or_after(t, ["lowercase", "lower"])
    if _match_any(REVERSE_PATTERNS, t):
        return "reverse_text", _extract_quoted_or_after(t, ["reverse"])
    if _match_any(PALINDROME_PATS, t):
        return "is_palindrome", _extract_quoted_or_after(t, ["is", "check"])

    return None


# -------------------------
# LLM CALL (single-shot)
# -------------------------
def ask_llm(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0,
                    "num_predict": 120,   # tighter = faster
                    "num_ctx": 512,        # reduced context window = faster
                    "num_thread": 8
                }
            },
            timeout=90
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except Exception as e:
        return json.dumps({"type": "final", "answer": f"LLM Error: {str(e)}"})


# -------------------------
# AGENT LOOP
# -------------------------
def run_agent(task: str):


    convo_reply = basic_conversation(task)
    if convo_reply:
        return {"plan": ["Conversation"], "observations": [], "result": convo_reply}

    # ── 2. Input validation ──
    if is_invalid_input(task):
        return {
            "plan": ["Invalid input"],
            "observations": [],
            "result": "Please provide a meaningful request."
        }


    fast = fast_route(task)
    if fast:
        tool_name, tool_input = fast
        tool_func = TOOLS.get(tool_name)
        if tool_func:
            result = tool_func(tool_input)
            return {
                "plan": [f"Fast route → {tool_name}"],
                "observations": [result],
                "result": result
            }


    prompt = f"""You are a tool-dispatching agent. Respond ONLY in valid JSON.

Task: {task}

If the task needs a tool, respond:
{{"type":"action","tool":"tool_name","input":"input_text"}}

If you can answer directly (factual/general knowledge), respond:
{{"type":"final","answer":"short answer in max 2 lines"}}

Available tools: {list(TOOLS.keys())}

Rules:
- calculator → math expressions
- planner → when user asks for steps, plan, roadmap
- summarize → when user asks to summarize text
- count_vowels / count_digits / word_count → counting tasks
- Do NOT use a tool for general knowledge questions

JSON only. No explanation."""

    llm_output = ask_llm(prompt)


    try:
        parsed = json.loads(llm_output)
    except json.JSONDecodeError:
        # Try to extract JSON substring
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
            except Exception:
                return {"plan": [], "observations": [], "result": "Could not parse agent response."}
        else:
            return {"plan": [], "observations": [], "result": "Could not parse agent response."}


    if parsed.get("type") == "action":
        tool_name  = parsed.get("tool", "")
        tool_input = parsed.get("input", "")
        tool_func  = TOOLS.get(tool_name)

        if tool_func:
            tool_result = tool_func(tool_input)
            return {
                "plan": [f"Tool: {tool_name}"],
                "observations": [tool_result],
                "result": tool_result
            }


    if parsed.get("type") == "final":
        answer = parsed.get("answer", "")
        answer = "\n".join(answer.split("\n")[:2])
        return {"plan": [], "observations": [], "result": answer}


    return {"plan": [], "observations": [], "result": "I couldn't process that request."}