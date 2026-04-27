import logging
from dataclasses import dataclass, field
from typing import List, Optional

from pawpal_system import Owner, Scheduler
from retriever import Retriever

logging.basicConfig(
    filename="pawpal.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("pawpal")


BLOCKED_TERMS = ["chocolate", "ibuprofen", "acetaminophen", "xylitol", "grape", "onion"]


@dataclass
class AgentResult:
    query: str
    plan: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    answer: str = ""
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    guardrail_triggered: bool = False
    notes: List[str] = field(default_factory=list)


class PawPalAgent:
    def __init__(self, owner: Optional[Owner] = None):
        self.owner = owner
        self.scheduler = Scheduler(owner) if owner else None
        self.retriever = Retriever()

    def _plan(self, query: str) -> List[str]:
        q = query.lower()
        steps = ["classify intent", "retrieve context"]
        if any(w in q for w in ["today", "schedule", "what's on", "tasks"]):
            steps.append("inspect schedule")
        if any(w in q for w in ["conflict", "overlap", "same time"]):
            steps.append("check conflicts")
        steps += ["compose answer", "self-check"]
        return steps

    def _guardrail(self, query: str) -> bool:
        q = query.lower()
        for term in BLOCKED_TERMS:
            if term in q and any(v in q for v in ["give", "feed", "okay", "ok to", "can i", "safe"]):
                return True
        return False

    def _self_check(self, answer: str, sources: List[str]) -> float:
        if not sources:
            return 0.2
        if len(answer) < 20:
            return 0.4
        score = min(1.0, 0.5 + 0.15 * len(sources))
        return round(score, 2)

    def ask(self, query: str) -> AgentResult:
        result = AgentResult(query=query)
        result.plan = self._plan(query)
        logger.info("query: %s", query)
        logger.info("plan: %s", result.plan)

        retrieved = self.retriever.retrieve(query, top_k=3)
        result.actions.append(f"retrieved {len(retrieved)} docs")
        result.sources = [doc["id"] for doc, _ in retrieved]

        schedule_snippet = ""
        if self.scheduler and "inspect schedule" in result.plan:
            today = self.scheduler.todays_schedule()
            result.actions.append(f"inspected schedule ({len(today)} tasks)")
            if today:
                lines = [f"- {t.time} {t.pet_name}: {t.description}" for t in today]
                schedule_snippet = "Today's tasks:\n" + "\n".join(lines)

        conflict_snippet = ""
        if self.scheduler and "check conflicts" in result.plan:
            conflicts = self.scheduler.detect_conflicts()
            result.actions.append(f"checked conflicts ({len(conflicts)} found)")
            if conflicts:
                conflict_snippet = "Conflicts:\n" + "\n".join("- " + c for c in conflicts)

        if retrieved:
            kb_text = "\n".join(f"- {doc['text']}" for doc, _ in retrieved)
            answer_parts = [f"Based on the knowledge base:\n{kb_text}"]
        else:
            answer_parts = ["No relevant knowledge base entry found."]

        if schedule_snippet:
            answer_parts.append(schedule_snippet)
        if conflict_snippet:
            answer_parts.append(conflict_snippet)

        result.answer = "\n\n".join(answer_parts)
        result.actions.append("composed answer")

        if self._guardrail(query):
            result.guardrail_triggered = True
            result.answer = (
                "Guardrail: this question involves a substance known to be toxic to pets. "
                "Please consult a vet before acting. Original retrieved guidance suppressed."
            )
            result.confidence = 0.0
            result.notes.append("blocked by safety guardrail")
            logger.warning("guardrail triggered for query: %s", query)
            return result

        result.confidence = self._self_check(result.answer, result.sources)
        result.actions.append(f"self-check confidence={result.confidence}")
        logger.info("answer confidence: %s sources: %s", result.confidence, result.sources)
        return result
