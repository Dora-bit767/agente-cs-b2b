from fastapi import FastAPI

app = FastAPI(
    title="Agente de Customer Success B2B",
    description="Agente inteligente para operações de Customer Success.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "mensagem": "Agente de Customer Success disponível."
    }

from agent.graph import criar_grafo

grafo = criar_grafo()

from pydantic import BaseModel, Field


class SolicitacaoAgente(BaseModel):
    nome_empresa: str = Field(min_length=2)
    quantidade_creditos: int | None = Field(default=None, gt=0)
    motivo: str | None = None

@app.post("/agent/executar")
def executar_agente(solicitacao: SolicitacaoAgente):

    estado_inicial = {
        "nome_empresa": solicitacao.nome_empresa,
        "quantidade_creditos": solicitacao.quantidade_creditos,
        "motivo": solicitacao.motivo or ""
    }

    resultado = grafo.invoke(estado_inicial)

    return {
        "status": resultado.get("status"),
        "empresa": solicitacao.nome_empresa,
        "resultado": resultado.get("resultado"),
        "assinatura": resultado.get("assinatura")
    }
