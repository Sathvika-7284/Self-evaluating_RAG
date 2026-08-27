RUBRIC = """
1. Accurate and grounded: RAG means Retrieval-Augmented Generation. It retrieves
   relevant information, adds it to the model prompt, then generates an answer. It
   must not promise perfect accuracy or zero hallucinations.
2. Beginner-friendly language: the explanation assumes no AI background.
3. Key points: it explains what RAG is, why it matters, and retrieve -> augment -> generate.
4. Teaches by example: it includes one concrete end-to-end scenario.
5. No unexplained jargon: technical terms are defined at first use or avoided.
6. Coherent teaching flow: required sections appear in a logical order.
7. Standalone lesson: it does not require links or outside material to understand it.
""".strip()

GROUNDING_FACTS = """
NON-NEGOTIABLE FACTS:
- RAG means Retrieval-Augmented Generation, not Reactive Attention Graph.
- Retrieval finds relevant passages from an approved collection of documents.
- Augmentation places retrieved passages beside the learner's question in the prompt.
- Generation is the language model writing an answer using that supplied context.
- RAG can improve relevance and allow updates without retraining, but it can still retrieve
  irrelevant or outdated information and can still produce an incorrect answer.
""".strip()


def generator_prompt(topic: str, memory_guidance: str) -> str:
    return f"""You are an expert instructional designer. Write a standalone beginner lesson on:
{topic}

The learner starts with zero background. Use short, plain-English paragraphs. Define
technical terms the first time they appear, or avoid them. Use exactly these Markdown
headings in exactly this order: ## Learning goal, ## The problem, ## What RAG is,
## How RAG works, ## Example, ## Limits, ## Recap. Explain what it is, why it matters,
and how it works. Include at least 350 words. Do not use links or invent alternate
meanings for RAG.

{GROUNDING_FACTS}

Lessons learned from previous runs (apply when relevant):
{memory_guidance or 'No prior lessons.'}
"""


def revision_prompt(topic: str, old_lesson: str, feedback: list[str], memory_guidance: str) -> str:
    changes = "\n".join(f"- {item}" for item in feedback)
    return f"""Rewrite the beginner lesson on {topic}. Preserve useful content but fix
every evaluator finding below. Return only the complete replacement lesson. Use the
exact headings ## Learning goal, ## The problem, ## What RAG is, ## How RAG works,
## Example, ## Limits, ## Recap. Write at least 350 words. Do not use links.

{GROUNDING_FACTS}

EVALUATOR FINDINGS:
{changes}

REUSABLE LESSONS:
{memory_guidance or 'No prior lessons.'}

PREVIOUS LESSON:
{old_lesson}
"""
