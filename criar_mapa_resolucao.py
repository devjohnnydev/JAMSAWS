import json
from pathlib import Path

INPUT = Path("output/global_static_analysis.json")
OUTPUT = Path("output/global_static_resolucao.txt")


def lista(valor):
    if not valor:
        return []

    if isinstance(valor, list):
        return [str(x) for x in valor if x]

    return [str(valor)]


def classificar(item):

    perguntas = lista(item.get("perguntas_detectadas"))
    comandos = lista(item.get("comandos_detectados"))
    trechos = lista(
        item.get("trechos_relacionados")
        or item.get("trechos_resposta")
    )

    texto = " ".join(perguntas + comandos + trechos)
    t = texto.lower()

    grupos = []
    acoes = []

    # =========================================================
    # 1. URL DE VALIDAÇÃO
    # =========================================================

    if "checkchallengeanswerurl" in t:
        grupos.append("URL DE VALIDAÇÃO")

        acoes.append(
            "Resolver a configuração indicada pela task e "
            "acessar CheckChallengeAnswerURL no final."
        )

    if "validateapiurl" in t:
        grupos.append("VALIDATE API")

        acoes.append(
            "Resolver a aplicação/configuração e acessar "
            "ValidateAPIURL para obter a resposta."
        )

    # =========================================================
    # 2. OUTPUT PROPERTIES
    # =========================================================

    if "output properties" in t:
        grupos.append("OUTPUT PROPERTIES")

        acoes.append(
            "Abrir Output Properties no JAM e identificar "
            "URLs, IDs, ARNs ou parâmetros necessários."
        )

    # =========================================================
    # 3. CLOUDWATCH
    # =========================================================

    if "cloudwatch" in t:
        grupos.append("CLOUDWATCH")

        acoes.append(
            "Consultar CloudWatch Logs conforme indicado "
            "pela task."
        )

    # =========================================================
    # 4. COMANDOS
    # =========================================================

    if comandos:
        grupos.append("COMANDOS")

        acoes.append(
            "Executar os comandos/procedimentos indicados "
            "pela task."
        )

    # =========================================================
    # 5. RESPOSTA NUMÉRICA
    # =========================================================

    palavras_numericas = [
        "numeric answer",
        "numeric",
        "number",
        "número",
        "two decimal",
        "decimal",
        "percentage",
        "percent",
        "rate",
        "port"
    ]

    if any(p in t for p in palavras_numericas):
        grupos.append("RESPOSTA NUMÉRICA")

        acoes.append(
            "Obter o valor solicitado e informar somente "
            "o formato exigido pela task."
        )

    # =========================================================
    # 6. HASH
    # =========================================================

    if "hash" in t:
        grupos.append("HASH")

        acoes.append(
            "Obter o hash gerado pelo procedimento/API "
            "e utilizá-lo como resposta."
        )

    # =========================================================
    # 7. URL
    # =========================================================

    if "url" in t:
        grupos.append("URL")

    # =========================================================
    # 8. INVESTIGAÇÃO AWS
    # =========================================================

    palavras_aws = [
        "aws console",
        "lambda console",
        "api gateway console",
        "amazon s3",
        "amazon ec2",
        "amazon rds",
        "dynamodb",
        "iam console",
        "bedrock",
        "sagemaker",
        "cloudwatch"
    ]

    if any(p in t for p in palavras_aws):
        grupos.append("AWS CONSOLE")

        acoes.append(
            "Executar a investigação/configuração no "
            "AWS Console conforme as instruções."
        )

    # =========================================================
    # 9. RESPOSTA DIRETA
    # =========================================================

    palavras_resposta = [
        "answer question",
        "submit your answer",
        "submit answer",
        "put into the textbox",
        "enter the answer",
        "answer to this challenge",
        "answer is"
    ]

    if any(p in t for p in palavras_resposta):
        grupos.append("RESPOSTA DIRETA")

    # =========================================================
    # 10. INVESTIGAÇÃO MANUAL
    # =========================================================

    if not grupos:
        grupos.append("INVESTIGAÇÃO MANUAL")

        acoes.append(
            "Ler a task completa e determinar manualmente "
            "o recurso AWS e o procedimento necessário."
        )

    # Remover duplicados
    grupos = list(dict.fromkeys(grupos))
    acoes = list(dict.fromkeys(acoes))

    return grupos, acoes, perguntas, comandos, trechos


def main():

    print("=" * 80)
    print("AWS JAM - MAPA DE RESOLUÇÃO GLOBAL_STATIC_ANSWER")
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
    print("Tasks encontradas:", len(dados))
    print()

    resumo = {}

    with open(OUTPUT, "w", encoding="utf-8") as out:

        out.write("=" * 100 + "\n")
        out.write("AWS JAM - MAPA DE RESOLUÇÃO GLOBAL_STATIC_ANSWER\n")
        out.write("=" * 100 + "\n\n")

        out.write(
            "OBJETIVO: organizar as 73 GLOBAL_STATIC_ANSWER "
            "por método de resolução.\n\n"
        )

        # =====================================================
        # ANALISA TODAS
        # =====================================================

        resultados = []

        for i, item in enumerate(dados, 1):

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

            grupos, acoes, perguntas, comandos, trechos = classificar(
                item
            )

            resultados.append({
                "challenge": challenge,
                "task": task,
                "title": title,
                "grupos": grupos,
                "acoes": acoes,
                "perguntas": perguntas,
                "comandos": comandos,
                "trechos": trechos
            })

            for grupo in grupos:
                resumo[grupo] = resumo.get(grupo, 0) + 1

            print(
                f"[{i:02d}/{len(dados)}] "
                f"{challenge} | TASK {task} | "
                f"{', '.join(grupos)}"
            )

        # =====================================================
        # RESUMO
        # =====================================================

        out.write("=" * 100 + "\n")
        out.write("RESUMO POR MÉTODO\n")
        out.write("=" * 100 + "\n\n")

        for grupo, quantidade in sorted(
            resumo.items(),
            key=lambda x: (-x[1], x[0])
        ):
            out.write(
                f"{grupo:<30} {quantidade} tasks\n"
            )

        out.write("\n")

        # =====================================================
        # LISTAGEM COMPLETA
        # =====================================================

        out.write("=" * 100 + "\n")
        out.write("MAPA COMPLETO\n")
        out.write("=" * 100 + "\n")

        for i, item in enumerate(resultados, 1):

            out.write("\n")
            out.write("=" * 100 + "\n")
            out.write(
                f"[{i:02d}] {item['challenge']} | "
                f"TASK {item['task']}\n"
            )
            out.write(
                f"TÍTULO: {item['title']}\n"
            )
            out.write("=" * 100 + "\n\n")

            # -------------------------------------------------
            # MÉTODO
            # -------------------------------------------------

            out.write("MÉTODO DE RESOLUÇÃO\n")
            out.write("-" * 60 + "\n")

            for grupo in item["grupos"]:
                out.write(f"- {grupo}\n")

            out.write("\n")

            # -------------------------------------------------
            # AÇÕES
            # -------------------------------------------------

            out.write("PRÓXIMAS AÇÕES\n")
            out.write("-" * 60 + "\n")

            for acao in item["acoes"]:
                out.write(f"- {acao}\n")

            out.write("\n")

            # -------------------------------------------------
            # PERGUNTAS
            # -------------------------------------------------

            out.write("PERGUNTAS / INSTRUÇÕES\n")
            out.write("-" * 60 + "\n")

            if item["perguntas"]:

                for pergunta in item["perguntas"]:
                    out.write(f"- {pergunta}\n")

            else:
                out.write("- Nenhuma detectada\n")

            out.write("\n")

            # -------------------------------------------------
            # COMANDOS
            # -------------------------------------------------

            out.write("COMANDOS\n")
            out.write("-" * 60 + "\n")

            if item["comandos"]:

                for comando in item["comandos"]:
                    out.write(f"- {comando}\n")

            else:
                out.write("- Nenhum detectado\n")

            out.write("\n")

            # -------------------------------------------------
            # TRECHOS
            # -------------------------------------------------

            out.write("TRECHOS RELACIONADOS\n")
            out.write("-" * 60 + "\n")

            if item["trechos"]:

                for trecho in item["trechos"]:
                    out.write(f"- {trecho}\n")

            else:
                out.write("- Nenhum detectado\n")

            out.write("\n")

    print()
    print("=" * 80)
    print("MAPA GERADO COM SUCESSO")
    print("=" * 80)
    print()
    print("Tasks analisadas:", len(dados))
    print("Arquivo:")
    print(OUTPUT)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()