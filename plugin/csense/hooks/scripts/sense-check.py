import os
import json
import datetime
import sys
import re

# Set encoding to UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_config():
    config_path = os.path.expanduser("~/.csense/conscience/config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"mode": "observe"}

def log_action(record):
    log_path = os.path.expanduser("~/.csense/conscience/logs/action-log.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + "\n")

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"decision": "approve"}))
            return
            
        data = json.loads(input_data)
        tool_name = data.get("tool_name", "Unknown")
        tool_input = data.get("tool_input", {})
        
        # Stringify input for regex checking
        input_str = json.dumps(tool_input)
        
        config = get_config()
        mode = config.get("mode", "observe")
        
        decision = "ALLOW"
        reasoning = "Fits identity, no concerns."
        risk_level = "low"
        cited_sources = []
        
        # Rule 6: Tone check (Founder Frank)
        banned_phrases = ["synergy", "leverage", "paradigm shift", "stakeholders", "ecosystem", "unprecedented", "circle back", "huddle", "let's unpack", "deep dive"]
        found_phrases = [p for p in banned_phrases if p.lower() in input_str.lower()]
        
        if found_phrases:
            decision = "REWRITE_ACTION"
            reasoning = f"Tone inconsistency: contains banned phrases {found_phrases}. Violates Governor Rule 6."
            risk_level = "low"
            cited_sources = ["governor/rules.md#rule-6"]
        
        # Rule: Force push
        if "push" in input_str and "--force" in input_str:
            decision = "BLOCK"
            reasoning = "Force-pushing to main branch is strictly forbidden. Violates Governor Rule 2."
            risk_level = "high"
            cited_sources = ["governor/rules.md#rule-2"]
            
        # Rule: DUMMY word (for testing)
        if "DUMMY" in input_str:
            decision = "BLOCK"
            reasoning = "The word 'DUMMY' is forbidden in all project files. Violates Governor Rule 4."
            risk_level = "medium"
            cited_sources = ["governor/rules.md#rule-4"]

        # Rule: Paid infra
        if any(x in input_str.lower() for x in ["gpu", "ec2", "instance", "provision"]):
            decision = "REQUIRE_APPROVAL"
            reasoning = "Spinning up paid infrastructure requires explicit approval. Violates Governor Rule 3."
            risk_level = "high"
            cited_sources = ["governor/rules.md#rule-3"]

        record = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "tool": tool_name,
            "decision": decision,
            "riskLevel": risk_level,
            "confidence": 1.0,
            "reasoning": reasoning,
            "citedSources": cited_sources,
            "actionSummary": input_str[:100] + "..." if len(input_str) > 100 else input_str,
            "mode": mode,
            "enforced": False # Observe mode
        }
        
        log_action(record)
        
        # In Phase 1a Observe Mode, always return approve
        print(json.dumps({"decision": "approve"}))

    except Exception as e:
        # Never crash the session
        print(json.dumps({"decision": "approve", "reasoning": f"hook error: {str(e)}"}))

if __name__ == "__main__":
    main()
