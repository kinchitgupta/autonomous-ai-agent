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
        "who made you": "I was built by Kinchit Gupta & Kanishk Bhatnagar.",
        "who created you": "I was developed by Kinchit Gupta & Kanishk Bhatnagar.",
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

    # only special characters
    if re.fullmatch(r"[^\w\s]+", task):
        return True

    # meaningless random long string without spaces
    if len(task) > 6 and " " not in task and task.isalpha():
        return True

    return False
# -------------------------
# LLM CALL
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
                    "num_predict": 150,
                    "num_ctx": 1024,
                    "num_thread": 8
                }
            },
            timeout=120
        )

        response.raise_for_status()
        return response.json().get("response", "").strip()

    except Exception as e:
        return json.dumps({
            "type": "final",
            "answer": f"LLM Error: {str(e)}"
        })


# -------------------------
# AGENT LOOP
# -------------------------
def run_agent(task: str):
    # -------- BASIC CONVERSATION --------
    convo_reply = basic_conversation(task)
    if convo_reply:
        return {
            "plan": ["Basic conversation handled"],
            "observations": [],
            "result": convo_reply
        }

    # -------- INVALID INPUT CHECK --------
    if is_invalid_input(task):
        return {
            "plan": ["Invalid input detected"],
            "observations": [],
            "result": "Unsupported or unclear input. Please provide a meaningful request."
        }

    # -------- BASIC CONVERSATION --------
    convo_reply = basic_conversation(task)
    if convo_reply:
        return {
            "plan": ["Basic conversation handled"],
            "observations": [],
            "result": convo_reply
        }

    # -------- FORCE CALCULATOR --------
    if re.fullmatch(r"[0-9.+\-*/()\s]+", task):
        tool_result = TOOLS["calculator"](task)
        return {
            "plan": ["Calculator tool forced"],
            "observations": [tool_result],
            "result": tool_result
        }

    # -------- PHASE 1: INTERNAL PLAN --------
    planning_prompt = f"""
Think step-by-step internally.
Create a short reasoning plan.
Do NOT give final answer.

Task:
{task}
"""
    hidden_plan = ask_llm(planning_prompt)

    # -------- PHASE 2: TOOL OR FINAL --------
    context = f"""
You already planned internally:

{hidden_plan}

Now produce final output.

Rules:
- Max 2 short lines in final answer
- No markdown
- Prefer tools over guessing

Tool rules:
- Use calculator for math
- Use planner ONLY when user asks for plan, roadmap, steps, points, or strategy
- Use summarize when user asks to summarize text
- Use count_vowels when user asks to count vowels
- Use count_digits when user asks to count digits
- Use count_consonants when user asks for consonant count
- Use word_count when user asks number of words
- Use char_count when user asks character count
- Use reverse_text when user asks to reverse text
- Use is_palindrome when user asks if text is palindrome
- Use to_uppercase / to_lowercase for case conversion
- Use normalize_spaces to clean extra spaces
- Do NOT call tools for simple factual questions

Respond ONLY valid JSON.

Tool call format:
{{
 "type": "action",
 "tool": "tool_name",
 "input": "input"
}}

Final answer format:
{{
 "type": "final",
 "answer": "two-line answer"
}}

Available tools:
{list(TOOLS.keys())}

Task:
{task}
"""

    llm_output = ask_llm(context)

    try:
        parsed = json.loads(llm_output)
    except:
        return {
            "plan": [],
            "observations": [],
            "result": "Model JSON error"
        }

    # -------- TOOL EXECUTION --------
    if parsed.get("type") == "action":
        tool_name = parsed.get("tool")
        tool_input = parsed.get("input", "")
        tool_func = TOOLS.get(tool_name)

        if tool_func:
            tool_result = tool_func(tool_input)

            followup_prompt = f"""
Tool result:
{tool_result}

Give final user answer in max 2 short lines.
Return JSON:
{{"type":"final","answer":"..."}}
"""
            final_out = ask_llm(followup_prompt)

            try:
                parsed_final = json.loads(final_out)
                final_answer = parsed_final.get("answer", tool_result)
            except:
                final_answer = tool_result

            return {
                "plan": [f"Tool used: {tool_name}"],
                "observations": [tool_result],
                "result": final_answer
            }

    # -------- FINAL ANSWER --------
    if parsed.get("type") == "final":
        result = parsed.get("answer", "")
        result = "\n".join(result.split("\n")[:2])

        return {
            "plan": [],
            "observations": [],
            "result": result
        }

    # -------- DEFAULT FALLBACK --------
    return {
        "plan": [],
        "observations": [],
        "result": "Invalid input. Please provide a meaningful request."
    }