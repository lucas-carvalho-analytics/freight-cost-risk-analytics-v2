# Observability Foundation

Esta fase nao fecha observabilidade completa. Ela melhora a visibilidade operacional com o menor conjunto util para troubleshooting inicial.

## O que entrou

- logs estruturados com `service`, `environment` e `version`
- `request_id` por request, retornado tambem no header `X-Request-ID`
- log basico de request concluida com metodo, path, status e duracao
- separacao entre liveness (`/api/v1/health`) e readiness (`/api/v1/ready`)
- compose de demo e production foundation usando sinais mais uteis para healthchecks

## Como interpretar os sinais

### Liveness

Endpoint:

- `GET /api/v1/health`

Uso:

- responder se o processo da API esta no ar
- nao valida dependencias externas

### Readiness

Endpoint:

- `GET /api/v1/ready`

Uso:

- responder se a API esta pronta para atender
- valida conectividade minima com o banco via `SELECT 1`

## O que observar nos logs

Eventos uteis desta fase:

- `app_startup`
- `app_shutdown`
- `http_request`
- `http_exception`
- `validation_exception`
- `unhandled_exception`

Campos uteis:

- `service`
- `environment`
- `version`
- `request_id`
- `path`
- `method`
- `status_code`
- `duration_ms`

## Comandos uteis

### Demo

```powershell
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml ps
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs -f backend
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs -f frontend
```

### Production foundation

```powershell
docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml ps
docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml logs -f backend
docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml logs -f frontend
```

## O que ainda falta

- agregacao central de logs
- metricas e alertas
- dashboards operacionais
- tracing distribuido
- correlation mais ampla entre frontend, nginx e backend
