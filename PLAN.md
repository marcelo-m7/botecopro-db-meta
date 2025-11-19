# BotecoPro Domain Code Generator Specification

This document defines the requirements for extending and completing the **Python → SQLite** code generator for the BotecoPro project.  The base repository already includes a set of YAML schema files under `db/schemas` that describe the domain tables.  CodeMachine must use these existing files as the single source of truth and generate:

* **Python models** using **SQLAlchemy** or **SQLModel**, targeting SQLite as the only database.
* **SQLite DDL** (`CREATE TABLE`, constraints and indexes) ready for migration or manual execution.

There is **only one organisation** and no need to handle multiple schemas.  Focus on finishing the generator and correcting any existing issues in the base project while adhering to standard Python packaging practices.  Optionally, Dart generation may come later, but this milestone is strictly Python and SQL.

## 1. Input: YAML schemas in `db/schemas`

The generator must consume the YAML files already present in the repository under **`db/schemas`**.  Each file describes a single entity (table) and follows the pattern used in the existing meta‑repository: a root object with an `entity` name, an optional `schema` (ignored because we have only one SQLite database), and an `attributes` map describing fields.  Attributes can include:

| Key              | Purpose                                        | Example                                |
|------------------|------------------------------------------------|----------------------------------------|
| `type`           | logical type (`int`, `float`, `bool`, `string`, `uuid`, `enum`, `decimal`, etc.) | `type: int` |
| `primary_key`    | whether this field is part of the primary key  | `primary_key: true` |
| `autoincrement`  | integer PK auto increments (SQLite)            | `autoincrement: true` |
| `nullable`       | whether the column can be null                 | `nullable: false` |
| `default`        | default value as a Python/SQL literal          | `default: 0` or `default: now()` |
| `enum`           | enum name if `type: enum`                      | `enum: OrderStatus` |
| `relation`       | foreign key reference                          | `relation: {target: Order, target_field: id}` |
| `precision`/`scale` | for decimal types                            | `precision: 10, scale: 2` |

Composite primary keys are supported via multiple fields marked with `primary_key: true`.  Foreign keys must be emitted as `ForeignKey` constraints in Python and as `FOREIGN KEY` clauses in SQL.  If the repository defines enumerations in a separate file (e.g. `enums.yaml`), they should be loaded and used for generating Python `Enum` classes and SQLite `CHECK` constraints.

## 2. Output: Python models

The generator must emit Python classes using SQLAlchemy’s declarative API that map directly onto the YAML entities.  Key points:

1. Use a single `Base = declarative_base()` imported from `sqlalchemy.orm` (or `SQLModel`’s declarative base if using SQLModel).  Each entity is a subclass of `Base` with a `__tablename__` matching the YAML file’s entity name or `storage.table`.
2. Columns are declared via `Column` with the appropriate SQLAlchemy types (`Integer`, `Float`, `Boolean`, `String`, `Text`, `DateTime`, `UUID`, etc.).  Use `nullable` and `default` as defined in the YAML.  For UUIDs, rely on Python’s `uuid.uuid4()` for default generation.
3. Integer primary keys with `autoincrement: true` should include `autoincrement=True`.  If multiple fields are primary keys, mark all with `primary_key=True`.
4. For foreign keys, declare the column as the same type as the target’s primary key and pass a `ForeignKey` pointing to `"<target_table>.<target_field>"`.  Relationships may be added via `relationship()` but are optional in this milestone.
5. Enumerations should be defined as Python `Enum` classes in a separate module and referenced via SQLAlchemy’s `Enum` type when generating columns.
6. Provide type hints using the Python `typing` module (`Optional[int]`, `UUID`, etc.) and annotate dataclass fields accordingly; integration with Pydantic is optional but recommended for later.
7. Generate one Python file per entity under `generated/python/` (e.g. `order.py`) and an `__init__.py` that imports all classes for convenience.
8. Include docstrings summarising each class and its fields.

For guidance, refer to the example model in `PLAN.md`【886825656178662†L143-L176】.  Adapt it for SQLite by using `Integer` instead of `UUID` where applicable and by not using Postgres‑specific types.  When using **SQLModel**, the classes should inherit from `SQLModel` instead of `Base`, and fields should be declared as class attributes with type annotations and `Field` metadata.

## 3. Output: SQLite DDL

For each entity generate a `.sql` file under `generated/sql/` containing:

* A `CREATE TABLE IF NOT EXISTS` statement with the correct column definitions.
* Primary key definitions.  For single integer PKs with auto‑increment, use `INTEGER PRIMARY KEY AUTOINCREMENT`; for other PKs use `PRIMARY KEY` constraint listing the columns.
* `NOT NULL` constraints and `DEFAULT` clauses as defined in the YAML.
* `FOREIGN KEY` constraints referencing the correct table and column.  Ensure that referenced tables are created before the referencing table or add `PRAGMA foreign_keys=ON;` at the top of the migration.
* Index definitions when an entity declares an `indexes` array.  Use `CREATE INDEX IF NOT EXISTS` and follow the naming convention `idx_<table>_<column>`.  Example: for `idx_orders_table_status` in the plan【886825656178662†L219-L223】.

SQLite type mapping should follow:

| YAML type | SQLite type |
|-----------|-------------|
| `int`     | `INTEGER` |
| `float`   | `REAL`    |
| `bool`    | `BOOLEAN` |
| `string`  | `TEXT`    |
| `decimal` | `NUMERIC(precision,scale)` |
| `uuid`    | `TEXT` (store UUID as text) |
| `timestamp` | `DATETIME` |

If custom scalar types are defined in the YAML (e.g. a `money_cents` type stored as an integer), map them to an appropriate SQLite base type (`INTEGER` for money in cents).

## 4. Project structure and tooling

To ensure maintainability and adherence to Python best practices, organise the repository as follows:

```
botecopro_db_meta/
├── pyproject.toml        # use PEP 621; define package name, version and dependencies
├── README.md             # overview and usage instructions
├── src/
│   └── botecopro_meta/
│       ├── __init__.py
│       ├── generator.py  # module exposing a `generate` function
│       └── templates/
│           ├── python_model.j2
│           └── sqlite_table.j2
├── domain.yaml           # the single canonical YAML file
├── generated/            # output directory created by the generator
│   ├── python/
│   └── sql/
└── tests/
    ├── test_generator.py
    └── fixtures/
```

* Use **pyproject.toml** with a `[project]` section to declare metadata and `[tool.poetry]` if Poetry is preferred.  Declare dependencies: `PyYAML`, `Jinja2`, `SQLAlchemy` (version 2.x), and `pytest` for tests.  A development dependency on `black` and `flake8` is recommended.
* Implement the generator as a Python package in `src/botecopro_meta/`.  Expose a `generate(domain_path: Path, output_dir: Path) -> None` function which reads the YAML, loads types/enums/entities, and renders Jinja2 templates into the output directory.
* Provide CLI entry points via `[project.scripts]` in `pyproject.toml` (e.g. `boteco-generate = botecopro_meta.generator:main`) so that running `boteco-generate --input domain.yaml --out generated/` performs the generation.
* Store Jinja2 templates under `src/botecopro_meta/templates/`.  Use descriptive names (`python_model.j2`, `sqlite_table.j2`).  Review the existing `python_sqlmodel.j2` template in the meta‑repository【70030431756859†L1-L11】 and adjust it for SQLAlchemy, type hints, and enum support.
* Write tests in `tests/`.  At minimum, load a sample YAML (e.g. the provided domain), run the generator into a temporary directory, and assert that the produced Python classes and SQL files compile/import correctly.  Tests should use the built‑in `sqlite3` module to execute the generated SQL and verify that tables and columns exist with the expected schema.

## 5. Development guidelines

* Follow **PEP 8** and **PEP 257** for code style and docstrings.  Configure `flake8` to run in CI.  Format code with `black`.
* Use **type hints** everywhere; consider using `typing_extensions` for `TypedDict` if helpful for YAML parsing.
* Write modular functions: separate YAML parsing (`load_domain`), model generation (`render_python_models`), SQL generation (`render_sql_ddl`), and file writing.  Avoid monolithic scripts.
* Document your public API in the README: installation, usage, command‑line options, and how to extend the templates.
* Ensure that the generator is idempotent: running it multiple times should overwrite previous output without errors.
* Keep the YAML schemas free of environment‑specific details.  Because this project targets a single organisation and a single SQLite database, there is no need to prefix table names with schema names or handle per‑tenant namespaces.  If future work adds multi‑tenant support, that logic should live in the generator (e.g. prefixing tables with tenant identifiers).

## 6. Future extensions

Although this milestone targets Python and SQLite, design the generator with extension points so that additional targets can be added later.  For example:

* A **Dart** generator can reuse the same YAML and produce Freezed/Pydantic classes; the plan in `PLAN.md` outlines the mappings【886825656178662†L318-L336】.
* A **PostgreSQL** generator may support multi‑schema generation (e.g. `org_{slug}` schemas) and `UUID` types.  Use separate Jinja templates for Postgres.
* Additional model attributes (e.g. `updated_at` triggers, check constraints) can be described in the YAML and implemented in templates.

---

This specification is based on the draft and examples provided in the existing meta‑repository.  In particular, the high‑level YAML structure and example tables in `PLAN.md`【886825656178662†L112-L178】 illustrate how entities should be defined, and the meta‑repository README explains the directory structure (`db-meta/schemas`, `relations.yaml`, `templates/`, `generator.py`)【875632390543743†L5-L11】.  Use these references to inform your implementation while adapting them for SQLite and modern Python practices.