from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    # Histórico de mensagens
    messages: Annotated[list[AnyMessage], add_messages]

    # Dados da empresa
    nome_empresa: str
    empresa_id: int

    # Dados da assinatura
    assinatura_id: int
    assinatura: dict[str, Any] | list[dict[str, Any]]

    # Dados da operação
    quantidade_creditos: int
    motivo: str

    # Resultado do processamento
    status: str
    resultado: str