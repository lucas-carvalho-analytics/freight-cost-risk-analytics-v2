# Container Smoke Tests Foundation

Esta fase nao fecha e2e completo. Ela adiciona uma validacao pequena, automatizavel e mais realista do stack de demo usando containers.

## O que a fundacao cobre

- sobe o stack de demo com `docker compose`
- builda frontend e backend dentro do fluxo
- valida que o frontend responde em `/`
- valida `GET /api/v1/health`
- valida `GET /api/v1/ready`
- derruba o ambiente ao final

## O que ela ainda nao cobre

- login automatizado
- seed de admin
- import de dataset
- fluxos protegidos por JWT
- e2e de navegador
- validacao completa de negocio

## Como rodar localmente

```powershell
python scripts/smoke_test_demo_stack.py
```

## Como entra no CI

O workflow de CI passa a incluir um job de smoke test do stack de demo, separado dos jobs de:

- backend
- frontend
- compose/config

## Leitura pratica

Se esse smoke test falhar:

1. rode o script localmente
2. observe `docker compose ps`
3. observe os logs dos servicos
4. corrija primeiro problemas de startup, healthcheck ou proxy
