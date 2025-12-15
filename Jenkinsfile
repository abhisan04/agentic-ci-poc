#!/usr/bin/env python3
import os
import sys
from openai import OpenAI

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[Agent] ERROR: OPENAI_API_KEY is not set")
    sys.exit(1)

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def scan_file_with_llm(file_path):
    """Send code file to LLM and get PASS/FAIL decision."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    prompt = f"Scan this code for potential issues. Return only 'PASS' or 'FAIL'.\n{code}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        decision = response.choices[0].message.content.strip().upper()
        return decision
    except Exception as e:
        print(f"[Agent] ERROR calling LLM: {e}")
        return "FAIL"  # fail-safe

def scan_workspace(directory="."):
    """Scan all .py and .java files in the given directory."""
    issues = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py") or f.endswith(".java"):
                path = os.path.join(root, f)
                decision = scan_file_with_llm(path)
                if decision == "FAIL":
                    issues.append(path)
    return issues

# Scan the workspace provided as argument (default = current folder)
target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
issues = scan_workspace(target_dir)

if issues:
    print("[Agent] LLM detected issues in the following files:")
    for i in issues:
        print(" -", i)
    sys.exit(1)  # Fail Jenkins stage
else:
    print("[Agent] No issues detected ✅")
    sys.exit(0)  # Pass Jenkins stage
