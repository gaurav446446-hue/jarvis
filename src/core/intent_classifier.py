"""Intent classifier for Jarvis AI."""
import re
from src.utils.constants import (
    INTENT_CONTROL,
    INTENT_QUERY,
    INTENT_GREETING,
    INTENT_CONTEXT,
    INTENT_EXPLAIN,
    INTENT_UNKNOWN,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Keyword patterns per intent
_PATTERNS = {
    INTENT_CONTROL: [
        r"\bturn (on|off)\b",
        r"\bswitch (on|off)\b",
        r"\bset fan\b",
        r"\bfan (speed|to|at)\b",
        r"\blight (on|off)\b",
        r"\bdim\b",
        r"\bbrighten\b",
        r"\bincrease fan\b",
        r"\bdecrease fan\b",
        r"\bstop fan\b",
        r"\bstart fan\b",
        r"\bpower (on|off)\b",
        r"\benable\b",
        r"\bdisable\b",
    ],
    INTENT_QUERY: [
        r"\bwhat('?s| is)\b",
        r"\bhow (hot|cold|warm|humid)\b",
        r"\btemperature\b",
        r"\bhumidity\b",
        r"\bwhat time\b",
        r"\bwhat day\b",
        r"\btell me\b",
        r"\bshow me\b",
        r"\bwhat are\b",
        r"\bstatus\b",
        r"\bhow (are|is)\b",
        r"\bcheck\b",
    ],
    INTENT_GREETING: [
        r"\b(good\s+)?(morning|evening|night|afternoon)\b",
        r"\bhello\b",
        r"\bhi\b",
        r"\bhey\b",
        r"\bwake up\b",
        r"\bjarvis\b",
    ],
    INTENT_CONTEXT: [
        r"\bi'?m (home|back|here|leaving|going|away|sleeping|awake)\b",
        r"\bi am (home|back|here|leaving|going|away|sleeping|awake)\b",
        r"\bleaving\b",
        r"\bgoing to sleep\b",
        r"\bbedtime\b",
        r"\bwoke up\b",
        r"\bjust woke\b",
        r"\barrive\b",
        r"\bdeparture\b",
    ],
    INTENT_EXPLAIN: [
        r"\bwhy (did|do|are|is)\b",
        r"\bexplain\b",
        r"\btell me about\b",
        r"\bhow (does|do|did)\b",
        r"\bwhat happened\b",
    ],
}


class IntentClassifier:
    """Rule-based intent classifier (Phase 1).

    Phase 2/3 will replace this with a trained scikit-learn model.
    """

    def classify(self, text: str) -> str:
        """Classify text into one of the defined intent categories."""
        if not text or not text.strip():
            return INTENT_UNKNOWN

        normalized = text.lower().strip()

        for intent, patterns in _PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    logger.debug("Intent '%s' matched pattern '%s'", intent, pattern)
                    return intent

        return INTENT_UNKNOWN

    def classify_with_confidence(self, text: str) -> tuple[str, float]:
        """Return (intent, confidence) tuple.

        Confidence is a simple heuristic based on pattern-match count.
        """
        if not text or not text.strip():
            return INTENT_UNKNOWN, 0.0

        normalized = text.lower().strip()
        scores: dict[str, int] = {intent: 0 for intent in _PATTERNS}

        for intent, patterns in _PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    scores[intent] += 1

        best_intent = max(scores, key=lambda k: scores[k])
        best_score = scores[best_intent]

        if best_score == 0:
            return INTENT_UNKNOWN, 0.0

        total = sum(scores.values())
        confidence = best_score / total if total > 0 else 0.0
        return best_intent, round(confidence, 2)
