import os
import json
import time
import requests
from dotenv import load_dotenv


load_dotenv()

API_HOST = os.getenv("JAM_API_HOST")

HEADERS = {
    "Authorization": os.getenv("JAM_AUTHORIZATION"),
    "x-aws-waf-token": os.getenv("JAM_WAF_TOKEN"),
    "Accept": "application/json",
    "Origin": "https://jam.aws.com",
}


def request_json(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print(f"[HTTP {response.status_code}] {url}")

    response.raise_for_status()

    return response.json()


def get_events(page=1, limit=150):
    url = (
        f"{API_HOST}/admin/events"
        f"?dateRangeEnd=2026-08-13T23%3A59%3A59.000Z"
        f"&dateRangeStart=2020-01-01T00%3A00%3A00.000Z"
        f"&includeEndedEvents=true"
        f"&limit={limit}"
        f"&page={page}"
    )

    return request_json(url)


def get_challenge(challenge_id):
    url = f"{API_HOST}/admin/challenges/{challenge_id}"

    return request_json(url)


def save_json(data, filename):
    os.makedirs("output", exist_ok=True)

    path = os.path.join("output", filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    print(f"\nArquivo salvo: {path}")


def find_challenge_ids(data):
    """
    Procura IDs/slugs de desafios de forma recursiva.
    """

    ids = set()

    def walk(obj):

        if isinstance(obj, dict):

            # Campos comuns
            for key in [
                "challengeId",
                "challenge_id",
                "slug"
            ]:
                value = obj.get(key)

                if isinstance(value, str) and value:
                    ids.add(value)

            for value in obj.values():
                walk(value)

        elif isinstance(obj, list):

            for item in obj:
                walk(item)

    walk(data)

    return sorted(ids)


def scan_challenges(max_challenges=None):

    print("=" * 70)
    print("AWS JAM - TASK SCANNER")
    print("=" * 70)

    print("\n[1] Consultando eventos...")

    events = get_events(page=1)

    save_json(
        events,
        "events_raw.json"
    )

    challenge_ids = find_challenge_ids(events)

    print(
        f"\nChallenges encontrados inicialmente: "
        f"{len(challenge_ids)}"
    )

    if not challenge_ids:
        print("\nATENÇÃO:")
        print("Nenhum challengeId/slug foi encontrado.")
        print("Abra output/events_raw.json para analisarmos o formato.")
        return []

    if max_challenges:
        challenge_ids = challenge_ids[:max_challenges]

    results = []

    print(
        f"\n[2] Consultando {len(challenge_ids)} Challenges..."
    )

    for index, challenge_id in enumerate(
        challenge_ids,
        start=1
    ):

        print(
            f"\n[{index}/{len(challenge_ids)}] "
            f"{challenge_id}"
        )

        try:

            challenge = get_challenge(
                challenge_id
            )

            results.append({
                "challengeId": challenge_id,
                "data": challenge
            })

            print("    OK")

        except Exception as error:

            print(
                f"    ERRO: {error}"
            )

            results.append({
                "challengeId": challenge_id,
                "error": str(error)
            })

        # Evita fazer chamadas muito agressivas
        time.sleep(0.3)

    save_json(
        results,
        "challenges_raw.json"
    )

    print("\nScanner finalizado.")

    return results


if __name__ == "__main__":

    scan_challenges(
        max_challenges=None
    )