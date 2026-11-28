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

def executar_adicao_creditos(state: AgentState) -> dict:
    """Executa a adição de créditos após todas as validações."""

    resultado = adicionar_creditos.invoke({
        "assinaturas_id": state["assinatura_id"],
        "quantidade": state["quantidade_creditos"],
        "motivo": state["motivo"]
    })

    if resultado["status"] != "sucesso":
        return {
            "status": "erro_adicao",
            "resultado": resultado.get(
                "mensagem",
                "Não foi possível adicionar os créditos."
            )
        }

    return {
        "status": "sucesso",
        "resultado": resultado["mensagem"],
        "assinatura": resultado["assinatura"]
    }
def decidir_apos_localizar(state: AgentState) -> str:
    if state.get("status") == "empresa_encontrada":
        return "continuar"
    return "encerrar"


def decidir_apos_consultar(state: AgentState) -> str:
    if state.get("status") != "assinatura_consultada":
        return "encerrar"

    if state.get("quantidade_creditos") is None:
        return "encerrar"

    return "continuar"


def decidir_apos_validar_assinatura(state: AgentState) -> str:
    if state.get("status") == "assinatura_validada":
        return "continuar"
    return "encerrar"


def decidir_apos_validar_solicitacao(state: AgentState) -> str:
    if state.get("status") == "solicitacao_validada":
        return "continuar"
    return "encerrar"

def criar_grafo():
    fluxo = StateGraph(AgentState)

    fluxo.add_node("localizar_empresa", localizar_empresa)
    fluxo.add_node("consultar_assinatura", consultar_dados_assinatura)
    fluxo.add_node("validar_assinatura", validar_assinatura)
    fluxo.add_node("validar_solicitacao", validar_solicitacao_creditos)
    fluxo.add_node("adicionar_creditos", executar_adicao_creditos)

    fluxo.set_entry_point("localizar_empresa")

    fluxo.add_conditional_edges(
        "localizar_empresa",
        decidir_apos_localizar,
        {
            "continuar": "consultar_assinatura",
            "encerrar": END
        }
    )

    fluxo.add_conditional_edges(
        "consultar_assinatura",
        decidir_apos_consultar,
        {
            "continuar": "validar_assinatura",
            "encerrar": END
        }
    )

    fluxo.add_conditional_edges(
        "validar_assinatura",
        decidir_apos_validar_assinatura,
        {
            "continuar": "validar_solicitacao",
            "encerrar": END
        }
    )

    fluxo.add_conditional_edges(
        "validar_solicitacao",
        decidir_apos_validar_solicitacao,
        {
            "continuar": "adicionar_creditos",
            "encerrar": END
        }
    )

    fluxo.add_edge("adicionar_creditos", END)

    return fluxo.compile()

