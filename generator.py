from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from yaml import YAMLError

BASE = Path(__file__).parent
TEMPLATE_DIR = BASE / "templates"


@dataclass
class EnumDef:
    name: str
    values: List[str]


@dataclass
class Attribute:
    name: str
    type_name: str
    base_type: str
    py_type_hint: str
    sa_type: str
    sql_type: str
    nullable: bool
    primary_key: bool
    autoincrement: bool
    default: Optional[Any]
    default_sql: Optional[str]
    column_args: str
    sql_line: str
    foreign_key: Optional[str]
    enum: Optional[str] = None
    enum_values: Optional[List[str]] = None


@dataclass
class Entity:
    name: str
    table: str
    attributes: List[Attribute]
    indexes: List[Dict[str, Any]]
    foreign_keys: List[str]
    composite_primary_keys: List[str]


class DomainLoader:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Dict[str, Any]:
        try:
            with self.path.open("r") as fh:
                content = yaml.safe_load(fh)
        except YAMLError as exc:
            raise RuntimeError(f"Failed to parse YAML file {self.path}: {exc}") from exc

        if not content or "botecopro_domain" not in content:
            raise RuntimeError(f"No botecopro_domain entry found in {self.path}")

        domain = content["botecopro_domain"]
        for section in ("entities", "enums", "types"):
            domain.setdefault(section, {})
        return domain


def resolve_base_type(type_name: str, types: Dict[str, Any]) -> str:
    if type_name in {"enum", "relation"}:
        return type_name
    custom = types.get(type_name)
    if isinstance(custom, dict) and "base" in custom:
        return str(custom["base"])
    return type_name


def python_type_for(base_type: str, enum: Optional[str] = None) -> str:
    mapping = {
        "int": "int",
        "integer": "int",
        "float": "float",
        "decimal": "Decimal",
        "bool": "bool",
        "boolean": "bool",
        "string": "str",
        "text": "str",
        "uuid": "uuid.UUID",
        "timestamp": "datetime",
    }
    if enum:
        return enum
    return mapping.get(base_type, "str")


def sqlalchemy_type_for(base_type: str, attr: Dict[str, Any], enum: Optional[str] = None) -> str:
    if enum:
        return f"SAEnum({enum})"

    if base_type in {"int", "integer"}:
        return "Integer"
    if base_type == "float":
        return "Float"
    if base_type in {"bool", "boolean"}:
        return "Boolean"
    if base_type in {"string", "text"}:
        return "String"
    if base_type == "uuid":
        return "String"
    if base_type == "timestamp":
        return "DateTime"
    if base_type == "decimal":
        precision = attr.get("precision", 10)
        scale = attr.get("scale", 2)
        return f"Numeric({precision}, {scale})"
    return "String"


def sqlite_type_for(base_type: str, attr: Dict[str, Any], enum_values: Optional[List[str]] = None) -> str:
    if base_type in {"int", "integer"}:
        return "INTEGER"
    if base_type == "float":
        return "REAL"
    if base_type in {"bool", "boolean"}:
        return "BOOLEAN"
    if base_type in {"string", "text"}:
        return "TEXT"
    if base_type == "uuid":
        return "TEXT"
    if base_type == "timestamp":
        return "DATETIME"
    if base_type == "decimal":
        precision = attr.get("precision", 10)
        scale = attr.get("scale", 2)
        return f"NUMERIC({precision},{scale})"
    if enum_values is not None:
        return "TEXT"
    return "TEXT"


def format_python_default(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return repr(value)
    return repr(value)


def format_sql_default(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return f"'{value}'"


def make_column_args(attr: Dict[str, Any], sa_type: str, foreign_key: Optional[str]) -> str:
    args: List[str] = [sa_type]
    if foreign_key:
        args.append(f"ForeignKey('{foreign_key}')")

    kwargs: List[str] = []
    if attr.get("primary_key"):
        kwargs.append("primary_key=True")
    if attr.get("autoincrement"):
        kwargs.append("autoincrement=True")
    if attr.get("nullable") is False:
        kwargs.append("nullable=False")
    default_repr = format_python_default(attr.get("default"))
    if default_repr is not None:
        kwargs.append(f"default={default_repr}")

    return ", ".join(args + kwargs)


def make_sql_line(
    name: str,
    sql_type: str,
    attr: Dict[str, Any],
    enum_values: Optional[List[str]],
    composite_primary: bool,
) -> str:
    primary = attr.get("primary_key", False)
    autoinc = attr.get("autoincrement", False)

    if (
        primary
        and autoinc
        and sql_type == "INTEGER"
        and not composite_primary
    ):
        return f"{name} INTEGER PRIMARY KEY AUTOINCREMENT"

    parts = [name, sql_type]
    if primary and not composite_primary:
        parts.append("PRIMARY KEY")
    if attr.get("nullable") is False:
        parts.append("NOT NULL")
    default_sql = format_sql_default(attr.get("default"))
    if default_sql:
        parts.append(f"DEFAULT {default_sql}")
    if enum_values:
        allowed = ", ".join(f"'{val}'" for val in enum_values)
        parts.append(f"CHECK ({name} IN ({allowed}))")
    return " ".join(parts)


def resolve_entities(domain: Dict[str, Any]) -> List[Entity]:
    enums = domain.get("enums", {})
    types = domain.get("types", {})
    entities_data = domain.get("entities", {})

    entities: List[Entity] = []
    for entity_name, data in entities_data.items():
        storage = data.get("storage", {}) or {}
        table = storage.get("table", entity_name.lower())
        raw_attrs = data.get("attributes", {}) or {}
        indexes = data.get("indexes", []) or []

        composite_primary_keys = [name for name, attr in raw_attrs.items() if attr.get("primary_key")]
        composite_primary = len(composite_primary_keys) > 1
        attrs: List[Attribute] = []
        foreign_keys: List[str] = []

        for attr_name, attr in raw_attrs.items():
            attr_type = attr.get("type")
            enum_name = attr.get("enum") if attr_type == "enum" else None
            enum_values = enums.get(enum_name, []) if enum_name else None

            if attr_type == "relation":
                target = attr.get("target")
                target_field = attr.get("target_field", "id")
                target_entity = entities_data.get(target, {})
                target_storage = target_entity.get("storage", {}) or {}
                target_table = target_storage.get("table", (target or "").lower())
                fk = f"{target_table}.{target_field}"
                target_attrs = target_entity.get("attributes", {})
                target_attr = target_attrs.get(target_field, {})
                base_type = resolve_base_type(target_attr.get("type", "string"), types)
            else:
                fk = None
                base_type = resolve_base_type(attr_type, types)

            sa_type = sqlalchemy_type_for(base_type, attr, enum_name)
            sql_type = sqlite_type_for(base_type, attr, enum_values)
            py_type = python_type_for(base_type, enum_name)

            nullable = attr.get("nullable")
            if nullable is None:
                nullable = not attr.get("required", False)

            py_type_hint = py_type
            if nullable:
                py_type_hint = f"Optional[{py_type}]"

            column_args = make_column_args(attr, sa_type, fk)
            sql_line = make_sql_line(attr_name, sql_type, attr, enum_values, composite_primary)

            if fk:
                foreign_keys.append(fk)

            attrs.append(
                Attribute(
                    name=attr_name,
                    type_name=attr_type,
                    base_type=base_type,
                    py_type_hint=py_type_hint,
                    sa_type=sa_type,
                    sql_type=sql_type,
                    nullable=bool(nullable),
                    primary_key=bool(attr.get("primary_key", False)),
                    autoincrement=bool(attr.get("autoincrement", False)),
                    default=attr.get("default"),
                    default_sql=format_sql_default(attr.get("default")),
                    column_args=column_args,
                    sql_line=sql_line,
                    foreign_key=fk,
                    enum=enum_name,
                    enum_values=enum_values,
                )
            )

        entities.append(
            Entity(
                name=entity_name,
                table=table,
                attributes=attrs,
                indexes=indexes,
                foreign_keys=foreign_keys,
                composite_primary_keys=composite_primary_keys,
            )
        )

    return entities


def render_template(name: str, ctx: Dict[str, Any]) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    try:
        template = env.get_template(name)
    except TemplateNotFound as exc:
        raise RuntimeError(f"Template '{name}' not found in templates directory") from exc
    return template.render(ctx)


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        fh.write(content)


def main() -> None:
    domain_path = BASE / "db-meta" / "schemas" / "001_domain.yaml"
    loader = DomainLoader(domain_path)
    domain = loader.load()

    enums = [EnumDef(name=k, values=v) for k, v in (domain.get("enums", {}) or {}).items()]
    entities = resolve_entities(domain)

    out_dir = BASE / "generated"
    python_out = out_dir / "python"
    sql_out = out_dir / "sql"

    for entity in entities:
        used_enums = [enum for enum in enums if any(attr.enum == enum.name for attr in entity.attributes)]
        ctx = {
            "entity": entity,
            "enums": used_enums,
        }

        python_rendered = render_template("python_sqlalchemy.j2", ctx)
        write_output(python_out / f"{entity.name.lower()}_model.py", python_rendered)

        sql_rendered = render_template("sqlite_table.j2", ctx)
        write_output(sql_out / f"{entity.name.lower()}_table.sql", sql_rendered)

    print(f"Generated {len(entities)} models")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
