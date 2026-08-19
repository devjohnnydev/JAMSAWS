import json

INPUT = "output/global_static_analysis.json"
OUTPUT = "output/global_static_report.txt"

with open(INPUT, "r", encoding="utf-8") as f:
    dados = json.load(f)

with open(OUTPUT, "w", encoding="utf-8") as out:

    out.write("=" * 80 + "\n")
    out.write("RELATÓRIO GLOBAL_STATIC_ANSWER\n")
    out.write("=" * 80 + "\n\n")

    for i, task in enumerate(dados, 1):

        out.write("=" * 80 + "\n")
        out.write(
            f"[{i:02d}] {task.get('challengeId')}\n"
        )
        out.write(
            f"TASK: {task.get('taskNumber')}\n"
        )
        out.write(
            f"TÍTULO: {task.get('taskTitle')}\n"
        )
        out.write("=" * 80 + "\n\n")

        perguntas = task.get("perguntas_detectadas", [])
        comandos = task.get("comandos_detectados", [])
        ips = task.get("ips_detectados", [])
        arns = task.get("arns_detectados", [])
        trechos = task.get("trechos_resposta", [])

        out.write("PERGUNTAS DETECTADAS\n")
        out.write("-" * 40 + "\n")

        if perguntas:
            for p in perguntas:
                out.write(f"- {p.strip()}\n")
        else:
            out.write("- Nenhuma detectada automaticamente\n")

        out.write("\n")

        out.write("COMANDOS DETECTADOS\n")
        out.write("-" * 40 + "\n")

        if comandos:
            for c in comandos:
                out.write(f"- {c.strip()}\n")
        else:
            out.write("- Nenhum\n")

        out.write("\n")

        out.write("IPS DETECTADOS\n")
        out.write("-" * 40 + "\n")

        if ips:
            for ip in ips:
                out.write(f"- {ip}\n")
        else:
            out.write("- Nenhum\n")

        out.write("\n")

        out.write("ARNS DETECTADOS\n")
        out.write("-" * 40 + "\n")

        if arns:
            for arn in arns:
                out.write(f"- {arn}\n")
        else:
            out.write("- Nenhum\n")

        out.write("\n")

        out.write("TRECHOS RELACIONADOS A RESPOSTA\n")
        out.write("-" * 40 + "\n")

        if trechos:
            for trecho in trechos:
                out.write(f"- {trecho.strip()}\n")
        else:
            out.write("- Nenhum\n")

        out.write("\n")

        out.write("CONTEÚDO COMPLETO\n")
        out.write("-" * 40 + "\n")
        out.write(task.get("content_limpo", ""))
        out.write("\n\n")


print("=" * 80)
print("RELATÓRIO GERADO")
print("=" * 80)
print(f"Tasks: {len(dados)}")
print(f"Arquivo: {OUTPUT}")
print("=" * 80)