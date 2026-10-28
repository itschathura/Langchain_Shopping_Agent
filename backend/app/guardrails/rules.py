import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class RuleCheckResult:
    passed: bool
    reason: Optional[str] = None
    redirect_message: Optional[str] = None


# Patterns for prompt injection and system jailbreaks
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|prompts)",
    r"forget\s+(everything|all)\s+you\s+(were\s+told|know)",
    r"(reveal|show|print|display|tell\s+me)\s+(your\s+)?(system\s+prompt|initial\s+instructions|instructions)",
    r"you\s+are\s+now\s+(in\s+)?(DAN|developer|jailbreak|unrestricted)\s+mode",
    r"act\s+as\s+(an?\s+)?unfiltered|jailbroken",
    r"bypass\s+(all\s+)?(safety|guardrail|security|content)\s+filters?",
    r"do\s+anything\s+now",
]

# Patterns for blatantly off-topic non-shopping intents
OFF_TOPIC_PATTERNS = [
    # Creative writing
    r"\b(write|compose|generate)\s+(a\s+)?(poem|poetry|sonnet|haiku|limerick|bedtime\s+story|song|rap|novel|essay)\b",
    r"\btell\s+me\s+a\s+(bedtime\s+)?story\b",
    # Coding & technical execution
    r"\b(write|generate|debug|fix)\s+(some\s+)?(python|javascript|typescript|c\+\+|java|rust|sql|html|css|code|script)\b",
    r"\b(binary\s+search|leetcode|reverse\s+a\s+linked\s+list|fibonacci|bubble\s+sort)\b",
    # Weather queries
    r"\b(what('s|\s+is)\s+the\s+weather|weather\s+forecast|is\s+it\s+raining|temperature\s+in)\b",
    # General trivia / homework
    r"\b(who\s+was|who\s+is)\s+(the\s+)?(president|prime\s+minister|king|queen)\s+of\b",
    r"\bwhat\s+is\s+the\s+capital\s+of\b",
]

COMPILED_INJECTION_REGEX = [
    re.compile(p, re.IGNORECASE | re.MULTILINE) for p in PROMPT_INJECTION_PATTERNS
]
COMPILED_OFF_TOPIC_REGEX = [
    re.compile(p, re.IGNORECASE | re.MULTILINE) for p in OFF_TOPIC_PATTERNS
]


def check_input_rules(query: str) -> RuleCheckResult:
    """Fast, zero-cost (< 1ms, $0) regex rule filter.
    
    Checks for:
    1. Prompt injection / jailbreaks
    2. Blatantly off-topic requests (poems, coding, weather, history)
    """
    clean_query = query.strip()
    if not clean_query:
        return RuleCheckResult(
            passed=False,
            reason="empty_query",
            redirect_message="Hello! I'm your grocery shopping assistant. How can I help you find groceries today?",
        )

    # 1. Check prompt injection
    for pattern in COMPILED_INJECTION_REGEX:
        if pattern.search(clean_query):
            return RuleCheckResult(
                passed=False,
                reason="prompt_injection_detected",
                redirect_message=(
                    "I am an e-commerce grocery shopping assistant. I cannot modify my system instructions, "
                    "but I'd love to help you find food, snacks, pantry items, or check your past orders."
                ),
            )

    # 2. Check blatant off-topic intents
    for pattern in COMPILED_OFF_TOPIC_REGEX:
        if pattern.search(clean_query):
            return RuleCheckResult(
                passed=False,
                reason="off_topic_query",
                redirect_message=(
                    "I am dedicated to helping you with grocery shopping, food products, and your order receipts. "
                    "Could I assist you with finding any grocery or pantry items instead?"
                ),
            )

    return RuleCheckResult(passed=True)

