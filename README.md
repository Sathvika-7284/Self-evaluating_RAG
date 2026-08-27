# Self-Evaluating Lesson Generator

A local, API-key-free agentic workflow that creates a beginner lesson on **Introduction to RAG**, evaluates it against hard pass/fail checks, revises failed drafts, and saves its decision trail.

It deliberately emphasizes the quality-control loop, not only the final lesson.

## What the system does

```text
Topic
  -> Local Ollama generator writes a lesson
  -> Deterministic evaluator applies 7 binary quality gates
  -> PASS: ship the lesson and log
  -> FAIL: save evidence, update persistent memory, regenerate with feedback
  -> Stop after 2 retries (3 total attempts)
```

The generator is an LLM running locally through Ollama. The evaluator is deliberately deterministic: its shipping decision is repeatable and cannot be softened by the same small local model that wrote the lesson. This is a practical trade-off for a reliable offline demo.

## Architecture

| Component | File | Responsibility |
|---|---|---|
| Orchestrator | `src/main.py` | Runs generation, evaluation, retrying, output writing, and demo modes. |
| Generator | `src/llm.py` + `src/prompts.py` | Calls a local Ollama model with grounded lesson-writing instructions. |
| Evaluator | `src/evaluator.py` | Applies seven explicit hard gates and produces evidence-based failures. |
| Memory | `src/memory.py` + `data/memory.json` | Persists recurring failure guidance across runs. |
| Schemas | `src/schemas.py` | Defines the structured decision records. |
| Tests | `tests/` | Tests memory persistence and rejection of a deliberate accuracy error. |

## Rubric: seven hard gates

Every check is either `PASS` or `FAIL`; there is no partial credit. A lesson is shipped only if all seven pass.

1. **Accurate and grounded** - correctly expands RAG as Retrieval-Augmented Generation and does not promise perfect answers.
2. **Beginner-friendly language** - uses enough plain-language explanation for a newcomer.
3. **Key points** - covers what RAG is, why it matters, and retrieve -> augment -> generate.
4. **Teaches by example** - includes an end-to-end example.
5. **No unexplained jargon** - monitored technical terms must be defined or avoided.
6. **Coherent teaching flow** - uses the seven required sections in order.
7. **Standalone lesson** - does not rely on links or other external material.

## Why the evaluator is deterministic

An LLM-only evaluator can be inconsistent, especially when it is a small local model. This implementation keeps the creative part (lesson generation) in the model, but implements the shipping requirements as explicit, testable rules. The evaluator returns concrete evidence and revision instructions for every failure. This makes the loop auditable and makes the deliberate-error demo reliable.

## Persistent memory / self-evolution

When a check fails, the system saves the failure count and its correction guidance in `data/memory.json`. The next generator prompt includes this guidance. Across runs, recurring weaknesses become proactive instructions instead of being rediscovered from scratch.

Successful patterns are saved too. This is lightweight memory, rather than a complex database, because the assignment needs a transparent mechanism that is easy to inspect in a GitHub repository.

## Requirements

- Windows PowerShell
- Python 3.12
- [Ollama for Windows](https://ollama.com/download)
- Around 3 GB of free disk space for the `llama3.2:3b` model

No OpenAI, Anthropic, or other cloud API key is required. Ollama runs the model locally.

## Setup

Run these commands from the repository root.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull llama3.2:3b
```

Verify that the model is available:

```powershell
ollama list
```

You should see `llama3.2:3b` in the output.

## Run the system

### Clean production run

```powershell
.\.venv\Scripts\python.exe -m src.main --topic "Introduction to RAG" --reset-memory
```

Expected outcome: `Status: SHIP`. The system saves:

- `outputs/final_lesson.md` - the final lesson.
- `outputs/rejection_log.json` - rejected attempts, evidence, required changes, and applied changes.
- `outputs/attempts/` - draft snapshots for the current run. This folder is intentionally not committed to Git.
- `data/memory.json` - persistent learning from the run.

### Deliberate-error demo

```powershell
.\.venv\Scripts\python.exe -m src.main --topic "Introduction to RAG" --demo-error --reset-memory
```

The program adds the intentionally incorrect sentence *"RAG makes answers always accurate."* to the first draft. The evaluator must reject it under **Accurate and grounded**, then the generator receives the correction and tries again.

### Safe-termination demo (optional)

```powershell
.\.venv\Scripts\python.exe -m src.main --topic "Introduction to RAG" --force-fail --reset-memory
```

This intentionally injects the factual error on every attempt. The program stops after the third evaluation with `MANUAL_REVIEW_REQUIRED`, proving that it cannot loop forever. Run the clean production command again afterwards so your final committed outputs show `SHIP`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp .pytest-tmp
```

The tests verify persistent memory and that the evaluator rejects the deliberate false claim.

## Limitations and next steps

The rule-based evaluator is intentionally transparent, but it cannot judge every subtle factual or pedagogical problem. A production system could add source retrieval, an independent stronger evaluator model, a curated regression set of flawed lessons, and human sampling for high-stakes content. The retry limit and manual-review outcome are kept even in this small prototype because a quality loop must have a safe stopping condition.
