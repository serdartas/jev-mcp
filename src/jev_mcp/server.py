from __future__ import annotations

import os
from typing import Annotated, Any, Literal

from mcp.server import MCPServer
from pydantic import BaseModel, ConfigDict, Field
from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score


class _QuestionBase(BaseModel):
    """Common validation policy for Jev questions."""

    model_config = ConfigDict(extra="forbid")


class NoulQuestion(_QuestionBase):
    """Binary yes/no or true/false judgment."""

    type: Literal["noul"]
    instructions: Any | None = None
    criteria: dict[str, Any | None] | None = None


class ChoiceQuestion(_QuestionBase):
    """Select one named option from a set of alternatives."""

    type: Literal["choice"]
    instructions: Any | None = None
    criteria: dict[str, Any | None]


class ScoreQuestion(_QuestionBase):
    """Rate the state against an ordered rubric starting at level 0."""

    type: Literal["score"]
    instructions: Any | None = None
    criteria: list[Any]


Question = Annotated[
    NoulQuestion | ChoiceQuestion | ScoreQuestion,
    Field(discriminator="type"),
]


mcp = MCPServer("Obasoft Jev")


def _require_api_key() -> None:
    if not os.environ.get("TYPESAFE_API_KEY"):
        raise RuntimeError(
            "TYPESAFE_API_KEY is not available to the Jev MCP process."
        )


def _to_typesafe_question(question: Question) -> Noul | Choice | Score:
    if isinstance(question, NoulQuestion):
        return Noul(
            instructions=question.instructions,
            criteria=question.criteria,
        )

    if isinstance(question, ChoiceQuestion):
        return Choice(
            instructions=question.instructions,
            criteria=question.criteria,
        )

    if isinstance(question, ScoreQuestion):
        return Score(
            instructions=question.instructions,
            criteria=question.criteria,
        )

    raise TypeError(f"Unsupported Jev question: {type(question)!r}")


def _jsonable(value: Any) -> Any:
    """Convert SDK/Pydantic responses into MCP-safe JSON values."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


@mcp.tool()
async def system_one(
    state: Any,
    questions: dict[str, Question],
    model: str = "jev-latest",
) -> dict[str, Any]:
    """Ask TypeSafe Jev to make one or more structured judgments.

    Use:
    - type="choice" when exactly one named alternative should be selected.
      `criteria` is an object mapping option names to descriptions.
    - type="noul" for a yes/no or true/false judgment. The returned `noul`
      value is the probability of yes/true.
    - type="score" for an ordered rubric. `criteria` is a list whose first
      item is score 0, second is score 1, and so on.

    `state` is the shared evidence/context the questions should judge. It may
    be a string, object, or array. Multiple question types may be mixed in one
    request. The response includes probabilities/confidence where supported.
    """
    _require_api_key()

    if not questions:
        raise ValueError("At least one Jev question is required.")

    sdk_questions = {
        name: _to_typesafe_question(question)
        for name, question in questions.items()
    }

    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state=state,
            questions=sdk_questions,
            model=model,
        )

    payload = _jsonable(response)

    # The SDK exposes request_id as useful trace metadata; preserve it when it
    # is not already part of the serialized response body.
    request_id = getattr(response, "request_id", None)
    if isinstance(payload, dict) and request_id and "request_id" not in payload:
        payload["request_id"] = request_id

    return payload


@mcp.tool()
async def list_models() -> dict[str, Any]:
    """List TypeSafe models/aliases currently available to System One."""
    _require_api_key()

    async with AsyncTypeSafeClient() as client:
        response = await client.models.list()

    return _jsonable(response)


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
