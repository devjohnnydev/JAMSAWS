import json
import os
import re

INPUT = "output/global_static_analysis.json"
RAW = "output/challenges_raw.json"
OUTPUT = "output/resolver_tasks.txt"


def carregar_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def classificar_task(texto):
    t = texto.lower()

    categorias = []

    palavras = {
        "cloudwatch": [
            "cloudwatch",
            "logs",
            "log group",
            "log stream"
        ],
        "lambda": [
            "lambda",
            "function",
            "invoke"
        ],
        "api_gateway": [
            "api gateway",
            "api gateway",
            "endpoint",
            "api stage"
        ],
        "ec2": [
            "ec2",
            "instance",
            "security group",
            "private ip",
            "public ip"
        ],
        "s3": [
            "s3",
            "bucket",
            "object"
        ],
        "iam": [
            "iam",
            "role",
            "policy",
            "principal",
            "arn"
        ],
        "dynamodb": [
            "dynamodb",
            "table"
        ],
        "rds": [
            "rds",
            "database"
        ],
        "sagemaker": [
            "sagemaker",
            "notebook",
            "endpoint"
        ],
        "quicksight": [
            "quicksight",
            "quick",
            "dataset",
            "dashboard"
        ],
        "bedrock": [
            "bedrock",
            "foundation model"
        ],
        "network": [
            "vpc",
            "subnet",
            "route table",
            "security group",
            "network"
        ]
    }

    for categoria, termos in palavras.items():
        if any(termo in t for termo in termos):
            categorias.append(categoria)

    if not categorias:
        categorias.append("investigacao_manual")

    return categorias


def extrair_urls(texto):
    return re.findall(r'https?://[^\s<>"\')]+', texto)


def extrair_ips(texto):
    padrao = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return sorted(set(re.findall(padrao, texto)))


def extrair_arns(texto):
    padrao = r'arn:aws:[A-Za-z0-9:/_.+\-=]+'
    return sorted(set(re.findall(padrao, texto)))


def localizar_tasks(raw):
    resultado = {}

    for item in raw:
        data = item.get("data", {})

        latest = data.get("latest", {})
        props = latest.get("props", {})

        tasks = props.get("tasks", [])

        for task in tasks:
            task_id = task.get("id")

            resultado[task_id] = {
                "challenge": item.get("challengeId")
                    or item.get("id")
                    or item.get("slug")
                    or data.get("slug"),
                "task": task
            }

    return resultado


def main():

    analysis = carregar_json(INPUT)
    raw = carregar_json(RAW)

    raw_tasks = localizar_tasks(raw)

    linhas = []

    linhas.append("=" * 100)
    linhas.append("AWS JAM - RESOLVER GLOBAL_STATIC_ANSWER")
    linhas.append("=" * 100)
    linhas.append(f"TOTAL DE TASKS: {len(analysis)}")
    linhas.append("")
    linhas.append(
        "Este relatório organiza as evidências disponíveis para investigação."
    )
    linhas.append("")

    for indice, item in enumerate(analysis, 1):

        challenge = item.get("challengeId", "N/D")
        task_number = item.get("taskNumber", "N/D")
        title = item.get("title", "SEM TÍTULO")

        task_id = item.get("taskId") or item.get("id")

        raw_info = raw_tasks.get(task_id, {})
        task = raw_info.get("task", {})

        content = task.get("content", "")

        if not content:
            content = item.get("conteudo_completo", "")

        categorias = classificar_task(content)

        urls = extrair_urls(content)
        ips = extrair_ips(content)
        arns = extrair_arns(content)

        linhas.append("")
        linhas.append("=" * 100)
        linhas.append(f"[{indice:02d}] {challenge}")
        linhas.append(f"TASK: {task_number}")
        linhas.append(f"TÍTULO: {title}")
        linhas.append("=" * 100)

        linhas.append("")
        linhas.append("CLASSIFICAÇÃO")
        linhas.append("-" * 40)

        for categoria in categorias:
            linhas.append(f"- {categoria}")

        linhas.append("")
        linhas.append("PERGUNTAS / INSTRUÇÕES")
        linhas.append("-" * 40)

        perguntas = item.get("perguntas_detectadas", [])

        if perguntas:
            for pergunta in perguntas:
                linhas.append(f"- {pergunta}")
        else:
            linhas.append("- Nenhuma pergunta estruturada detectada")

        linhas.append("")
        linhas.append("COMANDOS")
        linhas.append("-" * 40)

        comandos = item.get("comandos_detectados", [])

        if comandos:
            for comando in comandos:
                linhas.append(f"- {comando}")
        else:
            linhas.append("- Nenhum comando detectado")

        linhas.append("")
        linhas.append("URLs")
        linhas.append("-" * 40)

        if urls:
            for url in urls:
                linhas.append(f"- {url}")
        else:
            linhas.append("- Nenhuma")

        linhas.append("")
        linhas.append("IPS")
        linhas.append("-" * 40)

        if ips:
            for ip in ips:
                linhas.append(f"- {ip}")
        else:
            linhas.append("- Nenhum")

        linhas.append("")
        linhas.append("ARNS")
        linhas.append("-" * 40)

        if arns:
            for arn in arns:
                linhas.append(f"- {arn}")
        else:
            linhas.append("- Nenhum")

        linhas.append("")
        linhas.append("CONTEÚDO COMPLETO DA TASK")
        linhas.append("-" * 40)

        if content:
            linhas.append(content)
        else:
            linhas.append("CONTEÚDO NÃO LOCALIZADO")

        linhas.append("")

    os.makedirs("output", exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print("=" * 80)
    print("RESOLVER TASKS FINALIZADO")
    print("=" * 80)
    print(f"Tasks analisadas: {len(analysis)}")
    print(f"Arquivo: {OUTPUT}")
    print("=" * 80)


if __name__ == "__main__":
    main()