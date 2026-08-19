import json
from pathlib import Path

INPUT = Path("output/global_static_analysis.json")
OUTPUT = Path("output/indice_resolucao.txt")

with open(INPUT, "r", encoding="utf-8") as f:
    dados = json.load(f)

grupos = {
    "URL/API DE VALIDAÇÃO": [],
    "HASH": [],
    "OUTPUT PROPERTIES": [],
    "CLOUDWATCH": [],
    "COMANDOS": [],
    "RESPOSTA NUMÉRICA": [],
    "INVESTIGAÇÃO MANUAL": []
}

for item in dados:

    challenge = (
        item.get("challengeId")
        or item.get("challenge")
        or item.get("challenge_id")
        or "DESCONHECIDO"
    )

    task = (
        item.get("taskNumber")
        or item.get("task")
        or item.get("task_number")
        or "?"
    )

    title = item.get("title") or "SEM TÍTULO"

    texto = json.dumps(item, ensure_ascii=False).lower()

    registro = (
        f"{challenge} | TASK {task} | {title}"
    )

    encontrou = False

    if "checkchallengeanswerurl" in texto or "validateapiurl" in texto:
        grupos["URL/API DE VALIDAÇÃO"].append(registro)
        encontrou = True

    if "hash" in texto:
        grupos["HASH"].append(registro)
        encontrou = True

    if "output properties" in texto:
        grupos["OUTPUT PROPERTIES"].append(registro)
        encontrou = True

    if "cloudwatch" in texto:
        grupos["CLOUDWATCH"].append(registro)
        encontrou = True

    if item.get("comandos_detectados"):
        grupos["COMANDOS"].append(registro)
        encontrou = True

    if any(
        palavra in texto
        for palavra in [
            "numeric",
            "number",
            "two decimal",
            "percentage",
            "percent",
            "rate",
            "port"
        ]
    ):
        grupos["RESPOSTA NUMÉRICA"].append(registro)
        encontrou = True

    if not encontrou:
        grupos["INVESTIGAÇÃO MANUAL"].append(registro)


with open(OUTPUT, "w", encoding="utf-8") as out:

    out.write("=" * 90 + "\n")
    out.write("AWS JAM - ÍNDICE OPERACIONAL DE RESOLUÇÃO\n")
    out.write("=" * 90 + "\n\n")

    out.write(
        "TOTAL DE GLOBAL_STATIC_ANSWER: "
        + str(len(dados))
        + "\n\n"
    )

    for nome, itens in grupos.items():

        out.write("=" * 90 + "\n")
        out.write(
            f"{nome} ({len(itens)})\n"
        )
        out.write("=" * 90 + "\n\n")

        if not itens:
            out.write("Nenhuma task.\n\n")
            continue

        for i, item in enumerate(itens, 1):
            out.write(
                f"{i:02d}. {item}\n"
            )

        out.write("\n")

print("=" * 70)
print("ÍNDICE GERADO")
print("=" * 70)
print()
print("Tasks:", len(dados))
print("Arquivo:", OUTPUT)
print()