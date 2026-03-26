# Freight Cost Risk Analytics - Backend

MVP local da Fase 1 para analytics logistico usando FastAPI, PostgreSQL, SQLAlchemy 2 e Alembic.

## Estrutura

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── health.py
│   │   ├── __init__.py
│   │   └── router.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── audit_log.py
│   │   ├── shipment.py
│   │   └── user.py
│   ├── scripts/
│   │   ├── __init__.py
│   │   ├── import_shipments.py
│   │   └── seed_admin.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── services/
│   │   └── __init__.py
│   ├── __init__.py
│   └── main.py
├── alembic/
│   ├── versions/
│   │   └── 20260325_0001_create_initial_tables.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── .env.example
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## O que ja existe

- API FastAPI com roteamento versionado
- endpoint `GET /api/v1/health`
- configuracao por `.env`
- PostgreSQL via Docker Compose
- modelos iniciais `Shipment`, `User` e `AuditLog`
- migration inicial com Alembic
- sessao de banco com SQLAlchemy 2
- script de ingestao CSV para `shipments`
- autenticacao JWT basica com login e endpoint protegido
- script de seed para admin inicial
- camada simples em `services/` para consultas de analytics
- endpoints protegidos de KPI e filtros principais

## Regras do modelo Shipment

- `ocorrencia` pode assumir valores como `OK`, `Atraso` ou `Sinistro`
- `tem_ocorrencia` deve representar a regra derivada `ocorrencia != "OK"`
- `ad_valorem` pode ser calculado a partir de `valor_carga * taxa_ad_valorem_pct / 100`

## Requisitos

- Python 3.11+
- Docker e Docker Compose

## Setup local

1. Configure as variaveis de ambiente.

   O projeto aceita `.env` dentro de `backend/` e tambem o `.env` na raiz do repositorio.
   Defina `JWT_SECRET_KEY` com um valor real antes de iniciar a API.
   Se quiser usar o arquivo de exemplo:

   ```bash
   cp .env.example .env
   ```

   No PowerShell:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   No PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Suba o PostgreSQL:

   ```bash
   docker compose up -d
   ```

5. Rode as migrations:

   ```bash
   alembic upgrade head
   ```

6. Rode a ingestao do CSV, se quiser carregar a tabela `shipments`:

   ```bash
   python -m app.scripts.import_shipments caminho/para/arquivo.csv
   ```

   No PowerShell:

   ```powershell
   python -m app.scripts.import_shipments .\caminho\para\arquivo.csv
   ```

7. Crie o admin inicial:

   ```bash
   python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
   ```

   No PowerShell:

   ```powershell
   python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
   ```

8. Inicie a API:

   ```bash
   uvicorn app.main:app --reload
   ```

## Ingestao CSV

Mapeamento esperado do CSV:

- `Data do Embarque` -> `data_embarque`
- `Origem` -> `origem`
- `Destino` -> `destino`
- `Valor da Carga (R$)` -> `valor_carga`
- `Tipo de Veiculo` ou `Tipo de Veículo` -> `tipo_veiculo`
- `Transportadora` -> `transportadora`
- `Taxa Ad Valorem (%)` -> `taxa_ad_valorem_pct`
- `Frete Peso (R$)` -> `frete_peso`
- `Ocorrencias` ou `Ocorrências` -> `ocorrencia`

Regras aplicadas no import:

- nomes externos sao convertidos para o formato interno em `snake_case`
- datas sao convertidas com `dayfirst=True`
- valores monetarios e percentuais aceitam formatos como `1234.56`, `1234,56`, `1.234,56`, `R$ 1.234,56` e `12,5%`
- `ad_valorem` e calculado se nao existir pronto no CSV
- `tem_ocorrencia` vira `false` quando `ocorrencia == "OK"`
- `origem`, `destino`, `tipo_veiculo` e `transportadora` sao obrigatorios e falham com erro claro se vierem vazios
- reimportacoes evitam duplicacao simples comparando os dados ja existentes

## Endpoints iniciais

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/kpis/frete-total`
- `GET /api/v1/kpis/advalorem-total`
- `GET /api/v1/kpis/taxa-ocorrencias`
- `GET /api/v1/kpis/custo-por-transportadora`
- `GET /api/v1/kpis/custo-risco-destino`
- `GET /api/v1/filtros/origens`
- `GET /api/v1/filtros/destinos`
- `GET /api/v1/filtros/transportadoras`
- `GET /api/v1/filtros/tipos-veiculo`

Exemplo de resposta:

```json
{
  "status": "ok",
  "service": "freight_cost_risk_analytics",
  "version": "0.1.0"
}
```

## Autenticacao

Criar admin inicial:

```bash
python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
```

O script vai pedir a senha de forma segura no terminal e solicitar confirmacao.

Exemplo de login:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"Admin123!\"}"
```

Exemplo de uso do token:

```bash
curl http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer SEU_TOKEN"
```

No Swagger:

- faca login no `POST /api/v1/auth/login`
- copie o `access_token`
- clique em `Authorize`
- cole `Bearer SEU_TOKEN`

## KPIs e filtros

Todos os endpoints de KPI e filtros exigem Bearer token.

Filtros opcionais suportados via query params:

- `data_inicio`
- `data_fim`
- `origem`
- `destino`
- `transportadora`
- `tipo_veiculo`
- `ocorrencia`

Exemplo de KPI com filtros:

```bash
curl "http://127.0.0.1:8000/api/v1/kpis/frete-total?origem=Suape&transportadora=Belmont-Alpha&ocorrencia=ok" \
  -H "Authorization: Bearer SEU_TOKEN"
```

Exemplo de endpoint de filtros:

```bash
curl "http://127.0.0.1:8000/api/v1/filtros/destinos?origem=Jaboat%C3%A3o&transportadora=Trans-X" \
  -H "Authorization: Bearer SEU_TOKEN"
```

Regras calculadas:

- `frete-total`: soma de `frete_peso`
- `advalorem-total`: soma de `ad_valorem`
- `taxa-ocorrencias`: percentual de shipments com `tem_ocorrencia = true`
- `custo-por-transportadora`: `avg(frete_peso)` e quantidade de shipments por transportadora
- `custo-risco-destino`: `custo_medio`, `taxa_ocorrencia_pct` e `score_risco` heuristico
- `score_risco = custo_medio_normalizado * 0.4 + taxa_ocorrencia_normalizada * 0.6`
- endpoints de filtros ignoram o filtro do proprio campo para listar opcoes mais uteis na interface

## Proxima evolucao natural

- adicionar logs e tratamento padronizado de erros
- expandir a camada simples de `services/` para regras de negocio e agregacoes adicionais
