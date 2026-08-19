"""
auth.py — Autenticação com a API de progresso do Jam (ex.: AWS Jam / Skill Builder).

Mantém os headers/token fora do main.py para não vazar credenciais em logs
e para poder trocar de provedor de eventos (AWS Jam, plataforma própria, etc.)
sem tocar na lógica de negócio.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class JamCredentials:
    host: str
    token: str

    @property
    def headers(self) -> dict:
        return {
            "host": self.host,
            "x-aws-wai-token": self.token,  # nome do header visto no seu print
            "content-type": "application/json",
        }


def load_credentials() -> JamCredentials:
    host = os.environ["JAM_API_HOST"]
    token = os.environ["JAM_API_TOKEN"]
    if not host or not token:
        raise RuntimeError("Defina JAM_API_HOST e JAM_API_TOKEN no .env")
    return JamCredentials(host=host, token=token)
