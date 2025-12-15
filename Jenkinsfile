import os
import sys
import json
import urllib.request

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not set")
    sys.exit(1)

target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

def read_code_snippet(path, max_chars=4000):
    content = ""
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith((".py", ".java")):
                try:
                    with open(os.path.join(root, f), "r", errors="ignore") as file:
                        content += f"\n### File: {f}\n"
                        content += file.read(max_chars)
                except:
                    pass
    return content[:max_chars]

code = read_code_snippet(target_dir)

prompt = f"""
You are a CI code review agent.
Scan the following code and answer ONLY with:
- FAIL if there are critical issues
- PASS if code looks acceptable

Code:
{code}
"""

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "temperature": 0
}

req = urllib.request.Request(
    url="https://api.openai.com/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        decision = result["choices"][0]["message"]["content"].strip()
except Exception as e:
    print("❌ LLM call failed:", e)
    sys.exit(1)

print(f"🤖 Agent decision: {decision}")

if "FAIL" in decision.upper():
    sys.exit(1)

sys.exit(0)
