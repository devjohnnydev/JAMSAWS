import json
import re
from pathlib import Path

INPUT = Path("output/global_static_analysis.json")
OUTPUT = Path("output/validacoes_global_static.txt")

with open(INPUT, "r", encoding="utf-8") as f:
    dados = json.load(f)

print("=" * 80)
print("EXTRAINDO PROCEDIMENTOS DE VALIDAÇÃO")
print("=" * 80)

with open(OUTPUT, "w", encoding="utf-8") as out:

    out.write("=" * 100 + "\n")
    out.write("AWS JAM - MAPA DE VALIDAÇÃO GLOBAL_STATIC_ANSWER\n")
    out.write("=" * 100 + "\n\n")

    for i, item in enumerate(dados, 1):

        challenge = (
            item.get("challengeId")
            or item.get("challenge")
            or item.get("challenge_id")
            or "DESCONHECIDO"
        )

        task = item.get("taskNumber") or item.get("task") or "?"

        title = item.get("title") or "SEM TÍTULO"

        perguntas = item.get("perguntas_detectadas", [])
        comandos = item.get("comandos_detectados", [])
        trechos = (
            item.get("trechos_relacionados")
            or item.get("trechos_resposta")
            or []
        )

        texto = " ".join(
            str(x)
            for x in (
                perguntas +
                comandos +
                trechos
            )
        )

        texto_lower = texto.lower()

        # =====================================================
        # DETECTA PROPRIEDADES
        # =====================================================

        propriedades = []

        padroes = [
            r"\b\w*CheckChallengeAnswerURL\w*\b",
            r"\b\w*ValidateAPIURL\w*\b",
            r"\b\w*SalesAPIURL\w*\b",
            r"\b\w*OutputProperty\w*\b",
            r"\b\w*URL\b",
        ]

        for padrao in padroes:
            encontrados = re.findall(
                padrao,
                texto,
                flags=re.IGNORECASE
            )

            for x in encontrados:
                if x not in propriedades:
                    propriedades.append(x)

        # =====================================================
        # TIPO DE VALIDAÇÃO
        # =====================================================

        tipos = []

        if "checkchallengeanswerurl" in texto_lower:
            tipos.append("CHECK CHALLENGE ANSWER")

        if "validateapiurl" in texto_lower:
            tipos.append("VALIDATE API")

        if "cloudwatch" in texto_lower:
            tipos.append("CLOUDWATCH")

        if "output properties" in texto_lower:
            tipos.append("OUTPUT PROPERTIES")

        if not tipos:
            tipos.append("INVESTIGAÇÃO MANUAL")

        # =====================================================
        # AÇÕES
        # =====================================================

        acoes = []

        if "checkchallengeanswerurl" in texto_lower:
            acoes.append(
                "Resolver a configuração solicitada e acessar "
                "CheckChallengeAnswerURL"
            )

        if "validateapiurl" in texto_lower:
            acoes.append(
                "Resolver a aplicação e chamar ValidateAPIURL"
            )

        if "cloudwatch" in texto_lower:
            acoes.append(
                "Consultar CloudWatch Logs"
            )

        if "output properties" in texto_lower:
            acoes.append(
                "Consultar Output Properties no JAM"
            )

        if "curl" in texto_lower:
            acoes.append(
                "Executar o curl indicado pela task"
            )

        if not acoes:
            acoes.append(
                "Ler instruções e investigar manualmente"
            )

        # =====================================================
        # ESCREVE
        # =====================================================

        out.write("=" * 100 + "\n")
        out.write(
            f"[{i:02d}] {challenge} | TASK {task}\n"
        )
        out.write(f"TÍTULO: {title}\n")
        out.write("=" * 100 + "\n\n")

        out.write("TIPO\n")
        out.write("-" * 50 + "\n")

        for tipo in tipos:
            out.write(f"- {tipo}\n")

        out.write("\n")

        out.write("PROPRIEDADES / URLs DETECTADAS\n")
        out.write("-" * 50 + "\n")

        if propriedades:
            for p in propriedades:
                out.write(f"- {p}\n")
        else:
            out.write("- Nenhuma\n")

        out.write("\n")

        out.write("PRÓXIMAS AÇÕES\n")
        out.write("-" * 50 + "\n")

        for acao in acoes:
            out.write(f"- {acao}\n")

        out.write("\n")

        out.write("INSTRUÇÕES ENCONTRADAS\n")
        out.write("-" * 50 + "\n")

        for pergunta in perguntas:
            out.write(f"- {pergunta}\n")

        out.write("\n")

        out.write("COMANDOS\n")
        out.write("-" * 50 + "\n")

        if comandos:
            for comando in comandos:
                out.write(f"- {comando}\n")
        else:
            out.write("- Nenhum\n")

        out.write("\n")

        print(
            f"[{i:02d}/{len(dados)}] "
            f"{challenge} | TASK {task} | "
            f"{', '.join(tipos)}"
        )

print()
print("=" * 80)
print("FINALIZADO")
print("=" * 80)
print(f"Arquivo: {OUTPUT}")