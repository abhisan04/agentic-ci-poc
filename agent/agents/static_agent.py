import os
import sys
import json
import urllib.request
import subprocess

# --- Config ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
MAX_CHARS = 20000

if not OPENAI_API_KEY:
    # Static agent must NOT fail pipeline
    print(json.dumps({
        "decision": "FAIL",
        "severity": "HIGH",
        "issues": [{
            "file": "system",
            "line": "N/A",
            "issue": "OPENAI_API_KEY not set",
            "impact": "LLM static analysis could not run"
        }]
    }))
    sys.exit(0)

target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

# Identify this agent file to exclude
AGENT_FILE = os.path.basename(__file__)

# --- Read code with exact line numbers ---
def read_code_with_lines(path, max_chars=MAX_CHARS):
    content = ""

    try:
        files = subprocess.check_output(
            ["git", "ls-files"],
            cwd=path,
            text=True
        ).splitlines()
    except Exception:
        return content

    for f in files:
        if f == AGENT_FILE:
            continue

        if f.endswith((".py", ".java")):
            content += f"\n### File: {f}\n"
            try:
                with open(os.path.join(path, f), "r", errors="ignore") as file:
                    for idx, line in enumerate(file, start=1):
                        content += f"{idx}: {line}"
                        if len(content) >= max_chars:
                            return content
            except Exception:
                pass

    return content


code = read_code_with_lines(target_dir)

# --- LLM Prompt (STRICT JSON) ---
prompt = f"""
You are a Static Agent in an Agentic CI system.

The code below INCLUDES EXACT LINE NUMBERS.
Use them precisely.

Respond STRICTLY in valid JSON only.
Do NOT include markdown, explanations, or extra text.

JSON FORMAT:
{{
  "decision": "PASS | FAIL",
  "severity": "LOW | MEDIUM | HIGH",
  "issues": [
    {{
      "file": "<filename>",
      "line": "<exact line number>",
      "issue": "<what is wrong>",
      "impact": "<why it matters>"
    }}
  ]
}}

Rules:
- List ALL real issues (bugs, security, correctness)
- Do NOT fail for formatting or style
- If no issues exist, return decision PASS, severity LOW, issues []

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

# --- Call OpenAI API ---
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
    print(json.dumps({
        "decision": "FAIL",
        "severity": "HIGH",
        "issues": [{
            "file": "llm",
            "line": "N/A",
            "issue": "LLM call failed",
            "impact": str(e)
        }]
    }))
    sys.exit(0)

# --- Parse & Guardrail ---
try:
    parsed = json.loads(reply)
except Exception:
    parsed = {
        "decision": "FAIL",
        "severity": "HIGH",
        "issues": [{
            "file": "llm",
            "line": "N/A",
            "issue": "Invalid JSON returned by LLM",
            "impact": "Meta-agent cannot trust this analysis"
        }]
    }

# --- Output ONLY JSON ---
print(json.dumps(parsed))

# Static agent NEVER controls pipeline exit
sys.exit(0)
