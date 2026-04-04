# Tutorial do Usuário Final

Bem-vindo! Este tutorial ensina como instalar e usar o sistema de analytics logístico. Você não precisa ter experiência técnica — o instalador cuida de tudo.

---

## 1. O que é este sistema

O **Freight Cost Risk Analytics** é um painel online para acompanhar a operação logística da empresa. Com ele, você pode:

- Ver indicadores de frete, ad valorem e ocorrências
- Filtrar por período, origem, destino, transportadora e tipo de veículo
- Comparar custos entre transportadoras em gráfico
- Analisar o risco por destino de entrega
- Tudo protegido por login com e-mail e senha

O sistema roda na sua máquina e você acessa pelo navegador, como qualquer site.

---

## 2. Como instalar

O instalador verifica tudo que precisa, baixa o projeto, configura e inicia o sistema automaticamente.

### No Windows

1. Baixe o arquivo `instalar.bat` do projeto
2. Dê **duplo-clique** no arquivo
3. Se o Windows perguntar se deseja executar, clique em **"Executar assim mesmo"**
4. Siga as instruções na tela

### No Linux ou macOS

1. Baixe o arquivo `instalar.sh` do projeto
2. Abra o terminal na pasta onde baixou o arquivo
3. Execute:
   ```bash
   bash instalar.sh
   ```

### O que o instalador faz

O instalador trabalha em 8 etapas automáticas:

| Etapa | O que faz |
|---|---|
| 1 | Detecta seu sistema operacional |
| 2 | Verifica se Docker, Python e Git estão instalados |
| 3 | Cria a configuração do sistema automaticamente |
| 4 | Inicia os serviços (banco de dados, backend e frontend) |
| 5 | Aguarda tudo ficar pronto |
| 6 | Cria o usuário de acesso |
| 7 | Carrega 5.000 registros de demonstração |
| 8 | Configura o endereço local e abre o navegador |

Se algum programa estiver faltando (Docker, Python ou Git), o instalador avisa e abre a página de download para você. Depois de instalar o que faltou, é só rodar o instalador de novo.

### Quando terminar

O sistema abre sozinho no navegador. Você vai ver algo assim na tela do instalador:

```
  ✅  SISTEMA PRONTO!

  🌐 Acesse no navegador:
     http://freight-analytics.local:8080

  🔐 Login:
     E-mail:  admin@demo.local
     Senha:   demo1234
```

---

## 3. Como acessar

Depois da instalação, o navegador abre automaticamente. Se precisar acessar manualmente:

1. Abra o navegador (Chrome, Firefox ou Edge)
2. Acesse: `http://freight-analytics.local:8080`
   - Se esse endereço não funcionar, use: `http://127.0.0.1:8080`
3. Na tela de login:
   - **E-mail:** `admin@demo.local`
   - **Senha:** `demo1234`
4. Clique em **Entrar**

---

## 4. Como usar o dashboard

### Indicadores

No topo do dashboard, três cards mostram os números principais da operação:

| Indicador | O que mostra |
|---|---|
| **Frete total** | Soma dos custos de frete dos embarques filtrados |
| **Ad valorem total** | Soma dos valores de ad valorem |
| **Taxa de ocorrências** | Percentual de embarques com sinistro ou atraso |

### Gráficos

Abaixo dos indicadores:

- **Custo por transportadora** — compara custos entre empresas de transporte
- **Risco por destino** — mostra o nível de risco por localidade

### Filtros

A seção **Filtros operacionais** permite refinar os dados:

| Filtro | Exemplo |
|---|---|
| Data inicial e final | Analisar só o mês de março |
| Origem | Ver embarques que saíram de Suape |
| Destino | Focar em entregas para Caruaru |
| Transportadora | Analisar uma transportadora específica |
| Tipo de veículo | Filtrar por Carreta, Truck, etc. |

Os dados atualizam automaticamente ao mudar qualquer filtro. Para voltar ao estado original, clique em **Limpar filtros**.

### Sessão

A sessão dura 60 minutos. Quando expirar, o sistema volta para a tela de login. É só entrar de novo.

---

## 5. Como parar e ligar o sistema

### Parar

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down
```

Os dados ficam salvos. Nada é perdido.

### Ligar novamente

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up -d
```

Aguarde cerca de 30 segundos e acesse o endereço no navegador.

### Recomeçar do zero

Se quiser **apagar tudo** e reinstalar:

```bash
docker compose --env-file deploy/demo.env -f docker-compose.demo.yml down -v
```

Depois, rode o instalador novamente.

> **Atenção:** esse comando apaga todos os dados. Só use se realmente quiser recomeçar do zero.

---

## 6. Como saber se está tudo certo

| O que verificar | Como fazer | O que deve aparecer |
|---|---|---|
| Sistema acessível | Abrir o endereço no navegador | Tela de login |
| Login funciona | Entrar com e-mail e senha | Dashboard abre |
| Indicadores carregam | Olhar os 3 cards no topo | Números aparecem |
| Gráficos aparecem | Rolar a tela | Gráficos visíveis |
| Filtros respondem | Selecionar qualquer filtro | Dados mudam |

---

## 7. Problemas comuns

### "A página não abre"

- O sistema pode estar subindo. Aguarde 1 minuto e recarregue.
- Verifique se o Docker Desktop está aberto.
- Tente o endereço alternativo: `http://127.0.0.1:8080`

### "O login não funciona"

- Confirme: e-mail `admin@demo.local`, senha `demo1234`.
- Se rodou a instalação manual, o usuário pode não ter sido criado. Execute:
  ```bash
  docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@demo.local --full-name "Admin Demo" --password demo1234
  ```

### "Dashboard sem dados"

- Clique em **Limpar filtros** — algum filtro pode estar restringindo demais.
- Se o banco está vazio, rode o instalador novamente.

### "Porta 8080 ocupada"

1. Abra o arquivo `deploy/demo.env`
2. Troque `DEMO_PORT=8080` por outra porta (ex: `9090`)
3. Reinicie o sistema

### "O instalador diz que falta Docker/Python/Git"

O instalador abre a página de download automaticamente. Instale o programa indicado, e depois rode o instalador de novo.

---

## 8. Backup

### Fazer backup

```bash
python3 scripts/backup_postgres_compose.py --stack demo --env-file deploy/demo.env
```

No Windows, use `python` em vez de `python3`.

O backup é salvo em `backups/demo/`.

### Restaurar

> **Atenção:** substitui todos os dados atuais.

```bash
python3 scripts/restore_postgres_compose.py --stack demo --env-file deploy/demo.env --input backups/demo/NOME-DO-ARQUIVO.dump --yes-i-understand-this-will-overwrite-data
```

---

## 9. Importar dados reais

Para usar dados reais da empresa:

1. Prepare um CSV com as colunas: Data do Embarque, Origem, Destino, Valor da Carga (R$), Tipo de Veículo, Transportadora, Taxa Ad Valorem (%), Frete Peso (R$)
2. Coloque o arquivo em `backend/data/`
3. Execute:
   ```bash
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/nome-do-seu-arquivo.csv
   ```

---

## 10. Checklist

- [ ] Rodei o instalador (`instalar.bat` ou `instalar.sh`)
- [ ] O sistema mostrou "SISTEMA PRONTO!"
- [ ] Consigo acessar no navegador
- [ ] Consigo fazer login
- [ ] Dashboard mostra indicadores e gráficos
- [ ] Filtros funcionam
- [ ] Sei como parar e ligar o sistema

---

*Para configurações avançadas, consulte `docs/production-readiness.md` e `docs/secrets-and-operational-config.md`.*
