import json
import subprocess
import sys

def is_blocking(signal):
    """Returns True if the signal indicates HIGH severity failure"""
    return signal.get("decision") == "FAIL" and signal.get("severity") == "HIGH"

def run_static_agent():
    """Run LLM-based static agent and return parsed JSON"""
    print("🧠 Running Static LLM Agent...")
    output = subprocess.check_output(
        ["python3", "static_agent.py", "."],
        text=True
    )
    return json.loads(output)

def run_dynamic_agent():
    """Run dynamic agent and return parsed JSON"""
    print("⚙️ Running Dynamic Agent...")
    output = subprocess.check_output(
        ["python3", "dynamic_agent.py"],
        text=True
    )
    return json.loads(output)

def decide_next(static_signal):
    """
    Agentic decisioning logic
    Determines whether dynamic checks should run
    """
    if static_signal["decision"] == "FAIL":
        if static_signal["severity"] == "HIGH":
            return "STOP"
        else:
            return "RUN_DYNAMIC"

    # Static PASS
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
        final_result["action"] = "STOP"
        final_result["final_decision"] = "FAIL"
        return final_result

    # Decide path
    action = decide_next(static_signal)
    final_result["action"] = action

    # Run dynamic agent if needed
    if action == "RUN_DYNAMIC":
        dynamic_signal = run_dynamic_agent()
        final_result["dynamic"] = dynamic_signal

        # Hard stop if dynamic HIGH severity
        if is_blocking(dynamic_signal):
            final_result["final_decision"] = "FAIL"
            return final_result

    # No blocking signals
    final_result["final_decision"] = "PASS"
    return final_result

if __name__ == "__main__":
    result = meta_agent()
    print(json.dumps(result, indent=2))

    # Single exit point for Jenkins
    sys.exit(0 if result["final_decision"] == "PASS" else 1)
