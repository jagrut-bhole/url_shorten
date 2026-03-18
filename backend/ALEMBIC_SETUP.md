# Alembic Quick Guide (Simple)

This guide is for this backend project.
Alembic helps you save database schema changes in a safe, repeatable way.

## One-Time Setup

1. Open terminal in `backend` folder.
2. Activate virtual environment:

```bash
source .venv/Scripts/activate
```

3. Install packages:

```bash
python -m pip install -r requirements.txt
```

4. Make sure `.env` has `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/url_shortener
```

5. Initialize Alembic (only once for a new project):

```bash
python -m alembic init alembic
```

Note: In this project, `alembic/env.py` is already configured.

## Your Daily Workflow (Very Important)

Whenever you change models in `db/models.py`:

1. Create migration file:

```bash
python -m alembic revision --autogenerate -m "what_you_changed"
```

2. Apply migration to PostgreSQL:

```bash
python -m alembic upgrade head
```

That is all you need most of the time.

## Check Status

See current version:

```bash
python -m alembic current
```

See migration history:

```bash
python -m alembic history
```

## If Tables Already Exist

If tables were created earlier without Alembic:

1. Create baseline migration:

```bash
python -m alembic revision --autogenerate -m "baseline"
```

2. Mark DB as up-to-date (without running SQL again):

```bash
python -m alembic stamp head
```

## Common Errors (Simple Fix)

`DATABASE_URL is empty`
- Add `DATABASE_URL` in `.env`.

`Error loading ASGI app`
- Start backend using:

```bash
uvicorn main:app --reload
```

`NameError: sqlmodel is not defined` inside migration file
- Open latest file in `alembic/versions`.
- Add this import at top:

```python
import sqlmodel
```


# 1) Activate venv (inside backend)
source .venv/Scripts/activate

# 2) Create migration after model changes
python -m alembic revision --autogenerate -m "your_change_name"

# 3) Apply migration
python -m alembic upgrade head

# 4) Check current migration
python -m alembic current