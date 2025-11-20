BotecoPro metamodel - DRAFT
================================

Location: /mnt/data/botecopro-db-meta

Structure:
- db-meta/schemas/001_domain.yaml: single YAML domain definition (entities, types, enums)
- templates/: Jinja2 templates for SQLAlchemy models and SQLite DDL
- generator.py: generator that renders the templates for each entity

How to use:
1. Install dependencies: `pip install -r requirements.txt`
2. Run the generator: `python generator.py`
3. Check `generated/` for the auto-created SQLAlchemy models (under `generated/python`) and SQLite DDL (under `generated/sql`).
