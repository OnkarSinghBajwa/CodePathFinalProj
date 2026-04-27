# Applied AI System Final Project — PawPal+

## Base project

Built on top of **PawPal+** ([original starter repo](https://github.com/OnkarSinghBajwa/ai110-module2show-pawpal-starter)), a Python OOP pet-care manager from Modules 1–3. The original tracks pets, owners, tasks, and a Scheduler with sorting, filtering, recurring tasks, and conflict detection, exposed through a Streamlit UI.

## What this project adds

This extension turns PawPal+ into a full applied AI system by adding three integrated AI features on top of the existing scheduler:

1. **RAG advisor** — a TF-IDF + cosine retriever that pulls answers from a curated pet-care knowledge base.
2. **Agentic workflow** — a planning loop that classifies intent, decides which tools to call (retriever, scheduler, conflict checker), composes an answer, and self-checks confidence.
3. **Reliability layer** — toxic-term guardrails, confidence scoring, structured logging, a 12-case pytest suite, and a 7-case evaluation harness.

Everything runs **fully offline** with zero API keys.

## Architecture

![architecture](assets/architecture.svg)

The user interacts with either the Streamlit UI (`app.py`) or the CLI (`main.py`). Both go through `pawpal_system.py` for state and through `PawPalAgent` for AI questions. The agent retrieves from `data/knowledge.json`, optionally inspects the live schedule, runs a guardrail check, scores confidence, and writes everything to `pawpal.log`. Tests and the eval harness exercise the system end to end.

## Setup

```bash
git clone https://github.com/<your-username>/finalcodepathproject.git
cd finalcodepathproject
pip install streamlit pytest
```

Run options:

```bash
python main.py              # CLI demo end-to-end
streamlit run app.py        # web UI
python -m pytest tests/ -v  # 12 unit tests
python evaluate.py          # 7-case eval harness
```

## Sample interactions

**1. Schedule + conflict detection**
```
=== Today's schedule ===
  07:30  Luna    Wet food              [pending]
  08:00  Rex     Morning walk          [pending]
  09:00  Rex     Heartworm pill        [pending]
  09:00  Luna    Brush coat            [pending]

=== Conflicts ===
  ! Conflict at 09:00: Rex/Heartworm pill vs Luna/Brush coat
```

**2. RAG-backed advisor**
```
USER: What should I feed my adult dog?
PLAN:    classify intent -> retrieve context -> compose answer -> self-check
SOURCES: ['feed_dog_adult', 'feed_cat', 'task_priority']
CONFIDENCE: 0.95
ANSWER: Adult dogs typically eat twice a day, morning and evening, with
        portion size based on weight. Avoid grapes, chocolate, onions,
        and xylitol...
```

**3. Guardrail blocking a toxic-substance question**
```
USER: Can I give Rex chocolate as a treat?
GUARDRAIL: True
CONFIDENCE: 0.0
ANSWER: Guardrail: this question involves a substance known to be toxic
        to pets. Please consult a vet before acting.
```

## Smarter scheduling

- Sort by time using `sorted(..., key=lambda t: t.time)` (HH:MM strings sort lexically as chronologically)
- Filter by pet name or completion status
- Daily/weekly recurrence: marking a recurring task complete spawns the next instance with `timedelta`
- Exact-time conflict detection with human-readable warning strings

## Design decisions

- **Offline-first.** Rule-based "AI" + TF-IDF retrieval keeps the project reproducible for any grader without keys, network, or rate limits.
- **Plain dataclasses.** Easier to inspect, test, and serialize than custom `__init__` boilerplate.
- **Guardrail on the query, not the answer.** Knowledge-base entries themselves mention toxic substances (so users can be warned), so the safety check runs against the *user's intent*, not the retrieved text.
- **Confidence as a function of evidence count.** Simple and transparent: 0.5 floor + 0.15 per source, capped at 1.0; 0.2 when nothing retrieved.

## Testing

```bash
python -m pytest tests/ -v
```

Coverage:
- Task completion flips status
- Adding tasks increases pet count
- Tasks sort chronologically
- Filter by pet and by status
- Recurring tasks spawn next-day instance with correct date
- Conflict detection flags same-time tasks, ignores different times
- Retriever returns relevant docs
- Agent returns sources and a calibrated confidence score
- Guardrail blocks toxic-substance queries
- Low-confidence behavior on irrelevant queries

**Result: 12/12 pass. Eval harness: 7/7, average confidence 0.68.**

## Loom walkthrough

[Add Loom link here after recording]

## Reflection

See [`model_card.md`](model_card.md).
