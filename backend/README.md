# Freight Cost Risk Analytics - Backend

MVP local da Fase 1 para analytics logistico usando FastAPI, PostgreSQL, SQLAlchemy 2 e Alembic.

## Estrutura

```text
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   ├── __init__.py
│   │   └── router.py
│   ├── auth/
│   │   └── __init__.py
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
│   │   └── import_shipments.py
│   ├── schemas/
│   │   └── __init__.py
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

7. Inicie a API:

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

Exemplo de resposta:

```json
{
  "status": "ok",
  "service": "freight_cost_risk_analytics",
  "version": "0.1.0"
}
```

## Proxima evolucao natural

- criar schemas Pydantic para os modelos iniciais
- adicionar logs e tratamento padronizado de erros
- iniciar camada de repositorio ou services para regras de negocio
