# Production Foundation Smoke Tests

Esta fase adiciona uma validacao pequena e automatizavel do stack de `production foundation`, sem prometer deploy real.

## O que a fundacao cobre

- sobe o stack de `production foundation` com `docker compose`
- builda backend e frontend dentro do fluxo
- valida que o frontend responde em `/`
- valida `GET /healthz`
- valida `GET /api/v1/health`
- valida `GET /api/v1/ready`
- verifica que `migrate` termina com sucesso
- verifica que `backend`, `frontend` e `postgres` ficam saudaveis
- derruba o ambiente ao final

## O que ela ainda nao cobre

- login ou fluxos autenticados
- seed/import de dados
- smoke test de KPI protegido
- e2e de navegador
- deploy real

## Como rodar localmente

```powershell
python scripts/smoke_test_production_foundation.py
```

## Como entra no CI

O workflow de CI passa a incluir um job separado para o smoke test de `production foundation`, alem dos jobs de:

- backend
- frontend
- compose/config
- smoke test de demo

## Leitura pratica

Se esse smoke test falhar:

1. rode o script localmente
2. observe `docker compose ps`
3. observe os logs dos servicos
4. corrija primeiro problemas de migration, runtime, readiness ou reverse proxy
