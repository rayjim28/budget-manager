# Install and deploy the redesigned original BudgetWise

This project is rebuilt from the uploaded `budget-manager-main.zip`. It preserves the original `main_app` models and migration history. **It is not a drop-in replacement for your live Render service until tested against a backup of its database.**

## 1. Test as a separate app on your Mac

```bash
cd ~/personal_projects
mkdir -p budget-manager-modern-test
unzip -o ~/Downloads/budget-manager-modern-integrated.zip -d budget-manager-modern-test
cd budget-manager-modern-test
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py check
python manage.py migrate
python manage.py test
python manage.py runserver
```

This test version uses **local SQLite**, not your production database. Sign up for a local test account. Visit `http://127.0.0.1:8000/` then test creating budgets, incomes and expenses, editing/removing, transaction search, reports, and CSV export.

## 2. Stage it in the existing Git repository

Do not delete your old `budget-manager` repository or its `.git` directory. Create a branch from its current `main` and save a backup tag:

```bash
cd ~/personal_projects/budget-manager
# Worktree must be clean; otherwise commit/stash your existing changes first.
git status --short
git switch main
git pull --ff-only
git tag backup/budget-manager-before-modern
git switch -c feature/budget-manager-modern

# Apply source changes from the verified test folder; preserve local env and database.
rsync -av --exclude='.git/' --exclude='.env' --exclude='.venv/' --exclude='*.sqlite3' --exclude='__pycache__/' --exclude='staticfiles/' ~/personal_projects/budget-manager-modern-test/ ./

git status --short
git add -A
git diff --cached --stat
git commit -m 'Modernize BudgetWise UI and secure budget workflows'
git push -u origin feature/budget-manager-modern
```

Create a PR into `main`, but **do not merge yet**.

## 3. Verify staging before production

1. In Render, create a separate staging Web Service that deploys `feature/budget-manager-modern`.
2. Use a **separate PostgreSQL staging database** (ideally a restored, scrubbed backup of the old one) and enter its `DATABASE_URL` as a Render environment variable.
3. Set `DJANGO_SECRET_KEY` to a new secure value, `DJANGO_DEBUG=false`, and `DJANGO_ALLOWED_HOSTS` to the staging hostname. Set `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-staging-host>` if needed.
4. Set `PYTHON_VERSION=3.12.8` if Render does not pick up `.python-version`.
5. Build command: `./build.sh`
6. Start command: `gunicorn budgetmanager.wsgi:application --bind 0.0.0.0:$PORT`
7. Run `python manage.py migrate --noinput` once on staging before serving requests. Don't do this against the production database without a verified backup.
8. Check old users and data, and run both automated and manual tests. Confirm historical expenses and income still appear.

## 4. Production cutover and rollback

Take and verify a PostgreSQL backup before changing Render. Configure `DATABASE_URL` explicitly in the production service — the modern settings use SQLite locally when `DATABASE_URL` is absent, which would otherwise make the deployed app look empty. Rotate the old leaked database password and hardcoded Django secret. Reconfigure the service before merging `feature/budget-manager-modern` into `main`, and verify the deployed website afterward.

To roll back, redeploy the saved Git revision with its matching environment configuration and original database. Code rollback alone does not reverse database migrations. **No files in this archive change your live Render service or PostgreSQL database.**
