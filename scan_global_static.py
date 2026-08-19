import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv(
    "JAM_API_HOST",
    "https://core.proxy.prod.us-west-2.prod.jam.training.aws.dev"
).rstrip("/")

AUTHORIZATION = os.getenv("JAM_AUTHORIZATION")
WAF_TOKEN = os.getenv("JAM_WAF_TOKEN")

if not AUTHORIZATION:
    raise RuntimeError(
        "JAM_AUTHORIZATION não configurado no .env"
    )

if not WAF_TOKEN:
    raise RuntimeError(
        "JAM_WAF_TOKEN não configurado no .env"
    )


session = requests.Session()

session.headers.update({
    "Accept": "application/json",
    "Authorization": AUTHORIZATION,
    "x-aws-waf-token": WAF_TOKEN,
    "Origin": "https://jam.aws.com",
    "Referer": "https://jam.aws.com/",
})


def get_events(page):
    url = f"{HOST}/admin/events"

    params = {
        "dateRangeEnd": "2027-01-01T00:00:00.000Z",
        "dateRangeStart": "2020-01-01T00:00:00.000Z",
        "includeEndedEvents": "true",
        "limit": 150,
        "page": page,
    }

    response = session.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_challenge(challenge_id):
    url = f"{HOST}/admin/challenges/{challenge_id}"

    response = session.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def extract_challenge_ids(data):
    """
    Procura recursivamente por challengeId
    dentro do JSON retornado por /admin/events.
    """

    ids = set()

    def walk(value):

        if isinstance(value, dict):

            challenge_id = value.get("challengeId")

            if isinstance(challenge_id, str):
                ids.add(challenge_id)

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for child in value:
                walk(child)

    walk(data)

    return ids


def extract_global_static(challenge_id, data):
    """
    Procura GLOBAL_STATIC_ANSWER em qualquer
    nível do JSON do challenge.
    """

    encontrados = []

    def walk(value, path=""):

        if isinstance(value, dict):

            validation_type = value.get(
                "validationType"
            )

            if validation_type == "GLOBAL_STATIC_ANSWER":

                encontrados.append({
                    "challengeId": challenge_id,
                    "path": path,
                    "task": value
                })

            for key, child in value.items():

                child_path = (
                    f"{path}.{key}"
                    if path
                    else key
                )

                walk(child, child_path)

        elif isinstance(value, list):

            for index, child in enumerate(value):

                walk(
                    child,
                    f"{path}[{index}]"
                )

    walk(data)

    return encontrados


def main():

    print()
    print("=" * 70)
    print(" AWS JAM - GLOBAL_STATIC_ANSWER SCANNER")
    print("=" * 70)
    print()

    # ---------------------------------------------------------
    # ETAPA 1 - BUSCAR TODOS OS CHALLENGE IDs
    # ---------------------------------------------------------

    challenge_ids = set()

    for page in range(1, 100):

        print(
            f"[EVENTS] Consultando página {page}..."
        )

        try:

            data = get_events(page)

            ids = extract_challenge_ids(data)

            print(
                f"         {len(ids)} challenge IDs encontrados"
            )

            novos = ids - challenge_ids

            challenge_ids.update(ids)

            print(
                f"         {len(novos)} novos"
            )

            print(
                f"         Total acumulado: "
                f"{len(challenge_ids)}"
            )

            # Se não encontrou novos IDs,
            # provavelmente chegamos ao fim.
            if not novos:
                break

            # Se veio menos que o limite,
            # provavelmente é a última página.
            if len(ids) < 150:
                break

        except Exception as e:

            print(
                f"         ERRO: {e}"
            )

    print()
    print("=" * 70)
    print(
        f"TOTAL DE CHALLENGES: {len(challenge_ids)}"
    )
    print("=" * 70)
    print()

    # ---------------------------------------------------------
    # ETAPA 2 - CONSULTAR CADA CHALLENGE
    # ---------------------------------------------------------

    resultados = []

    for numero, challenge_id in enumerate(
        sorted(challenge_ids),
        start=1
    ):

        print(
            f"[{numero}/{len(challenge_ids)}] "
            f"{challenge_id}"
        )

        try:

            challenge = get_challenge(
                challenge_id
            )

            encontrados = extract_global_static(
                challenge_id,
                challenge
            )

            if encontrados:

                print(
                    f"    >>> ENCONTRADO: "
                    f"{len(encontrados)}"
                )

                for item in encontrados:

                    task = item["task"]

                    resultado = {
                        "challengeId":
                            challenge_id,

                        "path":
                            item["path"],

                        "validationType":
                            task.get(
                                "validationType"
                            ),

                        "task":
                            task
                    }

                    resultados.append(
                        resultado
                    )

            else:

                print(
                    "    - nenhum"
                )

        except requests.HTTPError as e:

            print(
                f"    HTTP ERROR: {e}"
            )

        except Exception as e:

            print(
                f"    ERROR: {e}"
            )

        time.sleep(0.15)

    # ---------------------------------------------------------
    # ETAPA 3 - SALVAR RESULTADO
    # ---------------------------------------------------------

    arquivo = (
        "global_static_answer_challenges.json"
    )

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            resultados,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print(" VARREDURA FINALIZADA")
    print("=" * 70)
    print()
    print(
        f"GLOBAL_STATIC_ANSWER encontrados: "
        f"{len(resultados)}"
    )
    print()
    print(
        f"Arquivo: {arquivo}"
    )
    print()


if __name__ == "__main__":
    main()