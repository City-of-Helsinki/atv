# ATV
Asiointitietovaranto Django REST API

[![Pytest](https://github.com/City-of-Helsinki/atv/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/City-of-Helsinki/atv/actions/workflows/pytest.yml?query=branch:main)
[![Codestyle](https://github.com/City-of-Helsinki/atv/actions/workflows/py-coding-style.yml/badge.svg?branch=main)](https://github.com/City-of-Helsinki/atv/actions/workflows/py-coding-style.yml?query=branch:main)
[![codecov](https://codecov.io/gh/City-of-Helsinki/atv/branch/main/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/atv)


## Development with [Docker](https://docs.docker.com/)

Prerequisites:
* Docker
* Docker Compose

1. Create a `docker-compose.env.yaml` file in the project folder:
   * Use `docker-compose.env.yaml.example` as a base, it does not need any changes for getting the project running.
   * Set entrypoint/startup variables according to taste.
     * `DEBUG`, controls debug mode on/off
     * `APPLY_MIGRATIONS`, applies migrations on startup
     * `CREATE_ADMIN_USER`, creates an admin user with credentials `admin`:(password, see below)
     (admin@hel.ninja)
     * `ADMIN_USER_PASSWORD`, the admin user's password. If this is not given, a random password is generated
     and written into stdout when an admin user is created automatically.

2. Run `docker-compose up`
    * The project is now running at [localhost:8081](http://localhost:8081)

**Optional steps**

1. Run migrations:
    * Taken care by the example env
    * `docker exec atv-backend python manage.py migrate`

2. Create superuser:
    * Taken care by the example env
    * `docker exec -it atv-backend python manage.py add_admin_user`


## Development without Docker

Prerequisites:
* PostgreSQL 17
* Python 3.12


### Installing Python requirements

* Run `pip install -r requirements.txt`
* Run `pip install -r requirements-dev.txt` (development requirements)


### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S atv  # use password `atv`
    sudo -u postgres createdb -O atv atv

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER atv CREATEDB;"


### Daily running

* Create `.env` file: `touch .env`
```dotenv
DEBUG=1
DATABASE_URL=postgres://atv:atv@localhost:5437/atv

# Optionals (with a default value on settings.py)
FIELD_ENCRYPTION_KEYS=
```

* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py add_admin_user`
* Run `python manage.py runserver 0:8000`

The project is now running at [localhost:8000](http://localhost:8000)


## Keeping Python requirements up to date

1. Install `pip-tools`:
    * `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:
    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:
    * `pip-compile --upgrade requirements.in`

5. To install Python requirements run:
    * `pip-sync requirements.txt`


## Code format


This project uses [Ruff](https://docs.astral.sh/ruff/) for code formatting and quality checking.

Basic `ruff` commands:

* lint: `ruff check`
* apply safe lint fixes: `ruff check --fix`
* check formatting: `ruff format --check`
* format: `ruff format`

[`pre-commit`](https://pre-commit.com/) can be used to install and
run all the formatting tools as git hooks automatically before a
commit.


## Running tests

* Set the `DEBUG` environment variable to `1`.
* Run `pytest`.


## Git blame ignore refs

Project includes a `.git-blame-ignore-revs` file for ignoring certain commits from `git blame`.
This can be useful for ignoring e.g. formatting commits, so that it is more clear from `git blame`
where the actual code change came from. Configure your git to use it for this project with the
following command:

```shell
git config blame.ignoreRevsFile .git-blame-ignore-revs
```
