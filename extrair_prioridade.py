import json
from pathlib import Path

INPUT = Path("output/challenges_raw.json")
OUTPUT = Path("output/prioridade_output_properties.txt")

TARGETS = {
    ("DEVOPS1", 1),
    ("fix-my-research", 3),
    ("gityourcryptoright", 1),
    ("gityourcryptoright", 2),
    ("gityourcryptoright", 5),
    ("movedbmanaged", 2),
    ("redshift-intro-games-jam", 2),
    ("redshift-intro-games-jam", 3),
    ("tag-youre-it", 1),
    ("webpage-styling-broken", 1),
    ("wordpress-breach-quest", 3),
    ("xray-serverless", 1),
}

with open(INPUT, "r", encoding="utf-8") as f:
    challenges = json.load(f)

encontradas = []

for registro in challenges:

    data = registro.get("data", {})
    latest = data.get("latest", {})
    props = latest.get("props", {})
    tasks = props.get("tasks", [])

    challenge_id = (
        registro.get("challengeId")
        or registro.get("id")
        or registro.get("slug")
        or data.get("slug")
        or data.get("id")
    )

    # tenta descobrir o ID em diferentes estruturas
    if not challenge_id:
        challenge_id = (
            props.get("id")
            or props.get("challengeId")
            or props.get("slug")
        )

    for task in tasks:

        numero = task.get("taskNumber")

        if (challenge_id, numero) not in TARGETS:
            continue

        encontradas.append({
            "challenge": challenge_id,
            "task": numero,
            "title": task.get("title"),
            "content": task.get("content"),
            "validationType": task.get("validationType"),
            "allowInputAnswer": task.get("allowInputAnswer"),
        })


with open(OUTPUT, "w", encoding="utf-8") as out:

    out.write("=" * 100 + "\n")
    out.write("AWS JAM - TASKS PRIORITÁRIAS: OUTPUT PROPERTIES\n")
    out.write("=" * 100 + "\n\n")

    out.write(
        f"Tasks encontradas: {len(encontradas)}\n\n"
    )

    for i, task in enumerate(encontradas, 1):

        out.write("=" * 100 + "\n")
        out.write(
            f"[{i:02d}] {task['challenge']} | TASK {task['task']}\n"
        )
        out.write("=" * 100 + "\n\n")

        out.write(
            f"TÍTULO: {task['title']}\n"
        )

        out.write(
            f"VALIDAÇÃO: {task['validationType']}\n"
        )

        out.write(
            f"INPUT ANSWER: {task['allowInputAnswer']}\n\n"
        )

        out.write("CONTEÚDO COMPLETO\n")
        out.write("-" * 80 + "\n")
        out.write(
            task["content"] or "SEM CONTEÚDO"
        )
        out.write("\n\n")

print("=" * 80)
print("EXTRAÇÃO FINALIZADA")
print("=" * 80)
print()
print("Tasks encontradas:", len(encontradas))
print("Arquivo:", OUTPUT)