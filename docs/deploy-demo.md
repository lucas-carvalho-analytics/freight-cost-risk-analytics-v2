# Deploy/Demo

Base simples de ambiente demonstravel com arquitetura same-origin:

- `frontend` buildado em Vite e servido como estatico pelo Nginx
- Nginx exposto para o navegador
- `GET/POST /api/v1/*` proxied para o backend FastAPI
- PostgreSQL rodando na mesma composicao

Essa abordagem evita depender de CORS no ambiente de demo e preserva o fluxo local de desenvolvimento separado:

- dev local do frontend continua com `npm run dev`
- dev local do backend continua com `uvicorn app.main:app --reload`
- demo local usa `docker compose -f docker-compose.demo.yml`

## Arquivos

- `docker-compose.demo.yml`
- `deploy/demo.env.example`
- `backend/Dockerfile.demo`
- `backend/docker/demo-entrypoint.sh`
- `frontend/Dockerfile`
- `frontend/nginx.demo.conf`

## Subida rapida

1. Copie o arquivo de ambiente:

   ```powershell
   Copy-Item deploy/demo.env.example deploy/demo.env
   ```

2. Suba o stack:

   ```powershell
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml up --build
   ```

3. Acesse o frontend:

   - `http://127.0.0.1:8080`

4. Crie o admin inicial:

   ```powershell
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.seed_admin --email admin@example.com --full-name "Admin"
   ```

5. Se quiser carregar dataset no ambiente de demo:

   - coloque o CSV em `backend/data/`
   - depois execute:

   ```powershell
   docker compose --env-file deploy/demo.env -f docker-compose.demo.yml exec backend python -m app.scripts.import_shipments /app/data/seu-arquivo.csv
   ```

## Observacoes

- o backend nao muda de regra de negocio
- o reverse proxy fica restrito ao Nginx do frontend
- o build do frontend usa `VITE_API_BASE_URL=/api/v1`, coerente com same-origin
- para publicar de verdade ainda faltam secret management, dominio/TLS, estrategia de imagem e observabilidade de runtime
