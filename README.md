<div align="center">

# 📊 Freight Cost Risk Analytics

**Painel de analytics logístico para acompanhar custos de frete, ad valorem e ocorrências em tempo real.**

[![CI](https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2/actions)

[Instalar](#-instalação-rápida) · [Tutorial do Usuário](docs/tutorial-usuario-final.md) · [Documentação Técnica](#-documentação-técnica) · [API](#-api)

</div>

---

## ✨ O que este sistema faz

| Recurso | Descrição |
|---|---|
| 📈 **Dashboard interativo** | Indicadores de frete total, ad valorem e taxa de ocorrências |
| 🔍 **Filtros operacionais** | Por período, origem, destino, transportadora e tipo de veículo |
| 📊 **Gráficos analíticos** | Custo por transportadora e risco por destino |
| 🔐 **Acesso protegido** | Login com autenticação JWT |
| 💾 **Backup criptografado** | Backup, criptografia AES-256 e restore automatizado |
| 🐳 **1 comando para instalar** | Instalador automático via Docker |

---

## 🚀 Instalação Rápida

> **Pré-requisito:** [Docker Desktop](https://docs.docker.com/get-docker/) instalado e aberto.

### Windows

Baixe e dê **duplo-clique** no arquivo [`instalar.bat`](instalar.bat).

O instalador verifica tudo que precisa, baixa, configura e inicia o sistema.

### Linux / macOS

```bash
git clone https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2.git
cd freight-cost-risk-analytics-v2
bash instalar.sh
```

### O que acontece

O instalador faz **tudo automaticamente** em 8 etapas:

```
  [1/8] Detecta seu sistema operacional
  [2/8] Verifica Docker, Python e Git
  [3/8] Cria configuração com chave de segurança
  [4/8] Inicia banco, backend e frontend
  [5/8] Aguarda tudo ficar saudável
  [6/8] Cria o usuário de acesso
  [7/8] Carrega 5.000 registros de demonstração
  [8/8] Configura o endereço e abre o navegador
```

### Resultado

Quando terminar, o navegador abre sozinho:

```
  ✅ SISTEMA PRONTO!

  🌐 Acesse: http://freight-analytics.local:8080

  🔐 Login:
     E-mail:  operador@freight-analytics.com
     Senha:   Freight@2024
```

> 📖 **Primeiro uso?** Leia o [Tutorial do Usuário](docs/tutorial-usuario-final.md) para aprender a usar o dashboard.

---

## ⚡ Comandos do dia a dia

| Ação | Comando |
|---|---|
| **Parar** | `docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down` |
| **Ligar** | `docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up -d` |
| **Ver logs** | `docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs -f` |
| **Reiniciar** | Parar → Ligar |
| **Recomeçar do zero** | Parar com `down -v` → rodar o instalador de novo |

---

## 🛠 Stack Técnica

<table>
<tr>
<td><strong>Backend</strong></td>
<td>Python 3.11 · FastAPI · SQLAlchemy 2 · Alembic · Pandas · Pytest</td>
</tr>
<tr>
<td><strong>Frontend</strong></td>
<td>React · TypeScript · Vite · Tailwind CSS</td>
</tr>
<tr>
<td><strong>Infraestrutura</strong></td>
<td>PostgreSQL 16 · Nginx · Docker Compose</td>
</tr>
<tr>
<td><strong>Segurança</strong></td>
<td>JWT (HS256) · AES-256-CBC (backups) · PBKDF2</td>
</tr>
</table>

---

## 📂 Estrutura do Projeto

```text
.
├── backend/                  # API FastAPI + lógica de negócio
│   ├── app/                  # Código principal
│   ├── alembic/              # Migrações do banco
│   ├── tests/                # Testes automatizados
│   └── docker/               # Entrypoints
├── frontend/                 # Dashboard React
│   ├── src/pages/            # LoginPage, DashboardPage
│   ├── src/components/       # FiltersPanel, Charts, MetricCard
│   └── src/services/         # Chamadas à API
├── scripts/                  # Operações: backup, restore, alertas
├── deploy/                   # Configurações por ambiente
├── docs/                     # Documentação completa
├── instalar.bat              # Instalador Windows
├── instalar.sh               # Instalador Linux/macOS
├── quick-start.py            # Motor do instalador (cross-platform)
└── docker-compose.demo.yml   # Stack de demonstração
```

---

## 🔌 API

### Endpoints públicos

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/health` | Status do sistema |
| `GET` | `/api/v1/ready` | Readiness check |
| `POST` | `/api/v1/auth/login` | Autenticação (retorna JWT) |
| `GET` | `/api/v1/auth/me` | Dados do usuário logado |

### KPIs protegidos (requer JWT)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/kpis/frete-total` | Soma do frete |
| `GET` | `/api/v1/kpis/advalorem-total` | Soma do ad valorem |
| `GET` | `/api/v1/kpis/taxa-ocorrencias` | Taxa de sinistros e atrasos |
| `GET` | `/api/v1/kpis/custo-por-transportadora` | Breakdown por transportadora |
| `GET` | `/api/v1/kpis/custo-risco-destino` | Análise de risco por destino |

### Filtros protegidos (requer JWT)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/filtros/origens` | Lista de origens disponíveis |
| `GET` | `/api/v1/filtros/destinos` | Lista de destinos |
| `GET` | `/api/v1/filtros/transportadoras` | Lista de transportadoras |
| `GET` | `/api/v1/filtros/tipos-veiculo` | Tipos de veículo |

Todos os filtros são aplicáveis como query parameters nos endpoints de KPI.

---

## 💾 Backup e Segurança

O sistema inclui pipeline completo de backup com criptografia:

```
dump → criptografia AES-256 → upload remoto → limpeza do arquivo original
```

| Operação | Comando |
|---|---|
| **Backup** | `python scripts/backup_postgres_compose.py --stack demo --env-file deploy/demo.env` |
| **Restore** | `python scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/ARQUIVO.dump --yes-i-understand-this-will-overwrite-data` |
| **Backup agendado** | `python scripts/run_scheduled_backup.py --stack demo --env-file deploy/demo.env --keep 3` |

A criptografia é automática quando `BACKUP_ENCRYPTION_KEY` está configurada. O restore detecta e descriptografa arquivos `.enc` automaticamente.

> 📖 Detalhes em [docs/backup-restore-foundation.md](docs/backup-restore-foundation.md)

---

## 📖 Documentação Técnica

| Documento | Conteúdo |
|---|---|
| [Tutorial do Usuário](docs/tutorial-usuario-final.md) | Guia completo para o usuário final |
| [Deploy Demo](docs/deploy-demo.md) | Arquitetura same-origin e setup |
| [Production Readiness](docs/production-readiness.md) | Base de preparação para produção |
| [Secrets e Config](docs/secrets-and-operational-config.md) | Contratos de variáveis por ambiente |
| [Observabilidade](docs/observability-foundation.md) | Logs, health e readiness |
| [CI/CD](docs/ci-cd-foundation.md) | Pipeline de integração contínua |
| [Backup/Restore](docs/backup-restore-foundation.md) | Operação de backup e restore |
| [Criptografia](docs/backup-encryption-foundation.md) | Criptografia AES-256 dos backups |
| [Restore Criptografado](docs/encrypted-restore-flow-foundation.md) | Restore de backups criptografados |
| [Alertas](docs/backup-failure-alerting-foundation.md) | Alertas de falha de backup |
| [Storage Remoto](docs/backup-remote-storage-foundation.md) | Upload para storage externo |
| [Scheduling](docs/backup-scheduling-foundation.md) | Agendamento de backups |
| [V2 Release Runbook](docs/v2-release-runbook.md) | Certificação operacional da V2 |

---

## 🧑‍💻 Desenvolvimento Local

<details>
<summary><strong>Backend (sem Docker)</strong></summary>

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
docker compose up -d             # sobe apenas o PostgreSQL
alembic upgrade head
uvicorn app.main:app --reload
```

Criar o admin:

```bash
python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
```

</details>

<details>
<summary><strong>Frontend (sem Docker)</strong></summary>

```bash
cd frontend
npm install
npm run dev
```

O dev server usa proxy para `http://127.0.0.1:8000` automaticamente.

</details>

<details>
<summary><strong>Testes</strong></summary>

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run lint && npm run build

# Validação de stacks
docker compose -f docker-compose.demo.yml config -q
docker compose -f docker-compose.production-foundation.yml config -q
```

</details>

---

## 📋 Requisitos de Instalação

| Programa | Obrigatório | Link |
|---|---|---|
| Docker Desktop | ✅ Sim | [docker.com/get-docker](https://docs.docker.com/get-docker/) |
| Python 3.11+ | ✅ Sim | [python.org/downloads](https://www.python.org/downloads/) |
| Git | ✅ Sim | [git-scm.com/downloads](https://git-scm.com/downloads) |
| Node.js 18+ | Só para dev | [nodejs.org](https://nodejs.org/) |

> O instalador verifica automaticamente se Docker, Python e Git estão instalados. Se faltou algo, ele abre a página de download no navegador.

---

<div align="center">

**Feito com foco em engenharia de dados, segurança operacional e experiência do usuário.**

[⬆ Voltar ao topo](#-freight-cost-risk-analytics)

</div>
