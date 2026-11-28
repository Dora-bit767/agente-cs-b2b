from fastapi import FastAPI
from pydantic import BaseModel, Field

from agent.graph import criar_grafo
from agent.intent import identificar_intencao
from agent.llm import assistente_cs


app = FastAPI(
    title="Agente de Customer Success B2B",
    description="Agente inteligente para operações de Customer Success.",
    version="1.0.0"
)

grafo = criar_grafo()


class SolicitacaoAgente(BaseModel):
    mensagem: str | None = None
    nome_empresa: str | None = None
    quantidade_creditos: int | None = Field(default=None, gt=0)
    motivo: str | None = None


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "mensagem": "Agente de Customer Success disponível."
    }


@app.post("/agent/executar")
def executar_agente(solicitacao: SolicitacaoAgente):

    if solicitacao.nome_empresa:
        estado_inicial = {
            "nome_empresa": solicitacao.nome_empresa,
            "quantidade_creditos": solicitacao.quantidade_creditos,
            "motivo": solicitacao.motivo or ""
        }

        resultado = grafo.invoke(estado_inicial)

        return {
            "tipo": "operacional",
            "status": resultado.get("status"),
            "empresa": solicitacao.nome_empresa,
            "resultado": resultado.get("resultado"),
            "assinatura": resultado.get("assinatura")
        }

    if solicitacao.mensagem:
        intencao = identificar_intencao(solicitacao.mensagem)

        if intencao.tipo == "geral":
            resposta = assistente_cs.invoke({
                "mensagem": solicitacao.mensagem
            })

            return {
                "tipo": "orientacao",
                "status": "sucesso",
                "resultado": resposta.content
            }

        if not intencao.nome_empresa:
            return {
                "tipo": "operacional",
                "status": "esclarecimento_necessario",
                "resultado": "Qual é o nome da empresa?"
            }

        if intencao.tipo == "consultar_empresa":
            resultado = grafo.invoke({
                "nome_empresa": intencao.nome_empresa
            })

            return {
                "tipo": "operacional",
                "status": resultado.get("status"),
                "empresa": intencao.nome_empresa,
                "resultado": resultado.get("resultado"),
                "assinatura": resultado.get("assinatura")
            }

        if intencao.tipo == "adicionar_creditos":
            if not intencao.acao_explicita:
                return {
                    "tipo": "operacional",
                    "status": "autorizacao_necessaria",
                    "resultado": "Confirme explicitamente se deseja adicionar os créditos."
                }

            if (
                intencao.quantidade_creditos is None
                or not intencao.motivo
            ):
                return {
                    "tipo": "operacional",
                    "status": "esclarecimento_necessario",
                    "resultado": (
                        "Informe a quantidade de créditos e o motivo da solicitação."
                    )
                }

            resultado = grafo.invoke({
                "nome_empresa": intencao.nome_empresa,
                "quantidade_creditos": intencao.quantidade_creditos,
                "motivo": intencao.motivo
            })

            return {
                "tipo": "operacional",
                "status": resultado.get("status"),
                "empresa": intencao.nome_empresa,
                "resultado": resultado.get("resultado"),
                "assinatura": resultado.get("assinatura")
            }

    return {
        "status": "erro",
        "resultado": "Informe uma mensagem ou o nome da empresa."
    }
