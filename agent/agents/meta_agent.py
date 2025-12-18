import json
import subprocess
import sys
import os

# --- Helper ---
def is_blocking(signal):
    """Returns True if the signal indicates HIGH severity failure"""
    return signal.get("decision") == "FAIL" and signal.get("severity") == "HIGH"

# --- Base directory (where this file lives) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_static_agent():
    """Run LLM-based static agent and return parsed JSON"""
    print("\n🧠 Running Static LLM Agent...")
    static_path = os.path.join(BASE_DIR, "static_agent.py")
    repo_root = os.path.join(BASE_DIR, "../..")

    try:
        # Capture stdout so we can parse JSON
        output = subprocess.check_output(
            ["python3", static_path, repo_root],
            text=True,
            stderr=subprocess.STDOUT
        )
        print(f"Static agent raw output:\n{output}")
        result = json.loads(output)
        print(f"✅ Static Agent Decision: {result.get('decision')} | Severity: {result.get('severity')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Static Agent subprocess failed: {e.output}")
        result = {"decision": "FAIL", "severity": "HIGH",
                  "issues": [{"file": "static_agent.py", "line": "N/A", "issue": "Subprocess failed", "impact": e.output}]}
    except Exception as e:
        print(f"❌ Static Agent unexpected error: {e}")
        result = {"decision": "FAIL", "severity": "HIGH",
                  "issues": [{"file": "static_agent.py", "line": "N/A", "issue": "Unexpected error", "impact": str(e)}]}

    return result

def run_dynamic_agent():
    """Run dynamic agent and return parsed JSON"""
    print("\n⚙️ Running Dynamic Agent...")
    dynamic_path = os.path.join(BASE_DIR, "dynamic_agent.py")

    try:
        output = subprocess.check_output(
            ["python3", dynamic_path],
            text=True,
            stderr=subprocess.STDOUT
        )
        print(f"Dynamic agent raw output:\n{output}")
        result = json.loads(output)
        print(f"✅ Dynamic Agent Decision: {result.get('decision')} | Severity: {result.get('severity')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Dynamic Agent subprocess failed: {e.output}")
        result = {"decision": "FAIL", "severity": "HIGH", "observations": [{"issue": "Subprocess failed", "impact": e.output}]}
    except Exception as e:
        print(f"❌ Dynamic Agent unexpected error: {e}")
        result = {"decision": "FAIL", "severity": "HIGH", "observations": [{"issue": "Unexpected error", "impact": str(e)}]}

    return result

def decide_next(static_signal):
    """Agentic decisioning logic"""
    if static_signal["decision"] == "FAIL":
        if static_signal["severity"] == "HIGH":
            return "STOP"
        else:
            return "RUN_DYNAMIC"

    if static_signal["severity"] in ["MEDIUM"]:
        return "RUN_DYNAMIC"

    return "SKIP_DYNAMIC"

def meta_agent():
    final_result = {}

    # Run static agent
    static_signal = run_static_agent()
    final_result["static"] = static_signal

    # Hard stop if static HIGH severity
    if is_blocking(static_signal):
        print("❌ Blocking due to HIGH severity from Static Agent")
        final_result["action"] = "STOP"
        final_result["final_decision"] = "FAIL"
        return final_result

    # Decide next action
    action = decide_next(static_signal)
    final_result["action"] = action
    print(f"➡️ Next action decided by meta-agent: {action}")

    # Run dynamic agent if needed
    if action == "RUN_DYNAMIC":
        dynamic_signal = run_dynamic_agent()
        final_result["dynamic"] = dynamic_signal

        # Hard stop if dynamic HIGH severity
        if is_blocking(dynamic_signal):
            print("❌ Blocking due to HIGH severity from Dynamic Agent")
            final_result["final_decision"] = "FAIL"
            return final_result

    # No blocking signals
    final_result["final_decision"] = "PASS"
    print("✅ Meta-agent final decision: PASS")
    return final_result

if __name__ == "__main__":
    result = meta_agent()
    print("\n--- Full Agent Result JSON ---")
    print(json.dumps(result, indent=2))

    # Exit code for Jenkins
    sys.exit(0 if result["final_decision"] == "PASS" else 1)
