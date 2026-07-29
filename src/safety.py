import re
from typing import Tuple, Dict, Any

# Common adversarial prompt patterns & injection triggers
ADVERSARIAL_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+(instructions|prompts)",
    r"disregard\s+(your\s+)?(system\s+)?prompt",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"system\s*:\s*",
    r"you\s+are\s+now\s+a\s+DAN",
    r"jailbreak",
]

def check_prompt_safety(query: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Scans incoming query for adversarial attacks or system prompt injection.
    
    Returns:
        (is_safe: bool, fallback_response: Dict[str, Any] or None)
    """
    normalized_query = query.lower().strip()
    
    for pattern in ADVERSARIAL_PATTERNS:
        if re.search(pattern, normalized_query, re.IGNORECASE):
            fallback_response = {
                "category": "General",
                "answer": "Security Policy Alert: The query contained restricted instructions or potential prompt injection and cannot be processed.",
                "confidence": 0.0,
                "rationale": f"Adversarial pattern detected matching security trigger: '{pattern}'",
                "actions": ["Log security violation", "Reject adversarial query", "Flag user IP/session"]
            }
            return False, fallback_response
            
    return True, None
