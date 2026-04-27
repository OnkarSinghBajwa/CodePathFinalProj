# Model Card — PawPal+ Applied AI System

## System overview

PawPal+ is a pet-care management app extended with three AI features: a TF-IDF retrieval-augmented advisor, an agentic plan-act-check workflow, and a reliability layer with guardrails, confidence scoring, and structured testing. The system is fully offline and rule-based, so its behavior is deterministic and auditable.

## Intended use

Help a pet owner organize daily routines (feeding, walks, meds, vet visits) and answer general pet-care questions grounded in a small curated knowledge base. Not a substitute for a veterinarian.

## Limitations and biases

- The knowledge base has only ten entries and skews toward dogs and cats. Rabbits, birds, reptiles, and exotic pets are barely covered, so retrieval will return weak matches or nothing for them.
- Conflict detection only flags exact same-time matches. Two tasks scheduled at 09:00 and 09:15 won't be flagged even if both take half an hour.
- The TF-IDF retriever has no understanding of synonyms or paraphrases. "Puppy chow" won't match the puppy-feeding entry if the words don't overlap.
- The toxic-term guardrail is a keyword filter. It catches "Can I give my dog chocolate" but not creative phrasings like "is cocoa a fun snack for Rex".
- Confidence scoring is a simple function of evidence count, not a real probability. A high score means "we found stuff," not "the answer is correct."

## Misuse and prevention

The biggest risk is a user trusting the advisor for medical decisions. Mitigations:
- Hard guardrail on a list of substances toxic to pets, blocking the answer entirely and pointing to a vet
- Every answer surfaces its retrieved source IDs and a confidence score so the user can judge trust
- Logging to `pawpal.log` so questions and outcomes are auditable
- README explicitly states this is not veterinary advice

If extended later, I would add a stronger blocklist, a "consult a vet" disclaimer on any medical-adjacent query, and rate limiting to discourage automated misuse.

## Testing summary

12/12 pytest cases pass, covering scheduler logic, recurrence, conflict detection, retrieval relevance, agent confidence, and guardrail blocking. The 7-case evaluation harness (`evaluate.py`) passes 7/7 with an average confidence of 0.68 across both benign and adversarial queries.

What surprised me during testing: the guardrail initially fired on benign feeding questions because it was scanning the *answer* text, and the knowledge base legitimately mentions chocolate as something to avoid. Moving the check to the user's *query* fixed it. That's a textbook example of how naive safety filters can over-block.

## AI collaboration during this project

I used Claude as a pair programmer throughout. Two specific instances worth calling out:

**Helpful suggestion.** When I asked how to prevent the guardrail from blocking benign queries that retrieved docs containing toxic-term mentions, the suggestion to scope the check to the user query (rather than the composed answer) was the right call. It cleanly separated "user intent to do something dangerous" from "knowledge base mentioning the dangerous thing in a warning." That's a real principle worth keeping.

**Flawed suggestion.** Early on the AI proposed using an embedding model from `sentence-transformers` for the retriever. That would have added a heavy dependency, required a model download, and broken the "fully offline, reproducible" goal for a knowledge base of ten entries. I rejected it and stayed with TF-IDF + cosine, which is the right tool for this scale.

## Reflection on building this

The biggest lesson was that the AI features (RAG, agent, guardrails) are easy to bolt on but hard to integrate *meaningfully*. The rubric specifically calls out that the feature has to change how the system behaves, not just sit next to it. So the agent doesn't just retrieve and dump text — it inspects the live schedule and conflict list when the query calls for it. That integration is what made the project feel like one system instead of three.

The other lesson: reliability work is more interesting than I expected. Writing the eval harness forced me to articulate what "working correctly" actually meant for each query type, and that exercise caught the guardrail bug before any user would have seen it.
