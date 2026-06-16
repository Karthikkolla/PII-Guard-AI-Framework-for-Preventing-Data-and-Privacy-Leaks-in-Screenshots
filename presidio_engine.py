import os
import logging
import warnings

# --- 0. THE FORCE SILENCER ---
warnings.filterwarnings("ignore", category=UserWarning, module="presidio_analyzer")
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.context_aware_enhancers import LemmaContextAwareEnhancer

# --- 1. ROBUST CUSTOM PATTERNS ---
# OTP: Strictly 6 digits
otp_pattern = Pattern(name="otp_pattern", regex=r"\b\d{6}\b", score=0.6)

# Phone: Handles 10 digits with optional +91 or dashes
phone_pattern = Pattern(name="phone_pattern", regex=r"(\+91[\-\s]?)?[6-9]\d{9}\b", score=0.6)

# Account Number: Handles 9 to 18 digits with optional spaces/dashes
# This is broader to catch "Account No: 1234 5678 9012"
acct_pattern = Pattern(
    name="acct_pattern",
    regex=r"\b\d{4}[ \d\-]{5,14}\d\b",
    score=0.45
)

# --- 2. RECOGNIZERS WITH EXTENDED CONTEXT ---
otp_recognizer = PatternRecognizer(
    supported_entity="OTP",
    patterns=[otp_pattern],
    context=["code", "otp", "verify", "password"]
)

phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[phone_pattern],
    context=["mobile", "phone", "contact", "whatsapp"]
)

# Increased score via context is crucial for random-looking account numbers
finance_recognizer = PatternRecognizer(
    supported_entity="ACCOUNT_NUMBER",
    patterns=[acct_pattern],
    context=["account", "acc", "savings", "checking", "beneficiary", "statement", "number", "iban"]
)

# --- 3. NLP & CONTEXT ENHANCER CONFIG ---
# We use a LemmaContextAwareEnhancer to allow Presidio to find "Account" even if the text says "Accounts"
context_enhancer = LemmaContextAwareEnhancer(
    context_prefix_count=10, # Look 10 words BACK for keywords
    context_suffix_count=5   # Look 5 words FORWARD for keywords
)

model_path = os.path.abspath(r"C:\pythonprojects\final_sroie_model")

configuration = {
    "nlp_engine_name": "transformers",
    "models": [{"lang_code": "en", "model_name": {"spacy": "en_core_web_sm", "transformers": model_path}}],
}

provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

# --- 4. CLEAN REGISTRY & ANALYZER ---
registry = RecognizerRegistry()
registry.load_predefined_recognizers(languages=["en"])
registry.add_recognizer(otp_recognizer)
registry.add_recognizer(phone_recognizer)
registry.add_recognizer(finance_recognizer)

analyzer = AnalyzerEngine(
    nlp_engine=nlp_engine,
    registry=registry,
    context_aware_enhancer=context_enhancer, # <--- Added context enhancer
    default_score_threshold=0.35
)

def analyze_text(text):
    target_entities = [
        "ORGANIZATION", "LOCATION", "DATE_TIME", "PERSON",
        "OTP", "PHONE_NUMBER", "ACCOUNT_NUMBER", "FINANCIAL_DATA", "CREDIT_CARD"
    ]
    return analyzer.analyze(text=text, entities=target_entities, language="en")

print("🎯 SROIE Engine Optimized: Account Detection Window Expanded!")