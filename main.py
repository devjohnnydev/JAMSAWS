"""
main.py — Orquestra: autentica -> busca progresso -> valida -> relatório.

Uso:
    python3 main.py <participante_ou_team_id>
"""
import sys

import requests

from auth import load_credentials
from challenges_catalog import load_catalog
from task_validation_report import print_report, write_report_json
from validation import validate_completed


def fetch_completed_challenges(participant_id: str) -> set[str]:
    """Busca os slugs dos desafios já concluídos por um participante/time
    na API do Jam. Ajuste o endpoint/parse conforme a API real."""
    creds = load_credentials()
    url = f"https://{creds.host}/participants/{participant_id}/progress"
    resp = requests.get(url, headers=creds.headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()
    return {item["slug"] for item in payload.get("completed", [])}


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python3 main.py <participante_ou_team_id>")
        sys.exit(1)

    participant_id = sys.argv[1]
    catalog = load_catalog("global_static_answer_challenges.txt")
    completed = fetch_completed_challenges(participant_id)

    results = validate_completed(completed, catalog)
    print_report(participant_id, results)
    write_report_json(participant_id, results)


if __name__ == "__main__":
    main()
