from .rule_engine import analyze_risk


def check_sensitivity(text_entities, objects, faces, full_text=""):
    """
    Acts as the decision gate. Threshold is met if any visual
    or textual PII is detected.
    """
    has_visual_pii = bool(objects or faces)
    has_textual_pii = bool(text_entities)
    has_keyword_match = analyze_risk(full_text)

    # Logic expansion: Returns True if any sensitivity threshold is met
    return has_visual_pii or has_textual_pii or has_keyword_match