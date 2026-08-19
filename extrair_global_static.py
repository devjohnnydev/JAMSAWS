import json

INPUT = "output/challenges_raw.json"
OUTPUT = "output/global_static_tasks.json"

with open(INPUT, "r", encoding="utf-8") as f:
    challenges = json.load(f)

resultado = []

for item in challenges:

    challenge_id = (
        item.get("challengeId")
        or item.get("id")
    )

    data = item.get("data", {})
    latest = data.get("latest", {})
    props = latest.get("props", {})

    challenge_title = (
        props.get("title")
        or props.get("name")
        or challenge_id
    )

    tasks = props.get("tasks", [])

    for task in tasks:

        if task.get("validationType") != "GLOBAL_STATIC_ANSWER":
            continue

        resultado.append({
            "challengeId": challenge_id,
            "challengeTitle": challenge_title,

            "taskId": task.get("id"),
            "taskNumber": task.get("taskNumber"),
            "taskTitle": task.get("title"),

            "scorePercent": task.get("scorePercent"),

            "content": task.get("content"),

            "validationType": task.get("validationType"),
            "allowInputAnswer": task.get("allowInputAnswer"),

            "validationFunction": task.get(
                "validationFunction"
            ),

            "validationFunctionRuntime": task.get(
                "validationFunctionRuntime"
            ),

            "validatedByLambda": task.get(
                "validatedByLambda"
            )
        })


with open(OUTPUT, "w", encoding="utf-8") as f:

    json.dump(
        resultado,
        f,
        ensure_ascii=False,
        indent=2
    )


print("=" * 70)
print("EXTRAÇÃO GLOBAL_STATIC_ANSWER")
print("=" * 70)

print(f"TOTAL ENCONTRADO: {len(resultado)}")
print(f"ARQUIVO: {OUTPUT}")

print("=" * 70)

for i, task in enumerate(resultado, 1):

    print(
        f"[{i:02d}] "
        f"{task['challengeId']} | "
        f"TASK {task['taskNumber']} | "
        f"{task['taskTitle']}"
    )