import json
import re
from html import unescape

INPUT = "output/global_static_tasks.json"
OUTPUT = "output/global_static_analysis.json"


def limpar_html(texto):
    texto = unescape(texto or "")
    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def procurar(padrao, texto):
    return re.findall(padrao, texto, re.IGNORECASE)


with open(INPUT, "r", encoding="utf-8") as f:
    tasks = json.load(f)


resultado = []

for task in tasks:

    content = task.get("content", "")
    texto = limpar_html(content)

    perguntas = procurar(
        r"[^.!?\n]*(?:what|which|where|how many|how much|provide|enter|answer|identify|find|give|name)[^.!?\n]*[?]?",
        texto
    )

    comandos = re.findall(
        r"(?:aws|awscli|python|pip|curl|wget|git|ssh)\s+[^\n<]+",
        texto,
        re.IGNORECASE
    )

    arns = re.findall(
        r"arn:aws:[^\s<]+",
        texto,
        re.IGNORECASE
    )

    ips = re.findall(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        texto
    )

    portas = re.findall(
        r"(?:port|porta)\s*(?:is|:|=)?\s*(\d{2,5})",
        texto,
        re.IGNORECASE
    )

    palavras_resposta = re.findall(
        r".{0,100}(?:answer|response|expected|value|output|result|password|secret|code|port|ip|arn).{0,150}",
        texto,
        re.IGNORECASE
    )

    resultado.append({
        "challengeId": task.get("challengeId"),
        "challengeTitle": task.get("challengeTitle"),
        "taskId": task.get("taskId"),
        "taskNumber": task.get("taskNumber"),
        "taskTitle": task.get("taskTitle"),

        "perguntas_detectadas": perguntas[:20],
        "comandos_detectados": comandos[:30],
        "arns_detectados": arns[:30],
        "ips_detectados": ips[:30],
        "portas_detectadas": portas[:30],
        "trechos_resposta": palavras_resposta[:30],

        "content_limpo": texto
    })


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)


print("=" * 70)
print("ANÁLISE DAS GLOBAL_STATIC_ANSWER")
print("=" * 70)
print(f"Tasks analisadas: {len(resultado)}")
print(f"Arquivo: {OUTPUT}")
print("=" * 70)

for i, r in enumerate(resultado, 1):

    print(
        f"[{i:02d}] "
        f"{r['challengeId']} | "
        f"TASK {r['taskNumber']} | "
        f"{r['taskTitle']}"
    )

    if r["perguntas_detectadas"]:
        print("     Perguntas:", len(r["perguntas_detectadas"]))

    if r["arns_detectados"]:
        print("     ARNs:", len(r["arns_detectados"]))

    if r["ips_detectados"]:
        print("     IPs:", len(r["ips_detectados"]))

    if r["comandos_detectados"]:
        print("     Comandos:", len(r["comandos_detectados"]))

print()
print("ANÁLISE FINALIZADA")