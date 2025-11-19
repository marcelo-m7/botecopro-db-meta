# BotecoPro Metamodel — Canonical Domain Source

This repository contains the canonical metamodel for BotecoPro. The metamodel is intended to be a single source of truth (a single YAML description of the domain) that can be used to generate runtime artifacts and documentation for multiple targets.

What this metamodel can be converted into (examples):

- SQL DDL (Postgres CREATE TABLE, constraints, indexes)
- Python classes (SQLAlchemy models, Pydantic schemas)
- Dart models (Freezed / json_serializable friendly)
- GraphQL schema
- OpenAPI specifications
- Human-readable documentation

This metamodel can be extended to support higher-level architectural patterns or distribution models:

- Event Sourcing & CQRS scaffolding
- Additional schema families (tenants, org-scoped schemas)
- Micro-front / microservice API boundaries

**Status:** Draft — useful as a starting point and roadmap for an automated generator.

**Quick usage (conceptual)**

- Edit the domain YAML files under `db-meta/` (or `PLAN/001_domain.yaml`).
- Run a generator (not included in this README yet) that reads the YAML and emits artifacts into a `generated/` directory.

Example (once a generator exists):

```powershell
python generator.py --input db-meta/001_domain.yaml --out generated
```

**Goals & next steps**

1. Provide a small, stable YAML metamodel that describes entities, fields, types, enums, references, indexes and targets.
2. Build a minimal Python generator that:
	- validates the YAML,
	- emits SQL files per schema,
	- emits Python models (SQLAlchemy + Pydantic),
	- emits Dart model files.
3. Add basic tests and linters to ensure generated artifacts meet formatting and typing expectations.
4. Iterate on richer features (enum generation, JSON columns, relationships, permissions/roles mapping, multi-schema support).

**How to contribute**

- Propose changes to the YAML metamodel by opening issues or PRs with example YAML snippets.
- If you want a generator feature (Dart, Python or SQL pattern), open an issue describing the expected input and example output.

**Contact / ownership**

This repository and metamodel are intended for the BotecoPro ecosystem. Use issues or PRs to discuss changes and improvements.

---

If you'd like, I can now:

- add a minimal Python generator scaffold and update this README with concrete run instructions, or
- produce example generated outputs for one entity (e.g., `orders`) so you can review the generation format.