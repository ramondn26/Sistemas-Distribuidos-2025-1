# TRABALHO PRÁTICO DA DISCIPLINA DE SISTEMAS DISTRIBUÍDOS (2025/1)

# Automação de Atendimento em E-commerce

## Problema

No e-commerce de varejo, o canal de chat web apresenta longos tempos de espera e alta taxa de abandono, gerando insatisfação do cliente e perda de conversões.

## Validação do Problema

- **66 % dos consumidores** esperam uma resposta em até 5 min via live chat
- **≈ 66 % consideram** essencial receber uma resposta imediata (até 10 min)
- **42 % dos clientes** preferem atendimento em tempo real online em vez de e-mail ou telefone
- **> 50 % abandonam** o chat durante esperas prolongadas

## Justificativa

- Tempo médio de primeira resposta em sistemas atuais: **1 min 35 s**
- Padrão de excelência do mercado: responder em **menos de 1 min**

## Objetivos

1. Reduzir o tempo médio de primeira resposta de **1 min 35 s** para **< 30 s**
2. Diminuir a taxa de abandono de chat de **> 50 %** para **< 20 %**

## Metodologia

- **Agentes de IA**
  - Agente externo via API.
  - Agente local containerizado em Docker.
- **Comunicação distribuída**
  - Broker ou A2A.
  - Cada agente como microserviço orquestrado.
- **API de Agregação**
  - FastAPI que recebe as mensagens do chat, chama os agentes e retorna a resposta ao cliente.
- **Segurança e Arquitetura**
  - Modelagem STRIDE e mitigação (TLS, JWT, rede isolada).
  - Diagramas C4 pré e pós-mitigação.


# Estrutura do projeto

Sistemas-Distribuidos-2025-1/
│
├── agent1/
│   ├── ml_assistant.py          # Agente 1: Assistente virtual (Flask)
│   └── requirements.txt         # Dependências do agente 1
│
├── agent2/
│   ├── sentiment_agent.py       # Agente 2: Analisador de sentimento (FastAPI)
│   └── requirements.txt         # Dependências do agente 2
│
├── main.py                      # Interface Streamlit integrando ambos agentes
│
├── README.md                    # Documentação do projeto
│
├── ARQUITETURA.md               # Documentação arquitetônica (opcional)
│
├── .env                         # Variáveis de ambiente (OpenAI API key etc.)
│
└── requirements.txt             # Dependências gerais (Streamlit, requests etc.)


## Metas de Sucesso

- **Primeira resposta** do agente em < 30 s no ambiente de testes.
- **Taxa de abandono** < 20 % aferida pelos logs de chat.


## Visão inicial

```plaintext

+-------------------+
|   Usuário         |
+-------------------+
         |
         v
+-------------------+
|   main.py         |  (Streamlit)
| Interface         |
+-------------------+
         |
         |-------------------------------+
         |                               |
         v                               v
+-------------------+        +---------------------------+
| agent2            |        | agent1                    |
| Sentiment Agent   |        | ML Assistant              |
| (FastAPI)         |        | (Flask + OpenAI)          |
+-------------------+        +---------------------------+
         \                              /
          \                            /
           \                          /
            +------------------------+
            |     Promoções          |
            | (entregues para todos) |
            +------------------------+


```

# Diagrama arquitetura final

```plaintext

                      +------------------+
                      | Usuário Comum    |
                      +------------------+
                              |
                              v
                      +-------------------+
                      |   main.py         |  (Streamlit)
                      | Interface         |
                      +-------------------+
                       /               \
                      /                 \
            +----------------+    +------------------+
            | Serviços       |    | Promoções        |
            | Básicos (todos)|    | Exclusivas       |
            +----------------+    +------------------+
                 |                        ^
                 |                        |
        +-------------------+   +--------------------+
        | agent2            |   |      Usuário       |
        | Sentiment Agent   |   |      Premium       |
        | (FastAPI)         |   +--------------------+
        +-------------------+
                 |
        +---------------------------+
        | agent1                    |
        | ML Assistant              |
        | (Flask + OpenAI)          |
        +---------------------------+

        
``` 




## Estrutura do Repositório

## Referências

1. HubSpot. _How Consumers Use Live Chat for Customer Service_ (2021)
2. Gorgias. _22 Live Chat Statistics You Need To Know_ (2023)
3. Zendesk. _AI in e-commerce: Live Chat Trends_ (2024)
4. Alexander Jarvis. _What Is Live Chat Abandonment Rate in E-commerce?_ (2025)
5. Tidio. _24 Essential Live Chat Statistics You Should Know_ (2025)
6. Zendesk CX Trends Report 2024.
