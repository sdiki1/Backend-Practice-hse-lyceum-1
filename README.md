# backend

This project was created By sdiki1. 

This project was completed as an assignment based on the task provided in the [HW 11-1 HSE Lyceum Web 2025 ](https://github.com/FloydanTheBeast/hse-lyceum-web-2025/blob/main/homework/hw-11-1.md).

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m backend
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

## Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

This command exposes the web application on port 8000, mounts current directory and enables autoreload.

But you have to rebuild image every time you modify `poetry.lock` or `pyproject.toml` with this command:

```bash
docker-compose build
```

## Project structure

```bash
$ tree "backend"
backend
├── conftest.py  # Fixtures for all tests
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database
│   └── models  # Package contains different models for sqlAlchemy
├── __main__.py  # Startup script. Starts uvicorn
├── services  # Package for different external services such as redis (I use it for caching data in the project)
├── settings.py  # Main configuration settings for project
├── static  # Static content, such as swagger (Shadi, i dont want to write html for pages, sorry)
├── tests  # Tests for project (Using pytest)
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router
    ├── application.py  # FastAPI application configuration
    └── lifespan.py  # Contains actions to perform on startup and shutdown
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here. 

All environment variables should start with "BACKEND_" prefix.

For example if you see in your "backend/settings.py" a variable named like
`random_parameter`, you should provide the "BACKEND_RANDOM_PARAMETER" 
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `backend.settings.Settings.Config`.

An example of .env file:
```bash
BACKEND_RELOAD="True"
BACKEND_PORT="8000"
IS_SHADI_GENIUS="True"
BACKEND_ENVIRONMENT="dev"
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/
## OpenTelemetry 

If you want to start your project with OpenTelemetry collector 
you can add `-f ./deploy/docker-compose.otlp.yml` to your docker command.

Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.otlp.yml --project-directory . up
```

This command will start OpenTelemetry collector and jaeger. 
After sending a requests you can see traces in jaeger's UI
at http://localhost:16686/.

This docker configuration is not supposed to be used in production. 
It's only for demo purpose.

You can read more about OpenTelemetry here: https://opentelemetry.io/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```
This 3 word will make code that doesn't smell too much.

Pre-commit is very useful to check your code before publishing it, because personally my code can be a pile of shit with a lots of hacks and inventions.  
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code, but code could be like AI and warden like Shadi can set u bad mark);
* mypy (validates types, if u hasn't downloaded python3.5 and latest and dont know about their innovation); -- but for first commits i will deactivate all this module bcs im too lazy to make auth user before first commit
* ruff (spots possible bugs if u'r very stupid like me);

## Migrations

If you want to migrate your database, you should run following commands:
```bash
alembic upgrade "<revision_id>"
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
alembic downgrade <revision_id>
alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
alembic revision --autogenerate
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose run --build --rm api pytest -vv .
docker-compose down
```

For running tests on your local machine.
1. you need to start a database

I prefer doing it with docker:
```
docker run -p "5432:5432" -e "POSTGRES_PASSWORD=backend" -e "POSTGRES_USER=backend" -e "POSTGRES_DB=backend" postgres:16.3-bullseye
```


2. Run the pytest:
```bash
pytest -vv .
```
