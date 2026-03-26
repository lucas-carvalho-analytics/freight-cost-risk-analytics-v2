# Branch Validation Checklist

Checklist base para validação de branches antes de commit, push ou PR.

## Git

- confirmar branch atual com `git branch --show-current`
- revisar working tree com `git status --short --branch`
- garantir que `.env` não esteja staged
- garantir que CSVs locais de teste não estejam staged
- confirmar que a branch partiu de uma `main` atualizada

## Ambiente

- entrar em `backend/`
- ativar `.venv`
- instalar dependências necessárias
- confirmar que Docker está disponível quando a branch depender de banco

## Sanity check mínimo

- `python -m compileall app`
- `alembic upgrade head`

## Validação funcional mínima

Escolher os endpoints ou scripts mais críticos da branch e validar pelo menos:

- caminho feliz principal
- autenticação, se o recurso for protegido
- persistência ou leitura de banco, se a branch tocar dados
- ausência de regressão em endpoint já consolidado, quando aplicável

## Exemplos por tipo de branch

### Infra/API

- subir API com `uvicorn app.main:app --reload`
- validar `GET /api/v1/health`

### Auth

- login bem-sucedido
- endpoint protegido
- auditoria em `audit_logs`

### KPI/Filtros

- um KPI simples
- um KPI agrupado
- um endpoint de filtro

## Testes automatizados

Quando a branch incluir cobertura nova:

- rodar `pytest`
- registrar no PR o que foi coberto e o que ainda ficou manual

## PR

- resumir entregas
- listar validações locais executadas
- declarar explicitamente o que não entrou na fase
