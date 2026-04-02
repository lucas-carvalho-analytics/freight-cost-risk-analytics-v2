# Backup/Restore Foundation

Esta fase adiciona uma base minima e reproduzivel para backup e restore do Postgres, sem prometer DR completo.

## O que entrou

- script de backup via `docker compose`
- script de restore via `docker compose`
- path previsivel para dumps em `backups/<stack>/`
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
python scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/seu-backup.dump --yes-i-understand-this-will-overwrite-data
```

### Backup do stack de production foundation

```powershell
python scripts/backup_postgres_compose.py --stack production-foundation --env-file deploy/production.env
```

### Restore do stack de production foundation

```powershell
python scripts/restore_postgres_compose.py --stack production-foundation --env-file deploy/production.env --input backups/production-foundation/seu-backup.dump --yes-i-understand-this-will-overwrite-data
```

## Cuidados operacionais

- dumps reais nao devem ser versionados
- o restore sobrescreve o banco alvo
- o script de restore para os servicos de runtime do app antes de restaurar e os sobe de novo ao final
- use secrets reais no env antes de operar fora de ambiente local

## O que ainda nao cobre

- agendamento automatico
- storage remoto
- politica de retencao
- verificacao automatica de integridade do dump
- DR completo
