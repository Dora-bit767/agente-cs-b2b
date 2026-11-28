from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from agent.config import GROQ_API_KEY, LLM_MODEL
from agent.prompts.system_prompt import SYSTEM_PROMPT


def criar_modelo():
    if not GROQ_API_KEY:
        raise ValueError("A chave GROQ_API_KEY não foi configurada.")

    return ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY,
        temperature=0
    )


llm = criar_modelo()

prompt_cs = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{mensagem}")
])

assistente_cs = prompt_cs | llm