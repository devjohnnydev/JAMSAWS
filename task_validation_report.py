"""
task_validation_report.py — Monta o relatório final (console + JSON) a partir
dos resultados de validação.
"""
import json
from pathlib import Path

from validation import ValidationResult


def print_report(participant: str, results: list[ValidationResult]) -> None:
    total_score = sum(r.score for r in results)
    print(f"\n=== Relatório: {participant} ===")
    for r in results:
        cats = ", ".join(r.matched_categories)
        print(f" - {r.slug:35s} | score={r.score} | categorias=[{cats}]")
    print(f"Total: {len(results)} desafios | score={total_score}\n")


def write_report_json(
    participant: str, results: list[ValidationResult], out_path: str = "report.json"
) -> None:
    data = {
        "participant": participant,
        "total_challenges": len(results),
        "total_score": sum(r.score for r in results),
        "results": [r.__dict__ for r in results],
    }
    Path(out_path).write_text(json.dumps(data, indent=2, ensure_ascii=False))
