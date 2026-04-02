# Backup Scheduling Foundation

Esta fase adiciona uma base minima para execucao recorrente de backups, sem prometer scheduler completo nem DR.

## O que entrou

- wrapper operacional para backup recorrente
- parametrizacao simples de `stack`, `env-file`, `output-dir` e `keep`
- pruning simples de backups antigos no diretorio alvo
- exemplos curtos de uso manual, cron e Task Scheduler

## Script

- `scripts/run_scheduled_backup.py`

## Exemplo manual

```powershell
python scripts/run_scheduled_backup.py --stack demo --env-file deploy/demo.env --keep 3
```

## Exemplo com diretorio dedicado

```powershell
python scripts/run_scheduled_backup.py --stack production-foundation --env-file deploy/production.env --output-dir backups/production-foundation --keep 7
```

## Exemplo de cron

```cron
0 2 * * * cd /srv/freight-cost-risk-analytics-v2 && /usr/bin/python3 scripts/run_scheduled_backup.py --stack production-foundation --env-file deploy/production.env --keep 7 >> logs/backup-schedule.log 2>&1
```

## Exemplo de Task Scheduler

Programa:

```text
python
```

Argumentos:

```text
scripts/run_scheduled_backup.py --stack demo --env-file deploy/demo.env --keep 3
```

Iniciar em:

```text
C:\caminho\para\freight-cost-risk-analytics-v2
```

## Cuidados operacionais

- o scheduler deve apontar para um env file real do ambiente
- dumps reais continuam fora do versionamento
- o `--keep` so faz pruning local simples no diretorio alvo
- antes de agendar em ambiente mais sensivel, confirme que backup e restore continuam passando localmente

## O que ainda nao cobre

- scheduler real no repositorio
- storage remoto
- criptografia
- alertas de falha
- DR completo
