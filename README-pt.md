# Travel Lead Qualification MVP

Sistema conversacional de qualificação de leads para agências de turismo, construído com FastAPI e Telegram Bot API. Os leads são capturados por meio de um fluxo de conversa estruturado, qualificados automaticamente, persistidos em banco de dados e monitorados através de um dashboard operacional.

> **Nota sobre a decisão de canal:** Este projeto foi originalmente desenhado com a WhatsApp Cloud API. Ao identificar que a aprovação de conta Meta Business seria um bloqueio para o prazo de entrega, a camada de integração foi migrada para o Telegram, que oferece uma API aberta sem necessidade de aprovação. O motor de qualificação, a camada de persistência, o dashboard e toda a lógica de negócio permanecem idênticos. Em um cenário de produção, trocar o canal de volta para WhatsApp é uma mudança isolada apenas na camada de integração.

---

## Demo ao Vivo

| | |
|---|---|
| Dashboard | https://travel-mvp-production-a93a.up.railway.app/dashboard |
| Docs da API | https://travel-mvp-production-a93a.up.railway.app/docs|
| Health | https://travel-mvp-production-a93a.up.railway.app |
| Telegram Bot | https://t.me/travel_qualification_demo_bot |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python · FastAPI |
| IA Conversacional | Anthropic Claude API (motor de qualificação) |
| Canal de mensagens | Telegram Bot API |
| Persistência | SQLite |
| Dashboard | Jinja2 · Chart.js |
| Configuração | python-dotenv |
| Deploy | Railway |

---

## Arquitetura

```
Usuário no Telegram
     │
     ▼
POST /api/telegram/webhook   ← Telegram entrega a mensagem
     │
     ▼
qualification.py             ← Máquina de estados conversacional
     │                          alimentada pela Claude API
     ▼
db.py (SQLite)               ← Lead persistido com score de temperatura
     │
     ▼
GET /api/metrics             ← Métricas agregadas
     │
     ▼
GET /dashboard               ← Dashboard operacional (Chart.js)
```

---

## Fluxo do Produto

1. O usuário envia `/start` para o bot no Telegram
2. O bot conduz uma conversa estruturada de qualificação — destino, período de viagem, tamanho do grupo, orçamento, tipo de viagem, prazo de decisão e prioridades
3. Ao final do fluxo, o Claude classifica a temperatura do lead: `hot`, `warm` ou `cold`
4. O lead qualificado é persistido no SQLite com um resumo completo em texto
5. O dashboard exibe KPIs em tempo real e gráficos para o time comercial

---

## Funcionalidades

- Captação de leads via bot no Telegram com fluxo conversacional
- Classificação de temperatura do lead por IA (`hot` / `warm` / `cold`)
- Persistência em SQLite com campos estruturados de qualificação
- API REST com `/api/metrics` para consumo do dashboard
- Dashboard operacional com visualizações em Chart.js: leads por destino, orçamento, origem, tipo de viagem, prazo de decisão e foco de prioridade
- Endpoint `POST /api/simulate` para testar o fluxo de qualificação sem precisar do Telegram
- `POST /api/leads` para criação manual de leads
- Validação do token do bot via `/api/telegram/test`

---

## Dashboard

![Dashboard](Screenshot.png)

---

## Campos de Qualificação

Cada lead qualificado captura:

| Campo | Descrição |
|---|---|
| `destination_country` | País de destino |
| `destination_city` | Cidade ou região específica |
| `travel_period_text` | Período de viagem em linguagem natural |
| `travelers_count` | Número de viajantes |
| `trip_type` | Ex: casal, família, solo, grupo |
| `budget_range` | Faixa de orçamento informada pelo lead |
| `decision_timing` | Com que rapidez pretendem decidir |
| `priority_focus` | O que mais importa: preço, conforto ou experiência |
| `lead_temperature` | `hot` / `warm` / `cold` — classificação pela IA |
| `lead_source` | `telegram`, `simulate` ou `manual` |
| `notes_summary` | Resumo estruturado completo gerado na qualificação |

---

## Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/dashboard` | Dashboard operacional (HTML) |
| `GET` | `/api/metrics` | Métricas agregadas de leads (JSON) |
| `POST` | `/api/leads` | Criar um lead manualmente |
| `POST` | `/api/simulate` | Simular uma conversa de qualificação |
| `POST` | `/api/telegram/webhook` | Receber mensagens do Telegram |
| `GET` | `/api/telegram/test` | Validar token do bot do Telegram |
| `GET` | `/api/telegram/updates` | Buscar atualizações brutas do Telegram |
| `GET` | `/api/telegram/send-test` | Enviar mensagem de teste via Telegram |

---

## Endpoint de Simulação — Sem Telegram Necessário

Você pode testar o fluxo completo de qualificação sem configurar o Telegram:

**Iniciar a conversa:**
```bash
curl -X POST https://travel-mvp-production-a93a.up.railway.app/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"phone": "+5511999990001", "message": "start", "session": null}'
```

**Continuar com as respostas, passando a sessão a cada turno:**
```bash
curl -X POST https://travel-mvp-production-a93a.up.railway.app/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5511999990001",
    "message": "Cancun",
    "session": {"state": "ask_destination", "lead": {}}
  }'
```

**Exemplo de resposta finalizada:**
```json
{
  "reply": "Perfeito. Qualifiquei esta oportunidade como lead quente para Cancun (México).",
  "session": {
    "state": "done",
    "lead": {
      "destination_city": "Cancun",
      "destination_country": "Mexico",
      "travel_period_text": "Julho",
      "travelers_count": 2,
      "budget_range": "R$ 20.000",
      "trip_type": "casal",
      "lead_temperature": "warm"
    }
  },
  "completed": true
}
```

---

## Rodando Localmente

```bash
git clone https://github.com/Padilhaaaaa/travel-mvp.git
cd travel-mvp

python -m venv venv
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edite o .env com suas credenciais

uvicorn app.main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`.
Documentação interativa da API em `http://localhost:8000/docs`.

---

## Deploy no Railway

Este projeto está pronto para deploy no [Railway](https://railway.app) sem configuração adicional.

1. Faça fork ou clone deste repo
2. Crie um novo projeto no Railway e conecte seu repositório GitHub
3. Adicione as variáveis de ambiente no painel do Railway
4. O Railway detecta o `Procfile` e faz o deploy automaticamente

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Após o deploy, registre o webhook do Telegram:

```bash
curl "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://<SUA_URL>.up.railway.app/api/telegram/webhook"
```

---

## Variáveis de Ambiente

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui       # opcional, para a rota send-test
DB_PATH=travel_mvp.db
APP_ENV=development
```

Para obter um token de bot no Telegram: abra [@BotFather](https://t.me/BotFather), envie `/newbot` e siga as instruções.

---

## Estrutura do Projeto

```
travel-mvp/
├── app/
│   ├── main.py               # App FastAPI, rotas, handler do webhook Telegram
│   ├── db.py                 # Conexão SQLite, schema, insert_lead
│   ├── services/
│   │   └── qualification.py  # Máquina de estados + integração com Claude
│   └── templates/
│       └── dashboard.html    # Dashboard operacional (Jinja2 + Chart.js)
├── .env.example
├── .gitignore
├── Procfile                  # Configuração de deploy Railway
├── requirements.txt
└── README.md
```

---

## O Que Adicionaria em uma Versão de Produção

- Substituir SQLite por PostgreSQL + pgvector para busca semântica de leads
- Adicionar verificação de assinatura do webhook do Telegram (`X-Telegram-Bot-Api-Secret-Token`)
- Armazenamento persistente de sessão (Redis) em vez de dicionário em memória
- Camada de autenticação no dashboard
- WhatsApp Cloud API como canal principal (troca direta pela camada do Telegram)
- Pipeline de CI/CD e Docker Compose para paridade local com produção
