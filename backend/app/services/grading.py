"""Server-side answer validation and grading.

The client renders feedback, but correctness is decided here so a learner cannot mark their own
answer correct and the analytics data stays trustworthy.
"""

from __future__ import annotations

from typing import Any

from app.core.errors import BadRequest
from app.models import Question, QuestionType

MAX_TEXT_LENGTH = 8000


class Graded:
    __slots__ = ("answer", "is_correct", "score", "feedback", "explanation", "correct_answer")

    def __init__(
        self,
        answer: dict[str, Any],
        is_correct: bool | None,
        score: float | None,
        feedback: str | None,
        explanation: str | None,
        correct_answer: Any | None,
    ) -> None:
        self.answer = answer
        self.is_correct = is_correct
        self.score = score
        self.feedback = feedback
        self.explanation = explanation
        self.correct_answer = correct_answer


def _option_values(spec: dict[str, Any]) -> list[str]:
    return [str(opt.get("value")) for opt in spec.get("options", []) if opt.get("value") is not None]


def _option_feedback(spec: dict[str, Any], value: str) -> str | None:
    for opt in spec.get("options", []):
        if str(opt.get("value")) == value:
            fb = opt.get("feedback")
            return str(fb) if fb else None
    return None


def grade(question: Question, answer: dict[str, Any]) -> Graded:
    """Validate the answer shape for the question type and compute correctness when defined."""
    spec = question.spec or {}
    qtype = QuestionType(question.type)
    explanation = spec.get("explanation")
    feedback: str | None = None
    is_correct: bool | None = None
    score: float | None = None
    correct_answer: Any | None = None

    if qtype is QuestionType.SINGLE_CHOICE:
        value = answer.get("value")
        if not isinstance(value, str) or not value:
            raise BadRequest("Select an option before submitting.", code="answer_invalid")
        valid = _option_values(spec)
        if valid and value not in valid:
            raise BadRequest("That option is not available for this question.", code="answer_invalid")
        expected = spec.get("correct")
        if isinstance(expected, str):
            is_correct = value == expected
            score = 1.0 if is_correct else 0.0
            correct_answer = expected
        feedback = _option_feedback(spec, value)
        answer = {"value": value}

    elif qtype is QuestionType.MULTI_CHOICE:
        values = answer.get("values")
        if not isinstance(values, list) or not values:
            raise BadRequest("Select at least one option.", code="answer_invalid")
        if len(values) > 20:
            raise BadRequest("Too many options selected.", code="answer_invalid")
        cleaned = [str(v) for v in values]
        valid = _option_values(spec)
        if valid and any(v not in valid for v in cleaned):
            raise BadRequest("One of those options is not available.", code="answer_invalid")
        expected = spec.get("correct")
        if isinstance(expected, list):
            expected_set = {str(v) for v in expected}
            chosen = set(cleaned)
            hits = len(chosen & expected_set)
            misses = len(chosen - expected_set)
            total = max(1, len(expected_set))
            score = max(0.0, (hits - misses) / total)
            is_correct = chosen == expected_set
            correct_answer = sorted(expected_set)
        answer = {"values": sorted(set(cleaned))}

    elif qtype is QuestionType.FREE_TEXT:
        text = answer.get("text")
        if not isinstance(text, str):
            raise BadRequest("A written response is required.", code="answer_invalid")
        text = text.strip()
        if len(text) > MAX_TEXT_LENGTH:
            raise BadRequest(
                f"Response is too long (max {MAX_TEXT_LENGTH} characters).", code="answer_too_long"
            )
        min_len = int(spec.get("minLength", 0))
        if len(text) < min_len:
            raise BadRequest(
                f"Please write at least {min_len} characters.", code="answer_too_short"
            )
        answer = {"text": text}

    elif qtype in (QuestionType.NUMERIC, QuestionType.SLIDER_ESTIMATE):
        raw = answer.get("value")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise BadRequest("A numeric answer is required.", code="answer_invalid")
        value = float(raw)
        lo, hi = spec.get("min"), spec.get("max")
        if isinstance(lo, (int, float)) and value < float(lo):
            raise BadRequest("Value is below the allowed range.", code="answer_out_of_range")
        if isinstance(hi, (int, float)) and value > float(hi):
            raise BadRequest("Value is above the allowed range.", code="answer_out_of_range")
        target = spec.get("correct")
        if isinstance(target, dict) and "min" in target and "max" in target:
            is_correct = float(target["min"]) <= value <= float(target["max"])
            score = 1.0 if is_correct else 0.0
            correct_answer = target
        elif isinstance(target, (int, float)):
            tolerance = float(spec.get("tolerance", 0))
            is_correct = abs(value - float(target)) <= tolerance
            score = 1.0 if is_correct else 0.0
            correct_answer = target
        answer = {"value": value}

    elif qtype is QuestionType.LIKERT:
        raw = answer.get("value")
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise BadRequest("Choose a point on the scale.", code="answer_invalid")
        lo = int(spec.get("min", 1))
        hi = int(spec.get("max", 5))
        if not lo <= raw <= hi:
            raise BadRequest("That scale point is not available.", code="answer_out_of_range")
        answer = {"value": raw}

    elif qtype is QuestionType.STRUCTURED:
        fields = answer.get("fields")
        if not isinstance(fields, dict) or not fields:
            raise BadRequest("Complete the activity before saving.", code="answer_invalid")
        if len(fields) > 30:
            raise BadRequest("Too many fields submitted.", code="answer_invalid")
        cleaned: dict[str, Any] = {}
        for key, value in fields.items():
            if not isinstance(key, str) or len(key) > 64:
                raise BadRequest("Invalid field name.", code="answer_invalid")
            if isinstance(value, str):
                if len(value) > MAX_TEXT_LENGTH:
                    raise BadRequest("A field is too long.", code="answer_too_long")
                cleaned[key] = value.strip()
            elif isinstance(value, (int, float, bool)) or value is None:
                cleaned[key] = value
            elif isinstance(value, list) and len(value) <= 50:
                cleaned[key] = [v for v in value if isinstance(v, (str, int, float, bool))]
            else:
                raise BadRequest(f"Unsupported value for field '{key}'.", code="answer_invalid")
        required = spec.get("requiredFields", [])
        missing = [f for f in required if not cleaned.get(f)]
        if missing:
            raise BadRequest(
                "Please complete: " + ", ".join(str(m) for m in missing), code="answer_incomplete"
            )
        answer = {"fields": cleaned}

    else:  # pragma: no cover - QuestionType is exhaustive
        raise BadRequest("Unsupported question type.", code="answer_invalid")

    if feedback is None and is_correct is not None:
        feedback = spec.get("correctFeedback") if is_correct else spec.get("incorrectFeedback")

    return Graded(answer, is_correct, score, feedback, explanation, correct_answer)
