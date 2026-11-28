from typing import Literal

from pydantic import BaseModel, Field

from agent.llm import llm


class IntencaoSolicitacao(BaseModel):
    tipo: Literal[
        "geral",
        "consultar_empresa",
        "adicionar_creditos"
    ] = Field(description="Tipo de solicitação do usuário")

    nome_empresa: str | None = Field(
        default=None,
        description="Nome da empresa mencionada"
    )

    quantidade_creditos: int | None = Field(
        default=None,
        description="Quantidade de créditos solicitada"
    )

    motivo: str | None = Field(
        default=None,
        description="Motivo informado para adicionar créditos"
    )

    acao_explicita: bool = Field(
        default=False,
        description="Verdadeiro somente quando o usuário pedir explicitamente a ação"
    )


classificador = llm.with_structured_output(IntencaoSolicitacao)


def identificar_intencao(mensagem: str) -> IntencaoSolicitacao:
    prompt = f"""
    Classifique a solicitação do usuário.

    Regras:
    - geral: dúvidas e orientações gerais sobre Customer Success.
    - consultar_empresa: pedido para localizar ou consultar uma empresa,
      assinatura, plano ou saldo de créditos.
    - adicionar_creditos: pedido explícito para adicionar créditos.
    - Nunca classifique como adicionar_creditos apenas uma pergunta
      sobre como funciona a adição de créditos.
    - Extraia o nome da empresa, a quantidade e o motivo, quando informados.
    - acao_explicita deve ser True somente quando o usuário pedir
      claramente que os créditos sejam adicionados.

    Mensagem: {mensagem}
    """

    return classificador.invoke(prompt)