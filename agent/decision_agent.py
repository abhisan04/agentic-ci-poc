import os
import sys
import json
import urllib.request

# --- Config ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
MAX_CHARS = 6000

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not set")
    sys.exit(1)

target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

# 🔹 Identify this agent file to exclude
AGENT_FILE = os.path.basename(__file__)

# --- Read code with exact line numbers ---
def read_code_with_lines(path, max_chars=MAX_CHARS):
    content = ""
    for root, _, files in os.walk(path):
        for f in files:
            # 🔹 EXCLUDE decision_agent.py (self)
            if f == AGENT_FILE:
                continue

            if f.endswith((".py", ".java")):
                file_path = os.path.join(root, f)
                content += f"\n### File: {f}\n"
                try:
                    with open(file_path, "r", errors="ignore") as file:
                        for idx, line in enumerate(file, start=1):
                            content += f"{idx}: {line}"
                            if len(content) >= max_chars:
                                return content
                except Exception:
                    pass
    return content

code = read_code_with_lines(target_dir)

# --- LLM Prompt ---
prompt = f"""
You are an Agentic CI Code Reviewer.

The code below INCLUDES EXACT LINE NUMBERS.
Use them precisely.

Respond STRICTLY in this format:

DECISION: PASS or FAIL
FINDINGS:
- File: <filename>
  Line: <exact line number>
  Issue: <what is wrong>
  Impact: <why it matters>

Fail ONLY for real issues (bugs, security, correctness).
Do NOT fail for formatting or style.

Code:
{code}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0
}

# --- Call OpenAI API (no SDK) ---
request = urllib.request.Request(
    url="https://api.openai.com/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read())
        reply = result["choices"][0]["message"]["content"]
except Exception as e:
    print("❌ LLM call failed:", e)
    sys.exit(1)

# --- Output ---
print("\n🤖 LLM RESPONSE")
print("--------------------------------------------------")
print(reply)
print("--------------------------------------------------")

# --- Enforce decision ---
if "DECISION: FAIL" in reply.upper():
    sys.exit(1)

sys.exit(0)
