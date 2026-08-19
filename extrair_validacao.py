import json
import re

INPUT = "output/global_static_tasks.json"
OUTPUT = "output/global_static_validation.json"

with open(INPUT, "r", encoding="utf-8") as f:
    tasks = json.load(f)

resultado = []

for task in tasks:

    content = task.get("content", "")

    # Localiza a seção Task Validation
    match = re.search(
        r"##\s*Task Validation(.*)",
        content,
        re.IGNORECASE | re.DOTALL
    )

    validation = ""

    if match:
        validation = match.group(1).strip()

    # Remove algumas seções posteriores, se existirem
    validation = re.split(
        r"\n##\s+",
        validation
    )[0].strip()

    resultado.append({
        "challengeId": task.get("challengeId"),
        "challengeTitle": task.get("challengeTitle"),
        "taskNumber": task.get("taskNumber"),
        "taskTitle": task.get("taskTitle"),
        "validationType": task.get("validationType"),
        "allowInputAnswer": task.get("allowInputAnswer"),
        "validationText": validation
    })


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(
        resultado,
        f,
        ensure_ascii=False,
        indent=2
    )

print("=" * 70)
print("TASK VALIDATION EXTRACTOR")
print("=" * 70)
print("Tasks:", len(resultado))
print("Arquivo:", OUTPUT)
print("=" * 70)

for i, task in enumerate(resultado, 1):

    print()
    print(
        f"[{i:02d}] "
        f"{task['challengeId']} | "
        f"TASK {task['taskNumber']}"
    )

    print(
        f"Título: {task['taskTitle']}"
    )

    print("VALIDAÇÃO:")

    if task["validationText"]:
        print(task["validationText"][:1000])
    else:
        print("NÃO ENCONTRADA")

    print("-" * 70) 