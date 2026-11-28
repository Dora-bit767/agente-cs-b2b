
# Agente de Customer Success B2B

## 1. Sobre o projeto

Projeto de desenvolvimento de um agente inteligente para apoiar operações de Customer Success em empresas SaaS.

O agente utiliza inteligência artificial para interpretar solicitações em linguagem natural e encaminhá-las para orientações gerais ou operações relacionadas às empresas e suas assinaturas.

## 2. Objetivos

- Responder dúvidas sobre Customer Success.
- Identificar a intenção das solicitações.
- Consultar empresas cadastradas.
- Consultar informações de assinaturas.
- Verificar condições para adição de créditos.
- Aplicar validações antes de executar operações.

## 3. Tecnologias utilizadas

- Python
- FastAPI
- LangChain
- LangGraph
- Groq
- Pydantic
- PostgreSQL
- Docker

## 4. Arquitetura do projeto

### Agent

Contém a lógica do agente:

- `graph.py`: fluxo de execução com LangGraph.
- `state.py`: estrutura de estado do agente.
- `tools.py`: ferramentas de consulta e operações.
- `intent.py`: classificação das intenções do usuário.
- `llm.py`: integração com o modelo de linguagem.
- `prompts/`: instruções de comportamento do agente.

### API

- `api/main.py`: disponibiliza os endpoints para interação com o agente.

## 5. Configuração

Crie um ambiente virtual Python:

```powershell
python -m venv venv
```

Ative o ambiente:

```powershell
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Configure as variáveis de ambiente utilizando o arquivo `.env.example` como referência.

Não compartilhe sua chave de API ou o arquivo `.env`.

## 6. Executar a API

Na raiz do projeto, execute:

```powershell
uvicorn api.main:app --reload --port 8000
```

Documentação interativa:

http://127.0.0.1:8000/docs

Verificação de saúde:

http://127.0.0.1:8000/health

## 7. Fluxo de funcionamento

O agente identifica a intenção da mensagem e encaminha a solicitação:

1. Orientações gerais de Customer Success.
2. Consulta de empresas e assinaturas.
3. Solicitações de adição de créditos.

As operações passam pelo fluxo de validação do LangGraph.

## 8. Segurança

O agente possui validações para operações de adição de créditos, incluindo:

- Verificação da existência da empresa.
- Consulta da assinatura.
- Verificação do status da assinatura.
- Validação da quantidade solicitada.
- Limite máximo de 3.000 créditos por solicitação.
- Validação do motivo da operação.

O modelo de linguagem não executa diretamente alterações no banco de dados.

## 9. Status do desenvolvimento

- [x] Estrutura inicial do projeto.
- [x] Ferramentas de consulta e operações.
- [x] Fluxo de validação com LangGraph.
- [x] Integração com Groq.
- [x] Classificação de intenções.
- [x] Integração com FastAPI.
- [x] Testes de orientação e consulta.
- [x] Testes de validação de solicitações incompletas.
- [ ] Revisão final da integração.
- [ ] Testes adicionais de segurança.
- [ ] Documentação final.

## 10.Exemplos de utilização da API

Endpoint:

POST http://127.0.0.1:8000/agent/executar

### Orientação geral

```json
{
  "mensagem": "Como reduzir o cancelamento de clientes SaaS?"
}


