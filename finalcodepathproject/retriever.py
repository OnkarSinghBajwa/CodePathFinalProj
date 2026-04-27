import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

KB_PATH = Path(__file__).parent / "data" / "knowledge.json"


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]+", text.lower())


class Retriever:
    def __init__(self, kb_path: Path = KB_PATH):
        with open(kb_path) as f:
            self.docs = json.load(f)
        self.tokenized = [tokenize(d["text"] + " " + " ".join(d["tags"])) for d in self.docs]
        self.df = Counter()
        for tokens in self.tokenized:
            for term in set(tokens):
                self.df[term] += 1
        self.n = len(self.docs)

    def _tfidf(self, tokens: List[str]) -> dict:
        tf = Counter(tokens)
        return {
            term: (count / len(tokens)) * math.log((self.n + 1) / (self.df.get(term, 0) + 1))
            for term, count in tf.items()
        }

    def _cosine(self, a: dict, b: dict) -> float:
        common = set(a) & set(b)
        if not common:
            return 0.0
        dot = sum(a[t] * b[t] for t in common)
        na = math.sqrt(sum(v * v for v in a.values()))
        nb = math.sqrt(sum(v * v for v in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        q_vec = self._tfidf(q_tokens)
        scored = []
        for doc, tokens in zip(self.docs, self.tokenized):
            d_vec = self._tfidf(tokens)
            score = self._cosine(q_vec, d_vec)
            if score > 0:
                scored.append((doc, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
