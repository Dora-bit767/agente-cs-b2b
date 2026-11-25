import httpx

from langchain.tools import tool
from pydantic import BaseModel, Field

from agent.config import SAAS_API_URL

class BuscarEmpresaInput(BaseModel):
    nome: str = Field(
        description="Nome fantasia ou parte do nome da empresa que deseja localizar."
    )


class ConsultarAssinaturaInput(BaseModel):
    empresa_id: int = Field(
        description="ID da empresa cuja assinatura será consultada."
    )

class AdicionarCreditosInput(BaseModel):
    assinaturas_id: int = Field(
        description="ID da assinatura que receberá os créditos."
    )
    quantidade: int = Field(
        gt=0,
        le=3000,
        description="Quantidade de créditos a adicionar, entre 1 e 3000."
    )
    motivo: str = Field(
        min_length=3,
        description="Justificativa para a adição dos créditos."
    )

@tool(args_schema=BuscarEmpresaInput)
def buscar_empresa(nome: str) -> dict:
    """Busca empresas pelo nome fantasia na API SaaS."""

    try:
        resposta = httpx.get(
            f"{SAAS_API_URL}/empresas",
            params={"nome": nome},
            timeout=10.0
        )

        resposta.raise_for_status()

        empresas = resposta.json()

        if not empresas:
            return {
                "status": "nao_encontrada",
                "mensagem": f"Nenhuma empresa encontrada com o nome: {nome}"
            }

        if len(empresas) > 1:
            return {
                "status": "ambigua",
                "quantidade": len(empresas),
                "mensagem": "Mais de uma empresa encontrada. É necessário escolher uma.",
                "empresas": empresas
            }

        return {
            "status": "encontrada",
            "quantidade": 1,
            "empresas": empresas
        }

    except httpx.TimeoutException:
        return {
            "status": "erro",
            "mensagem": "A API demorou demais para responder."
        }

    except httpx.HTTPStatusError as erro:
        return {
            "status": "erro",
            "mensagem": f"Erro HTTP: {erro.response.status_code}"
        }

    except httpx.RequestError:
        return {
            "status": "erro",
            "mensagem": "Não foi possível conectar à API SaaS."
        }
@tool(args_schema=ConsultarAssinaturaInput)
def consultar_assinatura(empresa_id: int) -> dict:
    """Consulta a assinatura de uma empresa na API SaaS."""

    try:
        resposta = httpx.get(
            f"{SAAS_API_URL}/assinaturas/{empresa_id}",
            timeout=10.0
        )

        resposta.raise_for_status()

        assinatura = resposta.json()

        return {
            "status": "consultada",
            "assinatura": assinatura
        }

    except httpx.TimeoutException:
        return {
            "status": "erro",
            "mensagem": "A API demorou demais para responder."
        }

    except httpx.HTTPStatusError as erro:
        return {
            "status": "erro",
            "mensagem": f"Erro HTTP: {erro.response.status_code}"
        }

    except httpx.RequestError:
        return {
            "status": "erro",
            "mensagem": "Não foi possível conectar à API SaaS."
        }

@tool(args_schema=AdicionarCreditosInput)
def adicionar_creditos(
    assinaturas_id: int,
    quantidade: int,
    motivo: str
) -> dict:
    """Adiciona créditos à assinatura de uma empresa na API SaaS."""

    try:
        resposta = httpx.post(
            f"{SAAS_API_URL}/assinaturas/{assinaturas_id}/creditos",
            json={
                "quantidade": quantidade,
                "motivo": motivo
            },
            timeout=10.0
        )

        resposta.raise_for_status()

        assinatura = resposta.json()

        return {
            "status": "sucesso",
            "mensagem": "Créditos adicionados com sucesso.",
            "assinatura": assinatura
        }

    except httpx.TimeoutException:
        return {
            "status": "erro",
            "mensagem": "A API demorou demais para responder."
        }

    except httpx.HTTPStatusError as erro:
        return {
            "status": "erro",
            "mensagem": f"Erro HTTP: {erro.response.status_code}"
        }

    except httpx.RequestError:
        return {
            "status": "erro",
            "mensagem": "Não foi possível conectar à API SaaS."
        }