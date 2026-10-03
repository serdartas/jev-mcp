from obasoft_jev_mcp.server import (
    ChoiceQuestion,
    NoulQuestion,
    ScoreQuestion,
    _to_typesafe_question,
)
from typesafe_sdk import Choice, Noul, Score


def test_noul_conversion() -> None:
    question = NoulQuestion(
        type="noul",
        instructions="Is this safe?",
        criteria={"true": "Safe", "false": "Unsafe"},
    )
    converted = _to_typesafe_question(question)
    assert isinstance(converted, Noul)


def test_choice_conversion() -> None:
    question = ChoiceQuestion(
        type="choice",
        instructions="Choose a deployment target",
        criteria={
            "kubernetes": "Existing Kubernetes platform",
            "standalone": "Standalone service",
        },
    )
    converted = _to_typesafe_question(question)
    assert isinstance(converted, Choice)


def test_score_conversion() -> None:
    question = ScoreQuestion(
        type="score",
        instructions="Rate operational risk",
        criteria=["Low", "Medium", "High"],
    )
    converted = _to_typesafe_question(question)
    assert isinstance(converted, Score)
