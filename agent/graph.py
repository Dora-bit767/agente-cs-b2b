from langgraph.graph import StateGraph, END

from agent.state import AgentState

from agent.tools import (
    buscar_empresa,
    consultar_assinatura,
    adicionar_creditos
)


def localizar_empresa(state: AgentState) -> dict:
    """Localiza a empresa pelo nome informado."""

    nome = state.get("nome_empresa", "")

    resultado = buscar_empresa.invoke({
        "nome": nome
    })

    if resultado["status"] != "encontrada":
        return {
            "status": resultado["status"],
            "resultado": resultado.get(
                "mensagem",
                "Não foi possível localizar a empresa."
            )
        }

    empresa = resultado["empresas"][0]

    return {
        "empresa_id": empresa["id"],
        "status": "empresa_encontrada",
        "resultado": f"Empresa localizada: {empresa['nome_fantasia']}"
    }
def consultar_dados_assinatura(state: AgentState) -> dict:
    """Consulta os dados da assinatura da empresa."""

    empresa_id = state.get("empresa_id")

    resultado = consultar_assinatura.invoke({
        "empresa_id": empresa_id
    })

    if resultado["status"] != "consultada":
        return {
            "status": "erro_assinatura",
            "resultado": resultado.get(
                "mensagem",
                "Não foi possível consultar a assinatura."
            )
        }

    assinaturas = resultado["assinatura"]

    if not assinaturas:
        return {
            "status": "sem_assinatura",
            "resultado": "A empresa não possui assinatura cadastrada."
        }

    if len(assinaturas) > 1:
        return {
            "status": "assinatura_ambigua",
            "resultado": "A empresa possui mais de uma assinatura."
        }

    assinatura = assinaturas[0]

    return {
        "assinatura_id": assinatura["id"],
        "assinatura": assinatura,
        "status": "assinatura_consultada",
        "resultado": (
            f"Plano: {assinatura['plano']} | "
            f"Status: {assinatura['status']} | "
            f"Saldo: {assinatura['saldo_creditos_api']} créditos"
        )
    }
def validar_assinatura(state: AgentState) -> dict:
    """Verifica se a assinatura permite adicionar créditos."""

    assinatura = state.get("assinatura")

    if not assinatura:
        return {
            "status": "sem_assinatura",
            "resultado": "Não existe assinatura para validar."
        }

    if assinatura["status"].upper() != "ATIVA":
        return {
            "status": "assinatura_inativa",
            "resultado": "A assinatura está inativa. Não é permitido adicionar créditos."
        }

    if assinatura["saldo_creditos_api"] <= 0:
        return {
            "status": "sem_creditos",
            "resultado": "A assinatura não possui saldo de créditos."
        }

    return {
        "status": "assinatura_validada",
        "resultado": "Assinatura ativa e apta para receber créditos."
    }
def validar_solicitacao_creditos(state: AgentState) -> dict:
    """Valida a quantidade e o motivo da solicitação de créditos."""

    quantidade = state.get("quantidade_creditos")
    motivo = state.get("motivo", "").strip()

    if state.get("status") != "assinatura_validada":
        return {
            "status": "operacao_bloqueada",
            "resultado": "A assinatura precisa ser validada antes da operação."
        }

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return {
            "status": "quantidade_invalida",
            "resultado": "A quantidade de créditos deve ser um número inteiro."
        }

    if quantidade <= 0:
        return {
            "status": "quantidade_invalida",
            "resultado": "A quantidade deve ser maior que zero."
        }

    if quantidade > 3000:
        return {
            "status": "limite_excedido",
            "resultado": "O limite máximo é de 3.000 créditos por operação."
        }

    if len(motivo) < 3:
        return {
            "status": "motivo_invalido",
            "resultado": "Informe um motivo com pelo menos 3 caracteres."
        }

    return {
        "status": "solicitacao_validada",
        "resultado": f"Solicitação validada: {quantidade} créditos. Motivo: {motivo}"
    }