import os
import sys
import json
import subprocess
import urllib.request

# --- Config ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"
MAX_OUTPUT_CHARS = 15000

# Command to run (customize later)
DYNAMIC_COMMAND = ["mvn", "test"]

if not OPENAI_API_KEY:
    print(json.dumps({
        "decision": "FAIL",
        "severity": "HIGH",
        "observations": [{
            "issue": "OPENAI_API_KEY not set",
            "impact": "Dynamic analysis could not run"
        }]
    }))
    sys.exit(0)

# --- Run Dynamic Command ---
try:
    process = subprocess.run(
        DYNAMIC_COMMAND,
        capture_output=True,
        text=True,
        timeout=300
    )
    output = (process.stdout + "\n" + process.stderr)[-MAX_OUTPUT_CHARS:]
except Exception as e:
    print(json.dumps({
        "decision": "FAIL",
        "severity": "HIGH",
        "observations": [{
            "issue": "Dynamic command execution failed",
            "impact": str(e)
        }]
    }))
    sys.exit(0)

# --- LLM Prompt ---
prompt = f"""
You are a Dynamic Agent in an Agentic CI system.

The following is runtime / test execution output.
Determine if it represents real failures, flaky behavior, or acceptable warnings.

Respond STRICTLY in valid JSON only.

JSON FORMAT:
{{
  "decision": "PASS | FAIL",
  "severity": "LOW | MEDIUM | HIGH",
  "observations": [
    {{
      "issue": "<what went wrong>",
      "impact": "<why it matters>"
    }}
  ]
}}

Rules:
- FAIL only for real test failures or runtime errors
- Ignore flaky, retryable, or non-blocking warnings
- If output is clean, return PASS with empty observations

Output:
{output}
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
        "observations": [{
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
        "observations": [{
            "issue": "Invalid JSON returned by LLM",
            "impact": "Meta-agent cannot trust dynamic analysis"
        }]
    }

# --- Output ONLY JSON ---
print(json.dumps(parsed))

# Dynamic agent NEVER controls pipeline exit
sys.exit(0)
