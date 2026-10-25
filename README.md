# BudgetWise — Django finance tracker

This update retains the original Budget Manager Django application and its database models, **not a new database schema**.
The original `main_app.PersonalBudget`, `ExpenseItem`, `Income` models and all seven historic migrations remain. Existing account/budget/expense/income data can be read from the same PostgreSQL database after validating the staged migration plan.

## Run locally with an isolated SQLite database

Requires Python 3.12+.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py test
python manage.py runserver
```

Create an account at `/signup/`. The dashboard is at `/dashboard/`; budgets, transactions and reports use the original data models. No sample financial records are inserted.

## Important about original data

- **Never point an untested deployment at the production database.** Back up the PostgreSQL database first and test against a restored copy.
- Original `Income` records have no date column, so income can be shown in overall totals but **not** honestly plotted as monthly income. The spending chart shows dated expenses only. Monthly income charts would require a future schema migration.
- Original budgets represent named groups of income and expenses. Budget bars therefore compare spending against recorded income, not against an invented per-category spending limit.
- The old ZIP contained a plaintext PostgreSQL credential and hardcoded Django secret. They have been removed from this source. **Rotate both secrets** and check Git history if the repository was ever public.
- Only remove/change old code after a tested replacement branch is approved. Preserve the old main branch and Render settings for rollback.

## Deploy safely to Render

Create a staging Web Service and **separate staging database** first. Set `DATABASE_URL` to the staging database, `DJANGO_SECRET_KEY` to a secure random key, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` for your hostname. Set `PYTHON_VERSION=3.12.8` if needed.

- Build: `./build.sh`
- Start: `gunicorn budgetmanager.wsgi:application --bind 0.0.0.0:$PORT`
- Run migrations separately against the staging database: `python manage.py migrate --noinput`
- Test signup, login/logout, budgets, income, expenses, reports, CSV, and user separation before production.

Do not overwrite the original live service or its database just by pushing these files.

## Design

BudgetWise uses forest green, sage and warm ivory with a restrained clay accent. The UI is Django templates and CSS, not a separate React application. The Python package remains named `budgetmanager` to preserve imports and deployment configuration.
