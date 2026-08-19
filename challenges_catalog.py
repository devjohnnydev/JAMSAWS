"""
challenges_catalog.py — Carrega o catálogo mestre de desafios.

Formato do .txt (um por linha):
    slug | Título do desafio
"""
from pathlib import Path
from typing import NamedTuple


class Challenge(NamedTuple):
    slug: str
    title: str


def load_catalog(path: str = "global_static_answer_challenges.txt") -> list[Challenge]:
    challenges = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        slug, title = (part.strip() for part in line.split("|", 1))
        challenges.append(Challenge(slug=slug, title=title))
    return challenges


def load_validation_types(path: str = "validation_types.txt") -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
