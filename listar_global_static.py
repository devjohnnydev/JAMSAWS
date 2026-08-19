import json

ARQUIVO = "output/global_static_analysis.json"
SAIDA = "output/global_static_lista.txt"

with open(ARQUIVO, "r", encoding="utf-8") as f:
    dados = json.load(f)

linhas = []

linhas.append("=" * 80)
linhas.append("GLOBAL_STATIC_ANSWER - LISTA DAS TASKS")
linhas.append("=" * 80)
linhas.append(f"TOTAL: {len(dados)}")
linhas.append("")

for i, task in enumerate(dados, 1):
    challenge = task.get("challengeId", "")
    numero = task.get("taskNumber", "")
    titulo = task.get("title", "SEM TÍTULO")

    linhas.append(f"[{i:02d}] {challenge}")
    linhas.append(f"     TASK: {numero}")
    linhas.append(f"     TÍTULO: {titulo}")
    linhas.append("")

linhas.append("=" * 80)
linhas.append("LISTAGEM FINALIZADA")
linhas.append("=" * 80)

with open(SAIDA, "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))

print("=" * 70)
print("LISTAGEM GERADA")
print("=" * 70)
print(f"Tasks: {len(dados)}")
print(f"Arquivo: {SAIDA}")
print("=" * 70)