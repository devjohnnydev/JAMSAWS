import json
import re
from pathlib import Path

INPUT = Path("output/global_static_analysis.json")
OUTPUT = Path("output/global_static_classificado.txt")


def classificar(task):
    texto = " ".join([
        str(task.get("title", "")),
        str(task.get("content", "")),
        " ".join(task.get("perguntas_detectadas", [])),
        " ".join(task.get("comandos_detectados", [])),
        " ".join(task.get("trechos_resposta", [])),
    ]).lower()

    grupos = []

    # URL de validação
    if any(x in texto for x in [
        "checkchallengeanswerurl",
        "check challenge answer url",
        "validateapiurl",
        "validate api",
        "/validate"
    ]):
        grupos.append("URL/API DE VALIDAÇÃO")

    # CloudWatch
    if any(x in texto for x in [
        "cloudwatch",
        "cloudwatch logs",
        "log group",
        "log stream",
        "cloudwatch insights"
    ]):
        grupos.append("CLOUDWATCH / LOGS")

    # Output Properties
    if any(x in texto for x in [
        "output properties",
        "output property",
        "stack outputs"
    ]):
        grupos.append("OUTPUT PROPERTIES")

    # Comandos
    if task.get("comandos_detectados"):
        grupos.append("EXECUÇÃO DE COMANDOS")

    # IP
    if re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", texto):
        grupos.append("IP / ENDEREÇO")

    # ARN
    if "arn:aws:" in texto:
        grupos.append("ARN")

    # Porta
    if any(x in texto for x in [
        "port",
        "porta",
        "reverse shell"
    ]):
        grupos.append("PORTA")

    # Hash
    if any(x in texto for x in [
        "hash",
        "sha256",
        "md5"
    ]):
        grupos.append("HASH")

    # Resposta numérica
    if any(x in texto for x in [
        "two decimal",
        "two decimal points",
        "decimal",
        "numeric answer",
        "number",
        "número"
    ]):
        grupos.append("RESPOSTA NUMÉRICA")

    # Pergunta direta
    if any(x in texto for x in [
        "answer question",
        "task validation",
        "submit your answer",
        "submit answer",
        "enter the answer",
        "enter your answer"
    ]):
        grupos.append("RESPOSTA DIRETA")

    if not grupos:
        grupos.append("INVESTIGAÇÃO MANUAL")

    # remove duplicados mantendo ordem
    grupos = list(dict.fromkeys(grupos))

    return grupos


def obter_texto_lista(valor):
    if not valor:
        return []

    if isinstance(valor, list):
        return [str(x) for x in valor if x]

    return [str(valor)]


def main():

    print("=" * 80)
    print("AWS JAM - CLASSIFICADOR GLOBAL_STATIC_ANSWER")
    print("=" * 80)

    if not INPUT.exists():
        print()
        print("ERRO: arquivo não encontrado:")
        print(INPUT)
        print()
        print("Execute primeiro:")
        print("python analisar_respostas.py")
        return

    with open(INPUT, "r", encoding="utf-8") as f:
        dados = json.load(f)

    print()
    print("Tasks carregadas:", len(dados))
    print()

    resultados = []

    for i, task in enumerate(dados, 1):

        challenge = (
            task.get("challengeId")
            or task.get("challenge")
            or task.get("challenge_id")
            or "DESCONHECIDO"
        )

        task_number = (
            task.get("taskNumber")
            or task.get("task")
            or task.get("task_number")
            or "?"
        )

        title = task.get("title") or "SEM TÍTULO"

        perguntas = obter_texto_lista(
            task.get("perguntas_detectadas")
        )

        comandos = obter_texto_lista(
            task.get("comandos_detectados")
        )

        trechos = obter_texto_lista(
            task.get("trechos_relacionados")
            or task.get("trechos_resposta")
        )

        # Criamos uma cópia temporária com os campos normalizados
        temp = dict(task)
        temp["perguntas_detectadas"] = perguntas
        temp["comandos_detectados"] = comandos
        temp["trechos_resposta"] = trechos

        grupos = classificar(temp)

        resultados.append({
            "challenge": challenge,
            "task": task_number,
            "title": title,
            "grupos": grupos,
            "perguntas": perguntas,
            "comandos": comandos,
            "trechos": trechos
        })

        print(
            f"[{i:02d}/{len(dados)}] "
            f"{challenge} | TASK {task_number} | "
            f"{', '.join(grupos)}"
        )

    # ==========================================================
    # GERA RELATÓRIO
    # ==========================================================

    with open(OUTPUT, "w", encoding="utf-8") as f:

        f.write("=" * 100 + "\n")
        f.write("AWS JAM - MAPA DE RESOLUÇÃO GLOBAL_STATIC_ANSWER\n")
        f.write("=" * 100 + "\n\n")

        f.write(f"TOTAL DE TASKS: {len(resultados)}\n\n")

        # ------------------------------------------------------
        # RESUMO POR GRUPO
        # ------------------------------------------------------

        contagem = {}

        for item in resultados:
            for grupo in item["grupos"]:
                contagem[grupo] = contagem.get(grupo, 0) + 1

        f.write("RESUMO POR GRUPO\n")
        f.write("-" * 100 + "\n")

        for grupo, quantidade in sorted(
            contagem.items(),
            key=lambda x: (-x[1], x[0])
        ):
            f.write(f"{grupo:<35} {quantidade}\n")

        f.write("\n")
        f.write("=" * 100 + "\n\n")

        # ------------------------------------------------------
        # LISTAGEM COMPLETA
        # ------------------------------------------------------

        for i, item in enumerate(resultados, 1):

            f.write("=" * 100 + "\n")
            f.write(
                f"[{i:02d}] {item['challenge']} | "
                f"TASK {item['task']}\n"
            )
            f.write(f"TÍTULO: {item['title']}\n")
            f.write("=" * 100 + "\n\n")

            f.write("CLASSIFICAÇÃO\n")
            f.write("-" * 100 + "\n")

            for grupo in item["grupos"]:
                f.write(f"- {grupo}\n")

            f.write("\n")

            f.write("PERGUNTAS / INSTRUÇÕES\n")
            f.write("-" * 100 + "\n")

            if item["perguntas"]:
                for pergunta in item["perguntas"]:
                    f.write(f"- {pergunta}\n")
            else:
                f.write("- Nenhuma detectada\n")

            f.write("\n")

            f.write("COMANDOS / PROCEDIMENTOS\n")
            f.write("-" * 100 + "\n")

            if item["comandos"]:
                for comando in item["comandos"]:
                    f.write(f"- {comando}\n")
            else:
                f.write("- Nenhum detectado\n")

            f.write("\n")

            f.write("TRECHOS RELACIONADOS À RESPOSTA\n")
            f.write("-" * 100 + "\n")

            if item["trechos"]:
                for trecho in item["trechos"]:
                    f.write(f"- {trecho}\n")
            else:
                f.write("- Nenhum detectado\n")

            f.write("\n")

    print()
    print("=" * 80)
    print("CLASSIFICAÇÃO FINALIZADA")
    print("=" * 80)
    print()
    print("Tasks analisadas:", len(resultados))
    print("Arquivo:", OUTPUT)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()