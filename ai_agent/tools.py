# -------------------------
# Calculator Tool
# -------------------------
def calculator(expression: str):
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid expression"


# -------------------------
# Exact 5-Line Summarizer
# -------------------------
def summarize(text: str):
    text = text.strip()

    sentences = text.replace("\n", " ").split(". ")

    clean = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if not s.endswith("."):
            s += "."
        clean.append(s)

    if len(clean) <= 5:
        return "\n".join(clean)

    return "\n".join(clean[:5])


# -------------------------
# Planner Tool
# -------------------------
def planner(problem: str):
    # simple dynamic planner logic
    base_steps = [
        f"Understand the goal: {problem}",
        "List required resources and constraints",
        "Break into actionable steps",
        "Execute and review progress"
    ]

    # ensure max 4 points only
    steps = base_steps[:4]

    return "\n".join([f"* {s}" for s in steps])


# -------------------------
# Count Vowels Tool
# -------------------------
def count_vowels(text: str):
    vowels = "aeiouAEIOU"
    count = sum(1 for char in text if char in vowels)
    return f"Vowel count: {count}"


# -------------------------
# Count Digits Tool
# -------------------------
def count_digits(text: str):
    count = sum(1 for char in text if char.isdigit())
    return f"Digit count: {count}"

def word_count(text: str):
    words = text.strip().split()
    return f"Word count: {len(words)}"
# -------------------------
# TOOL REGISTRY
# -------------------------
TOOLS = {
    "calculator": calculator,
    "summarize": summarize,
    "planner": planner,
    "count_vowels": count_vowels,
    "word_count": word_count,
    "count_digits": count_digits
}
