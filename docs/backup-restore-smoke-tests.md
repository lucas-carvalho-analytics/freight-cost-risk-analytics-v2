# Backup/Restore Smoke Tests

Esta fase adiciona uma validacao automatizavel do fluxo de backup e restore do Postgres, sem prometer DR completo.

## O que a fundacao cobre

- sobe um stack controlado de demo
- insere um dado sentinela no banco
- executa o backup via script operacional
- confirma dump e metadata sidecar
- valida campos como `sha256`, `stack`, `database` e `file_name`
- remove o dado sentinela
- executa restore via script operacional
- confirma retorno do dado
- derruba o ambiente ao final

## O que ela ainda nao cobre

- scheduler de backup
- storage remoto
- restore point-in-time
- DR completo
- validacao automatica recorrente fora do smoke test

## Como rodar localmente

```powershell
python scripts/smoke_test_backup_restore.py
```

## Como entra no CI

O workflow de CI passa a incluir um job separado para o smoke test de backup/restore, alem dos jobs de:

- backend
- frontend
- compose/config
- smoke tests de demo
- smoke tests de production foundation

## Leitura pratica

Se esse smoke test falhar:

1. rode o script localmente
2. observe `docker compose ps`
3. observe os logs dos servicos
4. corrija primeiro problemas de backup, metadata, hash ou restore
