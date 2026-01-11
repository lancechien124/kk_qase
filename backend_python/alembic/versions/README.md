# Alembic Migrations

This directory contains database migration scripts.

## Usage

### Create a new migration

```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

### View current revision

```bash
alembic current
```

## Migration Files

- `001_initial_migration.py` - Initial migration with all base tables

