import json


with open("output/challenges_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)


def walk(obj, path="root", depth=0, max_depth=8):

    if depth > max_depth:
        return

    if isinstance(obj, dict):

        for key, value in obj.items():

            key_lower = str(key).lower()

            if (
                "task" in key_lower
                or "answer" in key_lower
                or "global" in key_lower
                or "validation" in key_lower
            ):
                print(
                    f"[{path}.{key}] "
                    f"tipo={type(value).__name__}"
                )

            walk(
                value,
                f"{path}.{key}",
                depth + 1,
                max_depth
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj[:10]):

            walk(
                value,
                f"{path}[{index}]",
                depth + 1,
                max_depth
            )


print("=" * 70)
print("INSPEÇÃO DA ESTRUTURA")
print("=" * 70)

walk(data[0])

print("=" * 70)
print("FIM")
print("=" * 70)