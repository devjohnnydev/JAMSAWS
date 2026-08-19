import json
from pathlib import Path
from collections import Counter


INPUT = Path("output/challenges_raw.json")
OUTPUT = Path("output/tasks_analysis.json")


def analyze_task(challenge_id, challenge_title, task):

    validation_type = task.get("validationType")

    return {
        "challengeId": challenge_id,
        "challengeTitle": challenge_title,

        "taskId": task.get("id"),
        "taskNumber": task.get("taskNumber"),
        "taskTitle": task.get("title"),
        "scorePercent": task.get("scorePercent"),

        "validationType": validation_type,

        "allowInputAnswer": task.get("allowInputAnswer"),
        "validatedByLambda": task.get("validatedByLambda"),
        "validationFunctionRuntime": task.get(
            "validationFunctionRuntime"
        ),

        "variableScoringEnabled": task.get(
            "variableScoringEnabled"
        ),

        "content": task.get("content", "")
    }


def main():

    print("=" * 70)
    print("AWS JAM - TASK ANALYZER")
    print("=" * 70)

    with open(INPUT, "r", encoding="utf-8") as f:
        challenges = json.load(f)

    results = []

    validation_counter = Counter()

    total_tasks = 0

    for index, challenge in enumerate(challenges, start=1):

        data = challenge.get("data", {})
        latest = data.get("latest", {})
        props = latest.get("props", {})

        challenge_id = latest.get("challengeId")

        challenge_title = props.get(
            "title",
            challenge_id
        )

        tasks = props.get("tasks", [])

        print()
        print(
            f"[{index}/{len(challenges)}] "
            f"{challenge_id}"
        )

        print(
            f"    {challenge_title}"
        )

        print(
            f"    Tasks: {len(tasks)}"
        )

        for task in tasks:

            total_tasks += 1

            item = analyze_task(
                challenge_id,
                challenge_title,
                task
            )

            results.append(item)

            validation_type = (
                item["validationType"]
                or "UNKNOWN"
            )

            validation_counter[
                validation_type
            ] += 1

            print(
                f"       Task {item['taskNumber']}: "
                f"{item['taskTitle']}"
            )

            print(
                f"          validationType = "
                f"{validation_type}"
            )

            print(
                f"          allowInputAnswer = "
                f"{item['allowInputAnswer']}"
            )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("RESUMO")
    print("=" * 70)

    print(
        f"Challenges analisados: "
        f"{len(challenges)}"
    )

    print(
        f"Tasks analisadas: "
        f"{total_tasks}"
    )

    print()

    print("TIPOS DE VALIDAÇÃO:")

    for validation_type, quantidade in (
        validation_counter.most_common()
    ):

        print(
            f"  {validation_type}: "
            f"{quantidade}"
        )

    print()
    print(
        f"Arquivo: {OUTPUT}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()