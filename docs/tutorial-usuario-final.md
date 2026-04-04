# Tutorial do Usuário Final

Este tutorial explica como instalar e usar o sistema de analytics logístico. Ele foi escrito para quem vai operar o sistema no dia a dia, mesmo sem experiência prévia com este projeto.

---

## 1. O que é este sistema

Este sistema analisa custos de frete, ad valorem e ocorrências de operações logísticas. Ele permite que você:

- Visualize indicadores (KPIs) da operação em um dashboard web
- Filtre os dados por origem, destino, transportadora, tipo de veículo e período
- Veja gráficos de custo por transportadora e risco por destino
- Acompanhe a taxa de ocorrências (sinistros e atrasos)
- Acesse tudo de forma protegida por login com e-mail e senha

O sistema roda na sua máquina usando Docker. Você acessa pelo navegador, como qualquer site.

---

## 2. O que você precisa antes de começar

Confirme que você tem estes dois programas instalados:

- **Docker Desktop** — faz o sistema funcionar sem instalar nada extra
  - Windows: [https://docs.docker.com/desktop/install/windows-install/](https://docs.docker.com/desktop/install/windows-install/)
  - Linux: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
- **Git** — para baixar o projeto
  - [https://git-scm.com/downloads](https://git-scm.com/downloads)

Para confirmar que estão funcionando, abra o terminal e execute:

```bash
docker --version
git --version
```

Se aparecer a versão de cada um, está tudo certo. Se aparecer erro, instale o programa correspondente antes de continuar.

> **Importante:** o Docker Desktop precisa estar **aberto e rodando** antes de iniciar o sistema.

---

## 3. Como instalar e iniciar o sistema

São 3 comandos. Copie e cole no terminal, um por vez:

```bash
git clone https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2.git
```

```bash
cd freight-cost-risk-analytics-v2
```

```bash
bash quick-start.sh
```

O script vai:

1. Verificar se o Docker está funcionando
2. Criar o arquivo de configuração automaticamente
3. Iniciar todos os serviços
4. Aguardar tudo ficar saudável
5. Criar o usuário de acesso
6. Carregar dados de demonstração

Na primeira vez, pode levar alguns minutos enquanto o Docker baixa as imagens necessárias.

Quando terminar, você vai ver esta mensagem:

```
✅  Sistema pronto!

  Abra no navegador:
    http://127.0.0.1:8080

  Login:
    E-mail:  admin@demo.local
    Senha:   demo1234
```

---

## 4. Como acessar o sistema

1. Abra o navegador (Chrome, Firefox ou Edge)
2. Acesse `http://127.0.0.1:8080`
3. Na tela de login, digite:
   - **E-mail:** `admin@demo.local`
   - **Senha:** `demo1234`
4. Clique em **Entrar**

Você será levado direto ao dashboard com os dados de demonstração carregados.

---

## 5. Como usar o sistema no dia a dia

### Entender o dashboard

O dashboard mostra três indicadores principais no topo:

- **Frete total** — soma dos custos de frete dos embarques filtrados
- **Ad valorem total** — soma dos valores de ad valorem
- **Taxa de ocorrências** — percentual de embarques com ocorrência (sinistro ou atraso)

Abaixo dos indicadores, dois gráficos:

- **Custo por transportadora** — comparação entre as transportadoras
- **Risco por destino** — análise de risco por localidade de destino

### Usar os filtros

No topo do dashboard, a seção **Filtros operacionais** permite refinar os dados:

- **Data inicial** e **Data final** — período de análise
- **Origem** — local de saída (ex: Suape, Jaboatão)
- **Destino** — local de entrega
- **Transportadora** — empresa de transporte
- **Tipo de veículo** — VUC, Toco, Truck, Carreta ou Bitrem

Os indicadores e gráficos atualizam automaticamente ao alterar qualquer filtro.

Para voltar a ver todos os dados, clique em **Limpar filtros**.

### Sessão

Se a sessão expirar (padrão: 60 minutos), o sistema pede login novamente. Uma mensagem avisando que a sessão expirou aparece na tela.

---

## 6. Como parar e iniciar novamente

### Parar o sistema

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
```

Os dados são preservados. Você não perde nada ao parar.

### Iniciar novamente

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up -d
```

### Reiniciar se algo não estiver funcionando bem

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up --build -d
```

### Recomeçar do zero

Se quiser apagar tudo e começar limpo:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down -v
bash quick-start.sh
```

> **Atenção:** o `down -v` apaga todos os dados do banco. Só use se realmente quiser recomeçar.

---

## 7. Como saber se está tudo funcionando

| Verificação | Como testar | Resultado esperado |
|---|---|---|
| Sistema acessível | Abra `http://127.0.0.1:8080` | Tela de login aparece |
| Login funciona | Entre com `admin@demo.local` / `demo1234` | Dashboard abre |
| Dashboard carrega | Veja se indicadores aparecem | KPIs e gráficos visíveis |
| Filtros respondem | Selecione qualquer filtro | Dados atualizam |

Pelo terminal, você pode verificar a saúde dos serviços:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml ps
```

Todos devem mostrar status `healthy` ou `running`.

---

## 8. Problemas comuns e como resolver

### A página não abre no navegador

- O sistema pode ainda estar subindo. Aguarde 1 minuto e tente novamente.
- Verifique se o Docker Desktop está aberto e rodando.
- Verifique se os containers estão ativos:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml ps
```

### O login não funciona

- Confirme que está usando `admin@demo.local` e `demo1234`.
- Se criou o sistema manualmente (sem o `quick-start.sh`), pode ser que o usuário admin não tenha sido criado. Execute:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@demo.local --full-name "Admin Demo" --password demo1234
```

### O dashboard mostra "Sem dados para exibir"

- Os dados podem não ter sido importados. Clique em **Limpar filtros** primeiro.
- Se o banco está vazio, rode o `quick-start.sh` novamente ou importe dados manualmente (veja seção 10).

### Porta ocupada

Se outro programa está usando a porta 8080:

1. Abra o arquivo `deploy/demo.env`
2. Mude `DEMO_PORT=8080` para outra porta (ex: `DEMO_PORT=9090`)
3. Reinicie o sistema
4. Acesse `http://127.0.0.1:9090`

### O quick-start.sh deu erro

- Verifique se o Docker Desktop está realmente aberto
- Verifique se a internet está funcionando (necessário na primeira vez)
- Veja os logs detalhados:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml logs
```

---

## 9. Backup e recuperação

O sistema possui scripts para proteger os dados do banco.

### Fazer backup

Com o sistema rodando:

```bash
python3 scripts/backup_postgres_compose.py --stack demo --env-file deploy/demo.env
```

O backup é salvo na pasta `backups/demo/`.

### Restaurar um backup

> **Atenção:** este comando substitui todos os dados atuais.

```bash
python3 scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/NOME-DO-ARQUIVO.dump --yes-i-understand-this-will-overwrite-data
```

Substitua `NOME-DO-ARQUIVO` pelo nome real do arquivo de backup.

Se o backup estiver criptografado (`.dump.enc`), configure a chave de criptografia antes:

```bash
export BACKUP_ENCRYPTION_KEY="sua-chave"
python3 scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/NOME-DO-ARQUIVO.dump.enc --yes-i-understand-this-will-overwrite-data
```

---

## 10. Importar seus próprios dados

Se você quiser carregar um arquivo CSV com dados reais da operação:

1. Gere ou obtenha o arquivo CSV no formato esperado
2. Coloque o arquivo na pasta `backend/data/`
3. Execute:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/seu-arquivo.csv
```

O CSV deve conter as colunas: Data do Embarque, Origem, Destino, Valor da Carga (R$), Tipo de Veículo, Transportadora, Taxa Ad Valorem (%), Frete Peso (R$).

---

## 11. Checklist rápido

- [ ] Docker Desktop está instalado e aberto
- [ ] Rodei `bash quick-start.sh`
- [ ] O sistema mostrou "Sistema pronto!"
- [ ] Consigo abrir `http://127.0.0.1:8080`
- [ ] Consigo fazer login
- [ ] Dashboard mostra indicadores e gráficos
- [ ] Filtros funcionam
- [ ] Sei como parar (`docker compose ... down`)
- [ ] Sei como subir de novo (`docker compose ... up -d`)

Se todos os itens estão marcados, o sistema está pronto para uso.

---

## 12. Modo manual (alternativo)

Se por algum motivo o `quick-start.sh` não funcionar no seu ambiente, você pode configurar manualmente:

1. Copie o arquivo de configuração:
   ```bash
   cp deploy/demo.env.example deploy/demo.env
   ```

2. Abra `deploy/demo.env` e troque `JWT_SECRET_KEY` por um texto com pelo menos 32 caracteres

3. Inicie o sistema:
   ```bash
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up --build -d
   ```

4. Aguarde os serviços ficarem saudáveis (~1 minuto)

5. Crie o usuário admin:
   ```bash
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@demo.local --full-name "Admin Demo" --password demo1234
   ```

6. Gere e importe o dataset (precisa de Python 3 no computador):
   ```bash
   python3 gerar_dataset_logistica_pe.py
   cp dataset_operacoes_logisticas_pe.csv backend/data/
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/dataset_operacoes_logisticas_pe.csv
   ```

7. Acesse `http://127.0.0.1:8080` e faça login

---

*Para uso em ambientes mais sensíveis, consulte `docs/production-readiness.md` e `docs/secrets-and-operational-config.md`.*
