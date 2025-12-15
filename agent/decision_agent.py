#!/usr/bin/env python3
import os
import sys
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")  # set in Jenkins

def scan_code_llm(directory="."):
    issues = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py") or f.endswith(".java"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as file:
                    code = file.read()
                    prompt = f"Scan this code and return 'PASS' or 'FAIL' only:\n{code}"
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0
                    )
                    decision = response.choices[0].message.content.strip()
                    if decision.upper() == "FAIL":
                        issues.append(f"{path} flagged by LLM")
    return issues

target_dir = sys.argv[1] if len(sys.argv) > 1 else "."

issues = scan_code_llm(target_dir)

if issues:
    print("[Agent] Issues found by LLM:")
    for i in issues:
        print(" -", i)
    sys.exit(1)  # fail pipeline
else:
    print("[Agent] No issues ✅")
    sys.exit(0)
