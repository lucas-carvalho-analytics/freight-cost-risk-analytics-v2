# freight-cost-risk-analytics-v2

Backend MVP para analytics logístico com foco em custos de frete, ad valorem, ocorrências e exploração de indicadores via API protegida.

## Visão do projeto

Este repositório concentra a base técnica da V2 do projeto de analytics logístico. A aplicação foi organizada para permitir evolução incremental, começando por:

- ingestão local de dataset CSV para PostgreSQL
- autenticação JWT básica para acesso aos recursos protegidos
- exposição de KPIs e filtros principais via FastAPI
- trilha mínima de documentação e validação para sustentar as próximas fases

O objetivo da base atual é servir como fundação confiável para novas etapas, sem antecipar complexidade de frontend, ML, RBAC completo ou pipelines de produção.

## Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Pandas
- JWT com `PyJWT`
- Hash de senha com `passlib`
- Docker Compose
- Pytest para baseline mínima de testes

## Estrutura de diretórios

```text
.
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── scripts/
│   │   └── services/
│   ├── tests/
│   ├── .env.example
│   ├── alembic.ini
│   ├── docker-compose.yml
│   ├── README.md
│   ├── requirements-dev.txt
│   └── requirements.txt
├── docs/
│   └── branch-validation-checklist.md
├── gerar_dataset_logistica_pe.py
└── README.md
```

## Setup local

O fluxo principal roda a partir de `backend/`.

### 1. Ambiente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

No PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Dependências

```bash
pip install -r requirements.txt
```

Para a baseline de testes:

```bash
pip install -r requirements-dev.txt
```

### 3. Configuração local

Crie `backend/.env` a partir de `backend/.env.example` e defina pelo menos:

- `JWT_SECRET_KEY` com valor real
- credenciais do PostgreSQL local, se necessário

`.env` local não deve ser commitado.

### 4. Banco

```bash
docker compose up -d
alembic upgrade head
```

## Geração e import de dataset

O projeto inclui um gerador local de dataset:

- [gerar_dataset_logistica_pe.py](./gerar_dataset_logistica_pe.py)

Fluxo sugerido:

1. gerar o CSV localmente
2. manter o arquivo fora do versionamento
3. importar para `shipments`

Exemplo de import:

```bash
cd backend
python -m app.scripts.import_shipments caminho/para/arquivo.csv
```

## Autenticação

Criação do admin inicial:

```bash
cd backend
python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"Admin123!\"}"
```

Endpoint protegido:

```bash
curl http://127.0.0.1:8000/api/v1/auth/me \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Endpoints principais

### Base

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### KPIs protegidos

- `GET /api/v1/kpis/frete-total`
- `GET /api/v1/kpis/advalorem-total`
- `GET /api/v1/kpis/taxa-ocorrencias`
- `GET /api/v1/kpis/custo-por-transportadora`
- `GET /api/v1/kpis/custo-risco-destino`

### Filtros protegidos

- `GET /api/v1/filtros/origens`
- `GET /api/v1/filtros/destinos`
- `GET /api/v1/filtros/transportadoras`
- `GET /api/v1/filtros/tipos-veiculo`

Os endpoints de KPI e filtros aceitam filtros opcionais por query params, como:

- `data_inicio`
- `data_fim`
- `origem`
- `destino`
- `transportadora`
- `tipo_veiculo`
- `ocorrencia`

## Analytics vs engenharia e segurança

### Analytics

- modelagem inicial do dataset logístico em `shipments`
- agregações de frete, ad valorem, taxa de ocorrência e score heurístico de risco
- endpoints para exploração analítica com filtros

### Engenharia

- estrutura modular pronta para evolução
- sessão de banco com SQLAlchemy 2
- migrations com Alembic
- scripts explícitos de import e seed
- baseline mínima de testes e checklist operacional

### Segurança

- autenticação JWT
- hash seguro de senha
- validação de `JWT_SECRET_KEY` insegura no startup
- auditoria de login e de acesso aos KPIs
- arquivos locais sensíveis fora do versionamento

## Validação e testes

Checklist operacional por branch:

- [docs/branch-validation-checklist.md](./docs/branch-validation-checklist.md)

Smoke test inicial:

```bash
cd backend
pytest
```

## Roadmap

### Curto prazo

- expandir cobertura de testes automatizados
- consolidar documentação da raiz e do backend
- revisar padronização de erros e logs

### Médio prazo

- novos endpoints analíticos e comparativos
- testes de integração para auth, KPI e filtros
- melhorias na camada de services e contratos de resposta

### Futuro

- frontend
- RBAC mais completo
- pipelines de dados e observabilidade
- componentes de modelagem analítica e ML quando fizer sentido
