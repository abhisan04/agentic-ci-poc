# codeB/agent/decision_agent.py
import sys
import os

target_repo = sys.argv[1] if len(sys.argv) > 1 else '.'

print(f"[Agent] Scanning repo at: {target_repo}")

issues = []

# Scan Python files for TODO
for root, dirs, files in os.walk(target_repo):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path) as file:
                for i, line in enumerate(file, 1):
                    if "TODO" in line:
                        issues.append(f"{path}:{i} contains TODO")

if issues:
    print("[Agent] Found issues:")
    for issue in issues:
        print(issue)
    sys.exit(1)  # fail the pipeline
else:
    print("[Agent] No issues found ✅")
    sys.exit(0)  # continue
