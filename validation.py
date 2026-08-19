"""
validation.py — Compara desafios concluídos por um participante contra o
catálogo mestre, classifica por categoria e calcula o score.
"""
from dataclasses import dataclass, field

from challenges_catalog import Challenge

# Palavras-chave -> categoria. Em produção isso pode vir de um YAML/JSON
# editável, ou de embeddings (TF-IDF / sentence-transformers) em vez de
# match literal de substring.
CATEGORY_KEYWORDS = {
    "Cybersecurity": ["security", "kms", "iam", "escalation", "privilege",
                       "malware", "encrypt", "breach"],
    "Resolução de problemas": ["fix", "recover", "escape", "compromise",
                                "debug", "failover"],
    "Considerações operacionais": ["backup", "monitor", "high availability",
                                    "pipeline", "gateway"],
    "Cryptojacking": ["mining", "crypto", "bitcoin", "hashrate"],
}


@dataclass
class ValidationResult:
    slug: str
    title: str
    matched_categories: list[str] = field(default_factory=list)
    score: int = 0


def classify(title: str) -> list[str]:
    title_lower = title.lower()
    return [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(kw in title_lower for kw in keywords)
    ]


def validate_completed(
    completed_slugs: set[str], catalog: list[Challenge]
) -> list[ValidationResult]:
    results = []
    for challenge in catalog:
        if challenge.slug not in completed_slugs:
            continue
        categories = classify(challenge.title)
        results.append(
            ValidationResult(
                slug=challenge.slug,
                title=challenge.title,
                matched_categories=categories or ["Sem categoria"],
                score=len(categories) or 1,
            )
        )
    return results
