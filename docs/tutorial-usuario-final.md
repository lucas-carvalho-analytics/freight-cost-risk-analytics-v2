# Tutorial do Usuário Final

Este tutorial ensina como instalar, acessar e usar o sistema de analytics logístico no dia a dia. Ele foi feito para quem vai operar o sistema na empresa, mesmo sem experiência técnica anterior com este projeto.

---

## 1. O que é este sistema

O Freight Cost Risk Analytics é um painel web para acompanhar a operação logística da empresa. Com ele, você pode:

- Ver indicadores de custo de frete, ad valorem e ocorrências em tempo real
- Filtrar por período, origem, destino, transportadora e tipo de veículo
- Comparar o custo entre transportadoras em gráfico
- Analisar o risco por destino de entrega
- Acessar tudo de forma protegida por login

O sistema funciona na sua máquina usando Docker. Você acessa pelo navegador, como qualquer site.

---

## 2. O que você precisa ter instalado

Três programas são necessários:

**Docker Desktop** — roda o sistema sem precisar instalar bancos de dados ou servidores manualmente.
- Windows: [docker.com/desktop/windows](https://docs.docker.com/desktop/install/windows-install/)
- Linux: [docker.com/engine/install](https://docs.docker.com/engine/install/)
- macOS: [docker.com/desktop/mac](https://docs.docker.com/desktop/install/mac-install/)

**Python 3** — executa o script de instalação automática.
- [python.org/downloads](https://www.python.org/downloads/)
- No Windows, marque a opção **"Add Python to PATH"** durante a instalação

**Git** — baixa o projeto do repositório.
- [git-scm.com/downloads](https://git-scm.com/downloads)

### Como verificar

Abra o terminal e execute estes comandos, um por vez:

```bash
docker --version
git --version
```

No Linux ou macOS:
```bash
python3 --version
```

No Windows:
```powershell
python --version
```

Se cada comando mostrar um número de versão, está tudo certo. Se aparecer erro em algum, instale esse programa antes de continuar.

> **Importante:** o Docker Desktop precisa estar **aberto e rodando** antes de prosseguir.

---

## 3. Como instalar o sistema

Abra o terminal e execute estes comandos, um por vez:

**Passo 1 — Baixar o projeto:**

```bash
git clone https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2.git
```

**Passo 2 — Entrar na pasta do projeto:**

```bash
cd freight-cost-risk-analytics-v2
```

**Passo 3 — Executar a instalação automática:**

No Linux ou macOS:
```bash
python3 quick-start.py
```

No Windows:
```powershell
python quick-start.py
```

### O que acontece durante a instalação

O script faz tudo sozinho:

1. Detecta seu sistema operacional (Linux, macOS ou Windows)
2. Verifica se o Docker está funcionando
3. Cria o arquivo de configuração com uma chave de segurança gerada automaticamente
4. Inicia os serviços (banco de dados, backend e frontend)
5. Aguarda todos ficarem saudáveis
6. Cria o usuário de acesso
7. Gera e importa dados de demonstração

Na primeira vez, pode levar alguns minutos enquanto o Docker baixa o que precisa.

### Quando a instalação terminar

Você vai ver esta mensagem:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅  Sistema pronto!

  Abra no navegador:
    http://127.0.0.1:8080

  Login:
    E-mail:  admin@demo.local
    Senha:   demo1234

  Comandos úteis:
    Parar:    docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
    Subir:    docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up -d
    Logs:     docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs -f
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Pronto. O sistema está funcionando.

---

## 4. Como acessar

1. Abra o navegador (Chrome, Firefox ou Edge)
2. Digite na barra de endereço: `http://127.0.0.1:8080`
3. Na tela de login, preencha:
   - **E-mail:** `admin@demo.local`
   - **Senha:** `demo1234`
4. Clique em **Entrar**

O dashboard vai abrir com dados de demonstração já carregados.

---

## 5. Como usar o dashboard

### Indicadores

No topo do dashboard, três cards mostram os números principais:

| Indicador | O que mostra |
|---|---|
| **Frete total** | Soma dos custos de frete dos embarques filtrados |
| **Ad valorem total** | Soma dos valores de ad valorem |
| **Taxa de ocorrências** | Percentual de embarques com sinistro ou atraso |

Cada card também mostra quantos embarques foram considerados no cálculo.

### Gráficos

Abaixo dos indicadores, dois gráficos permitem análise visual:

- **Custo por transportadora** — compara os custos entre as empresas de transporte
- **Risco por destino** — mostra o nível de risco em cada localidade de entrega

### Filtros

A seção **Filtros operacionais** fica no topo e permite refinar os dados exibidos:

| Filtro | Exemplo de uso |
|---|---|
| Data inicial e final | Analisar apenas o mês de março |
| Origem | Ver embarques que saíram de Suape |
| Destino | Focar em entregas para Caruaru |
| Transportadora | Comparar uma transportadora específica |
| Tipo de veículo | Filtrar por Carreta, Truck, etc. |

Os indicadores e gráficos atualizam automaticamente quando você muda qualquer filtro.

Para voltar a ver todos os dados, clique em **Limpar filtros**.

### Sessão

A sessão de login dura 60 minutos. Quando expirar, o sistema volta para a tela de login com um aviso. É só entrar novamente.

---

## 6. Como parar e ligar o sistema

### Parar

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
```

Os dados ficam salvos. Nada é perdido ao parar o sistema.

### Ligar novamente

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up -d
```

Aguarde cerca de 30 segundos e acesse `http://127.0.0.1:8080`.

### Reiniciar (se algo estiver estranho)

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up --build -d
```

### Recomeçar do zero

Se quiser apagar **todos os dados** e voltar ao estado inicial:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down -v
```

Depois, rode o quick-start novamente:

No Linux ou macOS:
```bash
python3 quick-start.py
```

No Windows:
```powershell
python quick-start.py
```

> **Atenção:** o comando `down -v` apaga tudo do banco de dados. Só use se realmente quiser recomeçar do zero.

---

## 7. Como saber se está tudo certo

Use esta tabela para conferir passo a passo:

| O que testar | Como fazer | O que você deve ver |
|---|---|---|
| Sistema acessível | Abra `http://127.0.0.1:8080` | Tela de login aparece |
| Login funciona | Digite `admin@demo.local` / `demo1234` | Dashboard abre |
| Indicadores carregam | Olhe os 3 cards no topo | Números de frete, ad valorem e ocorrências |
| Gráficos aparecem | Role a tela para baixo | Gráficos de transportadora e destino |
| Filtros respondem | Selecione qualquer filtro | Indicadores e gráficos mudam |

Para verificar pelo terminal:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml ps
```

Todos os serviços devem mostrar `healthy` ou `running`.

---

## 8. Problemas comuns

### "Não consigo abrir a página no navegador"

- O sistema pode ainda estar subindo. Aguarde 1 minuto e recarregue.
- Confira se o Docker Desktop está aberto e rodando.
- Verifique os containers:
  ```bash
  docker compose --env-file deploy/demo.env -f docker-compose.demo.yml ps
  ```

### "O login não funciona"

- Confira se está digitando exatamente: `admin@demo.local` e `demo1234`.
- Se configurou manualmente (sem o quick-start), o usuário pode não ter sido criado. Execute:
  ```bash
  docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@demo.local --full-name "Admin Demo" --password demo1234
  ```

### "Dashboard mostra: Sem dados para exibir"

- Clique em **Limpar filtros** — algum filtro pode estar restringindo demais.
- Se o banco está vazio, rode o `quick-start.py` novamente.

### "A porta 8080 está ocupada"

1. Abra o arquivo `deploy/demo.env` em um editor de texto
2. Troque `DEMO_PORT=8080` por outra porta, como `DEMO_PORT=9090`
3. Reinicie o sistema
4. Acesse `http://127.0.0.1:9090`

### "O quick-start.py deu erro"

- Confirme que o Docker Desktop está aberto e funcionando
- Confirme que a internet está funcionando (necessário na primeira execução)
- Veja os logs para mais detalhes:
  ```bash
  docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs
  ```

---

## 9. Backup e recuperação

O sistema possui ferramentas para proteger os dados do banco.

### Fazer backup

Com o sistema rodando, execute:

```bash
python3 scripts/backup_postgres_compose.py --stack demo --env-file deploy/demo.env
```

No Windows, troque `python3` por `python`.

O backup será salvo na pasta `backups/demo/` com a data e hora no nome do arquivo.

### Restaurar um backup

> **Atenção:** este comando substitui todos os dados atuais pelo conteúdo do backup.

```bash
python3 scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/NOME-DO-ARQUIVO.dump --yes-i-understand-this-will-overwrite-data
```

Troque `NOME-DO-ARQUIVO` pelo nome real do arquivo de backup.

### Restaurar backup criptografado

Se o backup foi criptografado (nome termina em `.dump.enc`), configure a chave antes:

No Linux ou macOS:
```bash
export BACKUP_ENCRYPTION_KEY="sua-chave-de-criptografia"
```

No Windows:
```powershell
$env:BACKUP_ENCRYPTION_KEY="sua-chave-de-criptografia"
```

Depois, execute o mesmo comando de restore usando o arquivo `.dump.enc`.

---

## 10. Importar dados reais

Se a empresa quiser usar dados reais em vez dos dados de demonstração:

1. Prepare um arquivo CSV com estas colunas:
   - Data do Embarque
   - Origem
   - Destino
   - Valor da Carga (R$)
   - Tipo de Veículo
   - Transportadora
   - Taxa Ad Valorem (%)
   - Frete Peso (R$)

2. Coloque o arquivo na pasta `backend/data/` do projeto

3. Execute:
   ```bash
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/nome-do-seu-arquivo.csv
   ```

Os dados novos serão adicionados ao banco sem remover os que já existem.

---

## 11. Checklist de verificação

Use esta lista para confirmar que tudo está funcionando:

- [ ] Docker Desktop instalado e aberto
- [ ] Python 3 instalado
- [ ] Git instalado
- [ ] Executei o `quick-start.py` com sucesso
- [ ] Consigo abrir `http://127.0.0.1:8080`
- [ ] Consigo fazer login com `admin@demo.local` / `demo1234`
- [ ] Indicadores e gráficos carregam no dashboard
- [ ] Filtros funcionam e atualizam os dados
- [ ] Sei como parar o sistema
- [ ] Sei como ligar o sistema novamente

---

## 12. Instalação manual (alternativa)

Se o `quick-start.py` não funcionar no seu ambiente, você pode fazer a instalação passo a passo:

**1.** Copie o arquivo de configuração:

No Linux ou macOS:
```bash
cp deploy/demo.env.example deploy/demo.env
```

No Windows:
```powershell
Copy-Item deploy/demo.env.example deploy/demo.env
```

**2.** Abra `deploy/demo.env` em um editor de texto e troque o valor de `JWT_SECRET_KEY` por um texto longo (pelo menos 32 caracteres). Exemplo: `minha-chave-longa-aleatoria-segura-2026`

**3.** Inicie o sistema:
```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up --build -d
```

**4.** Aguarde cerca de 1 minuto

**5.** Crie o usuário de acesso:
```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@demo.local --full-name "Admin Demo" --password demo1234
```

**6.** Gere e importe os dados de demonstração:

No Linux ou macOS:
```bash
python3 gerar_dataset_logistica_pe.py
cp dataset_operacoes_logisticas_pe.csv backend/data/
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/dataset_operacoes_logisticas_pe.csv
```

No Windows:
```powershell
python gerar_dataset_logistica_pe.py
Copy-Item dataset_operacoes_logisticas_pe.csv backend/data/
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/dataset_operacoes_logisticas_pe.csv
```

**7.** Acesse `http://127.0.0.1:8080` e faça login

---

*Para ambientes de produção ou configurações avançadas, consulte `docs/production-readiness.md` e `docs/secrets-and-operational-config.md`.*
