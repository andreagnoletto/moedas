# CoinsDB

Sistema de catalogação de moedas físicas com contexto histórico, usando Django Admin como interface.

## Stack

- Python 3.13 / Django 6.0
- PostgreSQL 17
- Docker Compose
- uv (gerenciador de dependências)

## Estrutura

```
coinsdb/       → projeto Django (settings, urls, wsgi)
catalog/       → Country, CoinType
collection/    → CoinItem (moedas possuídas)
history/       → HistoricalContext, CoinTypeContext
data/csc/      → CSV de países (fonte: dr5hn/countries-states-cities-database)
```

## Setup rápido (Docker)

```bash
cp .env.example .env
docker compose up -d
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py import_countries
docker compose exec -e DJANGO_SUPERUSER_PASSWORD=admin web \
  uv run python manage.py createsuperuser --noinput --username admin --email admin@example.com
```

Acesse http://localhost:8000/admin/ com **admin / admin**.

## Setup local (sem Docker para o Django)

Requer PostgreSQL rodando na porta 5432.

```bash
docker compose up -d db          # sobe só o banco
cp .env.example .env
# ajuste DATABASE_URL no .env para localhost em vez de db
uv sync
uv run python manage.py migrate
uv run python manage.py import_countries
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Comandos úteis

```bash
docker compose up -d                # subir tudo
docker compose down                 # parar tudo
docker compose logs -f web          # logs do Django

# management commands (via Docker)
docker compose exec web uv run python manage.py makemigrations
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py import_countries
docker compose exec web uv run python manage.py check
```

## Variáveis de ambiente

| Variável | Exemplo | Descrição |
|---|---|---|
| `DATABASE_URL` | `postgres://coins:coins@db:5432/coinsdb` | Conexão com PostgreSQL |
| `DJANGO_SECRET_KEY` | `troque-esta-chave` | Secret key do Django |
| `DEBUG` | `True` | Modo debug |
