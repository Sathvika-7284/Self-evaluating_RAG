from src.evaluator import evaluate_lesson


VALID_LESSON = """## Learning goal
Think of this as a plain English guide to RAG and why it helps.
## The problem
Language models may not know a company's newest information.
## What RAG is
RAG means Retrieval-Augmented Generation. It uses relevant documents before writing an answer.
## How RAG works
First, retrieve useful passages. Next, augment the prompt by adding those passages. Finally, generate an answer.
## Example
For example, a student asks a question. The system retrieves a handbook section, adds it to the prompt, and writes an answer.
## Limits
RAG can still retrieve an irrelevant passage or generate an incorrect answer.
## Recap
RAG retrieves information, adds it to a prompt, and generates an answer.
""" + ("A simple explanation helps a new learner understand the idea. " * 50)


def test_valid_lesson_passes_all_hard_gates():
    assert evaluate_lesson(VALID_LESSON).overall_decision == "PASS"


def test_accuracy_claim_is_rejected():
    result = evaluate_lesson(VALID_LESSON + "\nRAG makes answers always accurate.")
    accuracy = next(check for check in result.checks if check.name == "Accurate and grounded")
    assert accuracy.status == "FAIL"
