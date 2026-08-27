from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Status = Literal["PASS", "FAIL"]


class RubricCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    status: Status
    evidence: str = Field(description="Direct evidence for the evaluator's decision.")
    required_change: str = Field(description="Use 'None' only when the check passes.")


class Evaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overall_decision: Status
    checks: list[RubricCheck]
    revision_instructions: list[str]


class RunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topic: str
    status: Literal["SHIP", "MANUAL_REVIEW_REQUIRED"]
    lesson: str
    attempts: int
    rejection_log: list[dict]
