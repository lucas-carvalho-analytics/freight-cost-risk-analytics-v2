# CI/CD Foundation

Esta fase nao fecha deploy automatizado. Ela adiciona uma base pequena de automacao para detectar regressao cedo em pull requests e em pushes para `main`.

## O que a pipeline cobre

### Backend

- `python -m compileall app tests`
- `pytest -q`

### Frontend

- `npm ci`
- `npm run lint`
- `npm run build`

### Compose/config

- `docker compose --env-file deploy/demo.env.example -f docker-compose.demo.yml config`
- `docker compose --env-file deploy/production.env.example -f docker-compose.production-foundation.yml config`

## Quando roda

- em `pull_request`
- em `push` para `main`

## O que esta fase ainda nao cobre

- deploy automatico
- publicacao de imagem
- migrations em ambiente remoto
- smoke test real do stack com containers subidos
- e2e de frontend no navegador
- verificacao de secrets em GitHub Actions

## Leitura pratica

Se a pipeline falhar:

1. corrija localmente o job correspondente
2. rode os mesmos comandos do workflow
3. atualize a branch e abra/atualize a PR
