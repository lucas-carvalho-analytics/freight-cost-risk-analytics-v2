# freight-cost-risk-analytics-v2

Aplicacao full-stack para analytics logistico com foco em custos de frete, ad valorem, ocorrencias e exploracao de indicadores via API protegida e dashboard web.

## Visao do projeto

Este repositorio concentra a base tecnica da V2 do projeto de analytics logistico. A aplicacao evoluiu em fases incrementais, cobrindo:

- ingestao local de dataset CSV para PostgreSQL
- autenticacao JWT para acesso aos recursos protegidos
- exposicao de KPIs e filtros principais via FastAPI
- dashboard React consumindo a API real
- baseline minima de testes e checklist operacional
- base simples de deploy/demo same-origin

O objetivo da base atual e servir como fundacao confiavel para demos, novas features de produto e evolucao de operacao, sem antecipar complexidade desnecessaria.

## Stack

- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Pandas
- React
- Vite
- TypeScript
- Tailwind CSS
- Nginx para demo/deploy same-origin
- Docker Compose
- Pytest

## Estrutura de diretorios

```text
.
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── docker/
│   ├── tests/
│   ├── .env.example
│   ├── Dockerfile.demo
│   ├── alembic.ini
│   ├── docker-compose.yml
│   ├── README.md
│   ├── requirements-dev.txt
│   └── requirements.txt
├── deploy/
│   └── demo.env.example
├── docs/
│   ├── branch-validation-checklist.md
│   └── deploy-demo.md
├── frontend/
│   ├── public/
│   ├── src/
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md
│   ├── nginx.demo.conf
│   └── package.json
├── docker-compose.demo.yml
├── gerar_dataset_logistica_pe.py
└── README.md
```

## Setup local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

No PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend usa `VITE_API_BASE_URL=/api/v1`, mantendo compatibilidade com a arquitetura same-origin de demo/deploy.

## Geracao e import de dataset

O projeto inclui um gerador local de dataset:

- [gerar_dataset_logistica_pe.py](./gerar_dataset_logistica_pe.py)

Fluxo sugerido:

1. gerar o CSV localmente
2. manter o arquivo fora do versionamento
3. importar para `shipments`

Exemplo:

```bash
cd backend
python -m app.scripts.import_shipments caminho/para/arquivo.csv
```

## API e autenticacao

### Endpoints base

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

Criacao do admin inicial:

```bash
cd backend
python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
```

## Demo/Deploy

Para ambiente demonstravel, a base desta fase segue arquitetura same-origin:

- frontend buildado e servido como estatico
- Nginx recebendo o trafego do navegador
- `/api/v1` proxied para o backend FastAPI
- PostgreSQL rodando na mesma composicao

Guia curto:

- [docs/deploy-demo.md](./docs/deploy-demo.md)

## Production readiness foundation

Existe agora uma base separada para preparacao de producao, ainda sem prometer deploy final:

- runtime do backend separado de migrations
- compose proprio para `production foundation`
- env example especifico para producao
- healthchecks operacionais minimos
- validacoes extras para `APP_ENV=production`

Guia curto:

- [docs/production-readiness.md](./docs/production-readiness.md)

## Secrets and operational config

Existe tambem uma base curta para contratos de env e tratamento de secrets por ambiente:

- `development`, `demo` e `production foundation` agora ficam mais explicitos
- placeholders inseguros falham mais cedo em cenarios criticos
- a documentacao deixa claro o que e obrigatorio e como rotacionar secrets basicos

Guia curto:

- [docs/secrets-and-operational-config.md](./docs/secrets-and-operational-config.md)

## Observability foundation

Existe agora uma base inicial de observabilidade para troubleshooting e operacao:

- logs estruturados com contexto mais consistente
- `request_id` por request
- separacao entre `health` e `ready`
- healthchecks do stack mais alinhados ao estado real dos servicos

Guia curto:

- [docs/observability-foundation.md](./docs/observability-foundation.md)

## CI/CD foundation

Existe agora uma base inicial de automacao para validacao do projeto:

- backend validado automaticamente
- frontend validado automaticamente
- compose/config validados automaticamente
- foco em PRs e em pushes para `main`

Guia curto:

- [docs/ci-cd-foundation.md](./docs/ci-cd-foundation.md)

## Container smoke tests foundation

Existe agora tambem uma validacao basica de stack com containers para o ambiente de demo:

- sobe o stack de demo de forma automatizavel
- valida frontend servido
- valida `health` e `ready` via compose
- valida login real, 1 KPI protegido e 1 filtro protegido
- derruba o ambiente ao final

Guia curto:

- [docs/container-smoke-tests-foundation.md](./docs/container-smoke-tests-foundation.md)

## Production foundation smoke tests

Existe agora tambem uma validacao minima e automatizavel do stack de `production foundation`:

- sobe o stack de producao base com `docker compose`
- valida `/healthz`, `health` e `ready`
- verifica `migrate` concluido e servicos saudaveis
- derruba o ambiente ao final

Guia curto:

- [docs/production-foundation-smoke-tests.md](./docs/production-foundation-smoke-tests.md)

## Backup/restore foundation

Existe agora uma base minima de backup e restore do Postgres para operacao local e foundation environments:

- backup via `docker compose`
- restore via `docker compose`
- dumps fora do versionamento em `backups/`
- confirmacao explicita para restore destrutivo

Guia curto:

- [docs/backup-restore-foundation.md](./docs/backup-restore-foundation.md)

## Validacao e testes

Checklist operacional por branch:

- [docs/branch-validation-checklist.md](./docs/branch-validation-checklist.md)

Smoke tests atuais:

```bash
cd backend
pytest
```

```bash
cd frontend
npm run lint
npm run build
```

## Roadmap

### Curto prazo

- ampliar a documentacao operacional
- endurecer a camada de deploy/demo
- evoluir a cobertura de testes automatizados

### Medio prazo

- expandir observabilidade e operacao de runtime
- novos endpoints analiticos e comparativos
- testes de integracao mais completos

### Futuro

- RBAC mais completo
- pipelines de dados e operacao
- componentes de modelagem analitica e ML quando fizer sentido
