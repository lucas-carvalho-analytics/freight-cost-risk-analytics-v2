# Backup/Restore Foundation

Esta fase adiciona uma base minima e reproduzivel para backup e restore do Postgres, sem prometer DR completo.

## O que entrou

- script de backup via `docker compose`
- script de restore via `docker compose`
- path previsivel para dumps em `backups/<stack>/`
- naming padronizado em UTC: `<stack>-<database>-YYYYMMDDTHHMMSSZ.dump`
- metadata sidecar em `<arquivo>.metadata.json`
- validacao basica de integridade com `pg_restore --list`
- restore com confirmacao explicita
- orientacao curta de operacao e cuidados

## Scripts

- `scripts/backup_postgres_compose.py`
- `scripts/restore_postgres_compose.py`

## Stacks suportados

- `demo`
- `production-foundation`

## Exemplos

### Backup do stack de demo

```powershell
python scripts/backup_postgres_compose.py --stack demo --env-file deploy/demo.env
```

### Restore do stack de demo

```powershell
python scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/demo-freight_analytics-20260402T150000Z.dump --yes-i-understand-this-will-overwrite-data
```

### Backup do stack de production foundation

```powershell
python scripts/backup_postgres_compose.py --stack production-foundation --env-file deploy/production.env
```

### Restore do stack de production foundation

```powershell
python scripts/restore_postgres_compose.py --stack production-foundation --env-file deploy/production.env --input backups/production-foundation/production-foundation-freight_analytics-20260402T150000Z.dump --yes-i-understand-this-will-overwrite-data
```

## Cuidados operacionais

- dumps reais nao devem ser versionados
- metadata sidecar ajuda a conferir contexto, hash e tamanho do backup
- o restore sobrescreve o banco alvo
- o script de restore para os servicos de runtime do app antes de restaurar e os sobe de novo ao final
- use secrets reais no env antes de operar fora de ambiente local

## Retencao minima sugerida

- `demo`: manter os 3 backups mais recentes e remover os anteriores manualmente
- `production-foundation`: manter pelo menos os 7 backups mais recentes ate existir politica automatizada
- sempre validar se o backup mais recente gera metadata e passa no restore antes de apagar historico recente

## O que ainda nao cobre

- agendamento automatico
- storage remoto
- politica de retencao
- verificacao automatica recorrente de integridade fora do fluxo manual
- DR completo
