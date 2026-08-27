import argparse
import json
from pathlib import Path

from .evaluator import evaluate_lesson
from .llm import LessonLLM
from .memory import MemoryStore
from .prompts import generator_prompt, revision_prompt
from .schemas import RunResult


ROOT = Path(__file__).resolve().parents[1]


def _inject_demo_error(lesson: str) -> str:
    return lesson.rstrip() + "\n\n**Deliberate demo error:** RAG makes answers always accurate.\n"


def _save_attempt(output_dir: Path, attempt: int, lesson: str) -> None:
    attempts_dir = output_dir / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    (attempts_dir / f"attempt_{attempt:02d}.md").write_text(lesson, encoding="utf-8")


def run(
    topic: str,
    demo_error: bool = False,
    force_fail: bool = False,
    model: str | None = None,
    reset_memory: bool = False,
) -> RunResult:
    """Generate, grade, revise, and persist a lesson with no more than two retries."""
    memory = MemoryStore(ROOT / "data" / "memory.json")
    if reset_memory:
        memory.reset()

    llm = LessonLLM(model)
    output_dir = ROOT / "outputs"
    print("[1/3] Generating a beginner lesson...")
    lesson = llm.text(generator_prompt(topic, memory.guidance()))
    if demo_error or force_fail:
        lesson = _inject_demo_error(lesson)

    rejection_log: list[dict] = []
    for attempt in range(1, 4):  # initial draft plus a maximum of two retries
        if force_fail and attempt > 1:
            lesson = _inject_demo_error(lesson)
        _save_attempt(output_dir, attempt, lesson)

        print(f"[2/3] Evaluating attempt {attempt}/3...")
        evaluation = evaluate_lesson(lesson)
        failed = [item.model_dump() for item in evaluation.checks if item.status == "FAIL"]

        if evaluation.overall_decision == "PASS":
            memory.record_success()
            result = RunResult(
                topic=topic, status="SHIP", lesson=lesson,
                attempts=attempt, rejection_log=rejection_log,
            )
            print(f"[3/3] Attempt {attempt} passed every hard gate. Lesson is ready to ship.")
            break

        rejection_log.append({
            "attempt": attempt,
            "decision": "REJECTED",
            "failed_checks": failed,
            "changes_requested": evaluation.revision_instructions,
            "changes_applied_on_next_attempt": evaluation.revision_instructions if attempt < 3 else [],
        })
        memory.learn_from(failed)
        print(f"[2/3] Attempt {attempt} rejected: {len(failed)} hard gate(s) failed.")

        if attempt == 3:
            result = RunResult(
                topic=topic, status="MANUAL_REVIEW_REQUIRED", lesson=lesson,
                attempts=attempt, rejection_log=rejection_log,
            )
            print("[3/3] Retry limit reached. Manual review is required.")
            break

        print(f"[1/3] Regenerating attempt {attempt + 1} with evaluator feedback...")
        lesson = llm.text(revision_prompt(topic, lesson, evaluation.revision_instructions, memory.guidance()))

    output_dir.mkdir(exist_ok=True)
    (output_dir / "final_lesson.md").write_text(result.lesson, encoding="utf-8")
    (output_dir / "rejection_log.json").write_text(
        json.dumps(result.model_dump(exclude={"lesson"}), indent=2), encoding="utf-8"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and self-evaluate a beginner lesson with local Ollama.")
    parser.add_argument("--topic", default="Introduction to RAG")
    parser.add_argument("--model", default="llama3.2:3b", help="A model already downloaded with Ollama.")
    parser.add_argument("--demo-error", action="store_true", help="Inject a factual error into only the first draft.")
    parser.add_argument("--force-fail", action="store_true", help="Inject a factual error on every attempt to demonstrate safe termination.")
    parser.add_argument("--reset-memory", action="store_true", help="Clear persistent memory before this run.")
    args = parser.parse_args()

    outcome = run(args.topic, args.demo_error, args.force_fail, args.model, args.reset_memory)
    print(f"Status: {outcome.status}; attempts: {outcome.attempts}")
    print(f"Saved: {ROOT / 'outputs'}")
