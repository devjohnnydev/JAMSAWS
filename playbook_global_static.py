import json
import re

INPUT = "output/global_static_analysis.json"
OUTPUT = "output/global_static_playbook.txt"


def carregar():
    with open(INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def classificar(texto):
    t = texto.lower()

    regras = {
        "CLOUDWATCH": ["cloudwatch", "logs", "log group", "log stream"],
        "LAMBDA": ["lambda", "function", "invoke"],
        "API_GATEWAY": ["api gateway", "api endpoint", "api stage"],
        "S3": ["amazon s3", "s3 bucket", "s3"],
        "EC2": ["ec2", "instance", "private ip", "public ip"],
        "IAM": ["iam", "role", "policy", "principal arn"],
        "BEDROCK": ["bedrock", "knowledge base", "retrieveandgenerate"],
        "SAGEMAKER": ["sagemaker", "jupyter notebook"],
        "QUICKSIGHT": ["quicksight", "amazon quick", "dataset"],
        "DYNAMODB": ["dynamodb"],
        "RDS": ["rds", "database"],
        "VPC_NETWORK": ["vpc", "subnet", "route table", "security group"],
    }

    encontrados = []

    for nome, termos in regras.items():
        if any(t in termo for termo in termos):
            encontrados.append(nome)

    return encontrados or ["INVESTIGAÇÃO MANUAL"]


def detectar_formato(texto):
    t = texto.lower()

    formatos = []

    if "two decimal" in t or "two decimal" in t or "2 decimal" in t:
        formatos.append("Número com 2 casas decimais")

    if "without" in t and "$" in t:
        formatos.append("Sem símbolo $")

    if "ip address" in t or "private ip" in t or "public ip" in t:
        formatos.append("Endereço IP")

    if "arn" in t:
        formatos.append("ARN")

    if "port" in t:
        formatos.append("Número de porta")

    if "url" in t:
        formatos.append("URL")

    return formatos


def detectar_origem(texto):
    t = texto.lower()

    origens = []

    if "cloudwatch" in t or "cloudwatch logs" in t:
        origens.append("CloudWatch Logs")

    if "output properties" in t:
        origens.append("JAM Output Properties")

    if "checkchallengeanswerurl" in t:
        origens.append("CheckChallengeAnswerURL")

    if "cloudfront" in t:
        origens.append("Amazon CloudFront")

    if "chatbot" in t:
        origens.append("Aplicação/Chatbot")

    if "jupyter" in t or "notebook" in t:
        origens.append("Jupyter/SageMaker")

    if "command" in t or "run the following" in t:
        origens.append("Comando indicado pela própria task")

    return origens


def main():

    dados = carregar()

    linhas = []

    linhas.append("=" * 100)
    linhas.append("AWS JAM - GLOBAL STATIC PLAYBOOK")
    linhas.append("=" * 100)
    linhas.append("")
    linhas.append(f"TOTAL DE TASKS: {len(dados)}")
    linhas.append("")
    linhas.append(
        "Objetivo: organizar a investigação de cada GLOBAL_STATIC_ANSWER."
    )
    linhas.append(
        "As respostas não são inventadas; devem ser obtidas conforme as instruções da task."
    )
    linhas.append("")

    for i, item in enumerate(dados, 1):

        challenge = item.get("challengeId", "N/D")
        task_number = item.get("taskNumber", "N/D")
        title = item.get("title", "SEM TÍTULO")

        perguntas = item.get("perguntas_detectadas", [])
        comandos = item.get("comandos_detectados", [])

        conteudo = item.get("conteudo_completo", "")

        if not conteudo:
            conteudo = " ".join(perguntas + comandos)

        servicos = classificar(conteudo)
        formatos = detectar_formato(conteudo)
        origens = detectar_origem(conteudo)

        linhas.append("=" * 100)
        linhas.append(f"[{i:02d}] {challenge}")
        linhas.append(f"TASK: {task_number}")
        linhas.append(f"TÍTULO: {title}")
        linhas.append("=" * 100)

        linhas.append("")
        linhas.append("SERVIÇOS / ÁREAS")
        linhas.append("-" * 50)

        for x in servicos:
            linhas.append(f"- {x}")

        linhas.append("")
        linhas.append("ONDE PROCURAR A RESPOSTA")
        linhas.append("-" * 50)

        if origens:
            for x in origens:
                linhas.append(f"- {x}")
        else:
            linhas.append("- Determinar durante a execução da task")

        linhas.append("")
        linhas.append("FORMATO DA RESPOSTA")
        linhas.append("-" * 50)

        if formatos:
            for x in formatos:
                linhas.append(f"- {x}")
        else:
            linhas.append("- Não identificado automaticamente")

        linhas.append("")
        linhas.append("PERGUNTAS / INSTRUÇÕES")
        linhas.append("-" * 50)

        if perguntas:
            for p in perguntas:
                linhas.append(f"- {p}")
        else:
            linhas.append("- Nenhuma detectada")

        linhas.append("")
        linhas.append("COMANDOS / PROCEDIMENTOS DETECTADOS")
        linhas.append("-" * 50)

        if comandos:
            for c in comandos:
                linhas.append(f"- {c}")
        else:
            linhas.append("- Nenhum detectado")

        linhas.append("")
        linhas.append("PRÓXIMA AÇÃO")
        linhas.append("-" * 50)

        if "CheckChallengeAnswerURL" in conteudo:
            linhas.append(
                "1. Execute e corrija a configuração descrita pela task."
            )
            linhas.append(
                "2. Consulte o CheckChallengeAnswerURL indicado no Output Properties."
            )
        elif "CloudWatch" in conteudo or "cloudwatch" in conteudo.lower():
            linhas.append(
                "1. Execute/resolva a configuração solicitada."
            )
            linhas.append(
                "2. Consulte os CloudWatch Logs indicados pela task."
            )
        elif "chatbot" in conteudo.lower():
            linhas.append(
                "1. Configure a aplicação conforme a task."
            )
            linhas.append(
                "2. Teste a pergunta indicada."
            )
            linhas.append(
                "3. Use o resultado como resposta."
            )
        else:
            linhas.append(
                "1. Ler as instruções da task."
            )
            linhas.append(
                "2. Executar a investigação no serviço AWS indicado."
            )
            linhas.append(
                "3. Capturar o valor solicitado."
            )

        linhas.append("")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print("=" * 80)
    print("PLAYBOOK GERADO")
    print("=" * 80)
    print(f"Tasks: {len(dados)}")
    print(f"Arquivo: {OUTPUT}")
    print("=" * 80)


if __name__ == "__main__":
    main()