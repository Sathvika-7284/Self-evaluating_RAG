"""Deterministic, evidence-based quality gate for beginner RAG lessons.

The generator is an LLM. The evaluator is intentionally deterministic so the shipping
decision is repeatable and a small local model cannot grade its own mistakes leniently.
"""

from .schemas import Evaluation, RubricCheck


REQUIRED_HEADINGS = [
    "## Learning goal", "## The problem", "## What RAG is", "## How RAG works",
    "## Example", "## Limits", "## Recap",
]


def _check(name: str, passed: bool, evidence: str, change: str) -> RubricCheck:
    return RubricCheck(
        name=name,
        status="PASS" if passed else "FAIL",
        evidence=evidence,
        required_change="None" if passed else change,
    )


def evaluate_lesson(lesson: str) -> Evaluation:
    """Apply all seven binary rubric gates and return actionable evidence."""
    text = lesson.lower()
    positions = [text.find(heading.lower()) for heading in REQUIRED_HEADINGS]
    ordered_sections = all(position >= 0 for position in positions) and positions == sorted(positions)

    forbidden_claims = [
        "reactive attention graph", "rag makes answers always accurate", "rag guarantees",
        "guarantees correct", "eliminates hallucinations", "always retrieves good",
    ]
    forbidden_found = next((claim for claim in forbidden_claims if claim in text), None)
    accurate = (
        "retrieval-augmented generation" in text
        and all(phrase in text for phrase in ("retriev", "prompt", "generat"))
        and not forbidden_found
    )
    beginner = len(lesson.split()) >= 300 and any(
        signal in text for signal in ("plain english", "in other words", "simply", "think of")
    )
    key_points = all(
        phrase in text
        for phrase in ("retrieval-augmented generation", "retrieve", "augment", "generate", "why")
    )
    example = (
        "## example" in text
        and any(term in text for term in ("for example", "imagine", "suppose"))
        and all(phrase in text for phrase in ("question", "retriev", "answer"))
    )

    jargon_rules = {
        "llm": "large language model",
        "embedding": "numerical representation",
        "vector database": "database",
        "context window": "text the model can read",
    }
    undefined = [term for term, definition in jargon_rules.items() if term in text and definition not in text]
    standalone = not any(marker in text for marker in ("http://", "https://", "see link"))

    checks = [
        _check(
            "Accurate and grounded", accurate,
            "RAG is correctly expanded and the retrieve → prompt → generate sequence is present."
            if accurate else f"Missing the required definition/flow or found forbidden claim: {forbidden_found!r}.",
            "State that RAG means Retrieval-Augmented Generation; explain retrieve, add context to the prompt, then generate; remove any guarantee claim.",
        ),
        _check(
            "Beginner-friendly language", beginner,
            "The lesson is long enough for a beginner and includes a plain-language teaching signal."
            if beginner else "The lesson is too short or lacks an explicit plain-language explanation.",
            "Use at least 300 words and include a simple analogy or phrase such as 'Think of it as'.",
        ),
        _check(
            "Key points", key_points,
            "It covers the definition, why RAG matters, and retrieve → augment → generate."
            if key_points else "One or more required concepts are missing.",
            "Explain what RAG is, why it matters, and each stage: retrieve, augment, generate.",
        ),
        _check(
            "Teaches by example", example,
            "The example includes a question, retrieval step, and answer-generation step."
            if example else "No complete end-to-end example was detected.",
            "Add one scenario showing a user question, relevant document retrieval, prompt augmentation, and an answer.",
        ),
        _check(
            "No unexplained jargon", not undefined,
            "No monitored jargon is used without its plain-English definition."
            if not undefined else f"These terms need definitions: {', '.join(undefined)}.",
            f"Define or remove these terms: {', '.join(undefined)}.",
        ),
        _check(
            "Coherent teaching flow", ordered_sections,
            "All seven required sections appear in the required order."
            if ordered_sections else "Required headings are missing or out of order.",
            "Use the seven required headings in order: Learning goal, The problem, What RAG is, How RAG works, Example, Limits, Recap.",
        ),
        _check(
            "Standalone lesson", standalone,
            "No external links or outside material are required."
            if standalone else "The lesson includes an external link or directs the learner elsewhere.",
            "Remove external links and include all needed explanation in the lesson itself.",
        ),
    ]
    failures = [check.required_change for check in checks if check.status == "FAIL"]
    return Evaluation(
        overall_decision="PASS" if not failures else "FAIL",
        checks=checks,
        revision_instructions=failures,
    )
