# logic/rule_engine.py
import json
import os

DEFAULT_RULES = {"sensitive_keywords": ["secret", "password", "otp", "bank", "balance"]}
CONFIG_PATH = r"C:\pythonprojects\PythonProject2\config\privacy_rules.json"


def load_privacy_rules():
    if not os.path.exists(CONFIG_PATH): return DEFAULT_RULES
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data if "sensitive_keywords" in data else DEFAULT_RULES
    except:
        return DEFAULT_RULES


rules = load_privacy_rules()


def analyze_risk(full_text):
    """
    Scans text and predicts risk level based on keywords.
    """
    found_triggers = [w for w in rules["sensitive_keywords"] if w.lower() in full_text.lower()]

    if not found_triggers:
        return "🟢 LOW", "No sensitive keywords found.", found_triggers

    # Simple logic: more keywords = higher risk
    if len(found_triggers) > 3:
        return "🔴 HIGH", f"Found high-risk terms: {', '.join(found_triggers[:3])}...", found_triggers
    return "🟡 MEDIUM", f"Detected keywords: {', '.join(found_triggers)}", found_triggers