# Production Readiness Foundation

Esta fase nao fecha deploy de producao. Ela reduz riscos reais e separa melhor o que era apenas demo do que ja pode servir como base de operacao mais seria.

## O que entrou

- compose separado para `production foundation`
- backend com runtime proprio para producao
- migrations desacopladas do startup do app
- env example especifico de producao
- healthchecks simples para frontend, backend e banco
- validacoes minimas para ambiente `production`

## Decisoes desta fase

### 1. Runtime do app separado de migration

No ambiente de demo, o backend podia subir e rodar migration no mesmo startup.

Para a base de producao:

- `migrate` roda como servico operacional separado
- `backend` sobe so depois de `migrate` completar com sucesso
- o runtime do app nao aplica schema automaticamente

### 2. Same-origin continua valido

Seguimos com:

- frontend estatico em Nginx
- `/api/v1` proxied para o backend

Isso continua simples, coerente com o MVP e evita CORS desnecessario tambem para producao inicial.

### 3. Validacoes minimas de seguranca

Quando `APP_ENV=production`:

- `JWT_SECRET_KEY` precisa ter pelo menos 32 caracteres
- `WEB_CONCURRENCY` precisa ser maior ou igual a 1

## Como validar a base

1. Copie o env:

   ```powershell
   Copy-Item deploy/production.env.example deploy/production.env
   ```

2. Ajuste pelo menos:

- `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY`

3. Valide a composicao:

   ```powershell
   docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml config
   ```

4. Suba a base:

   ```powershell
   docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml up --build -d
   ```

5. Verifique saude:

   ```powershell
   docker compose --env-file deploy/production.env -f docker-compose.production-foundation.yml ps
   ```

## O que ainda NAO esta pronto para producao

- dominio e TLS
- secret management real
- CI/CD e publicacao de imagens
- backup/restore do banco
- politica de rollback
- monitoramento e alertas mais completos
- hardening de rede, headers e autenticao operacional
- processo formal para seed/import em ambiente real

## Leitura complementar

- [docs/deploy-demo.md](./deploy-demo.md)
