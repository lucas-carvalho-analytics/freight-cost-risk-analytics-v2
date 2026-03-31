# Secrets and Operational Config

Esta fase nao fecha producao. Ela reduz risco operacional deixando mais explicito:

- o que cada ambiente precisa configurar
- quais placeholders nao podem sobreviver em demo/producao
- como tratar secrets sem colocar valores reais no repo

## Contrato curto por ambiente

### Development

Arquivo base:

- `backend/.env.example`

Objetivo:

- desenvolvimento local
- iteracao rapida
- menor atrito operacional

Minimo obrigatorio:

- `JWT_SECRET_KEY` real
- `DATABASE_URL` ou `POSTGRES_*` coerentes com seu banco local

### Demo

Arquivo base:

- `deploy/demo.env.example`

Objetivo:

- ambiente demonstravel
- same-origin com Nginx e `/api/v1`

Minimo obrigatorio:

- `JWT_SECRET_KEY` real com pelo menos 32 caracteres
- revisar `POSTGRES_PASSWORD` se o ambiente deixar de ser descartavel

### Production foundation

Arquivo base:

- `deploy/production.env.example`

Objetivo:

- preparar operacao mais seria sem prometer producao pronta

Minimo obrigatorio:

- `POSTGRES_PASSWORD` real
- `JWT_SECRET_KEY` real com pelo menos 32 caracteres
- `WEB_CONCURRENCY >= 1`

## Regras praticas de secrets

- nunca commitar `.env`, `.env.local` ou qualquer variante real
- nunca reaproveitar placeholder do repo em demo/producao
- prefira gerar segredos longos e aleatorios por ambiente
- se um secret foi compartilhado em chat, screenshot ou log, trate como comprometido e rotacione

## Rotacao curta

### JWT secret

1. gere um novo valor longo e aleatorio
2. atualize o ambiente alvo
3. reinicie a aplicacao
4. considere todos os tokens antigos invalidados

### Senha do banco

1. altere a senha no banco
2. atualize o ambiente da aplicacao
3. reinicie os servicos dependentes
4. confirme conectividade e healthchecks

## O que a aplicacao valida hoje

- `JWT_SECRET_KEY` default inseguro falha sempre
- `JWT_SECRET_KEY` placeholder falha em `demo` e `production`
- `JWT_SECRET_KEY` com menos de 32 caracteres falha em `demo` e `production`
- `ACCESS_TOKEN_EXPIRE_MINUTES < 5` falha
- `POSTGRES_PASSWORD` placeholder/default falha em `production`
- `WEB_CONCURRENCY < 1` falha em `production`

## O que ainda continua fora do escopo

- secret manager real
- KMS ou vault
- rotacao automatizada
- segregacao por cloud/provedor
- CI/CD com injecao segura de envs
