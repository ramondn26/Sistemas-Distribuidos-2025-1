# TRABALHO PRÁTICO DA DISCIPLINA DE SISTEMAS DISTRIBUÍDOS (2025/1)

# Automação de Atendimento em E-commerce

## Problema
No e-commerce de varejo, o canal de chat web apresenta longos tempos de espera e alta taxa de abandono, gerando insatisfação do cliente e perda de conversões.

## Validação do Problema
- **66 % dos consumidores** esperam uma resposta em até 5 min via live chat :contentReference[oaicite:0]{index=0}.  
- **≈66 % consideram** essencial receber uma resposta imediata (até 10 min) :contentReference[oaicite:1]{index=1}.  
- **42 % dos clientes** preferem atendimento em tempo real online em vez de e-mail ou telefone :contentReference[oaicite:2]{index=2}.  
- **> 50 % abandonam** o chat durante esperas prolongadas :contentReference[oaicite:3]{index=3}.

## Justificativa
- Tempo médio de primeira resposta em sistemas atuais: **1 min 35 s** :contentReference[oaicite:4]{index=4}.  
- Padrão de excelência do mercado: responder em **menos de 1 min** :contentReference[oaicite:5]{index=5}.

## Objetivos
1. Reduzir o tempo médio de primeira resposta de **1 min 35 s** para **< 30 s**.  
2. Diminuir a taxa de abandono de chat de **> 50 %** para **< 20 %**.

## Metodologia
- **Agentes de IA**  
  - Agente externo via API.  
  - Agente local containerizado em Docker.  
- **Comunicação distribuída**  
  - Broker ou A2A.  
  - Cada agente como microserviço orquestrado.  
- **API de Agregação**  
  -  
- **Segurança e Arquitetura**  
  - Modelagem STRIDE e mitigação (TLS, JWT, rede isolada).  
  - Diagramas C4 pré e pós-mitigação.

## Metas de Sucesso
- **Primeira resposta** do agente em < 30 s no ambiente de testes.  
- **Taxa de abandono** < 20 % aferida pelos logs de chat.

## Estrutura do Repositório

## Referências
1. HubSpot. *How Consumers Use Live Chat for Customer Service* (2021) :contentReference[oaicite:6]{index=6}  
2. Gorgias. *22 Live Chat Statistics You Need To Know* (2023) :contentReference[oaicite:7]{index=7}  
3. Alexander Jarvis. *What Is Live Chat Abandonment Rate in E-commerce?* (2025) :contentReference[oaicite:8]{index=8}  
4. Tidio. *24 Essential Live Chat Statistics You Should Know* (2025) :contentReference[oaicite:9]{index=9}  
