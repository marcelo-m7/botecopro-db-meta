"""Generate Python models and SQLite DDL from BotecoPro domain YAML."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import sys

sys.path.insert(0, "/usr/lib/python3/dist-packages")

import yaml

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:  # pragma: no cover - fallback renderer handles templates
    Environment = None
    FileSystemLoader = None
    select_autoescape = None

BASE_TYPES = {
    "int": {"python": "int", "sqlalchemy": "Integer", "sqlite": "INTEGER"},
    "float": {"python": "float", "sqlalchemy": "Float", "sqlite": "REAL"},
    "bool": {"python": "bool", "sqlalchemy": "Boolean", "sqlite": "BOOLEAN"},
    "string": {"python": "str", "sqlalchemy": "String", "sqlite": "TEXT"},
    "text": {"python": "str", "sqlalchemy": "Text", "sqlite": "TEXT"},
    "uuid": {"python": "UUID", "sqlalchemy": "String", "sqlite": "TEXT"},
    "datetime": {
        "python": "datetime",
        "sqlalchemy": "DateTime",
        "sqlite": "DATETIME",
    },
    "timestamp": {
        "python": "datetime",
        "sqlalchemy": "DateTime",
        "sqlite": "DATETIME",
    },
    "decimal": {
        "python": "Decimal",
        "sqlalchemy": "Numeric",
        "sqlite": "NUMERIC",
    },
}


@dataclass
class EnumDefinition:
    """Represents an enumeration defined in the domain."""

    name: str
    values: List[str]


@dataclass
class AttributeDefinition:
    """Resolved attribute including type metadata for templates."""

    name: str
    raw: Dict
    base_type: str
    python_type: str
    sqlalchemy_type: str
    sqlite_type: str
    nullable: bool = True
    primary_key: bool = False
    autoincrement: bool = False
    default: Optional[str] = None
    enum: Optional[str] = None
    enum_values: Optional[List[str]] = None
    relation: Optional[Tuple[str, str]] = None  # (table, field)
    precision: Optional[int] = None
    scale: Optional[int] = None


@dataclass
class EntityDefinition:
    """Entity and its attributes after resolution."""

    name: str
    table: str
    attributes: List[AttributeDefinition]
    indexes: List[Dict] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)


@dataclass
class DomainDefinition:
    """Full domain definition including enums and entities."""

    name: str
    enums: Dict[str, EnumDefinition]
    entities: List[EntityDefinition]
    custom_types: Dict[str, Dict]


class DomainLoader:
    """Load domain YAML into rich definitions."""

    def __init__(self, domain_path: Path):
        self.domain_path = domain_path

    def load(self) -> DomainDefinition:
        data = yaml.safe_load(self.domain_path.read_text())
        if len(data) == 1 and "entities" not in next(iter(data.values())):
            domain_name, domain_data = next(iter(data.items()))
        elif len(data) == 1:
            domain_name, domain_data = next(iter(data.items()))
        else:
            domain_name, domain_data = "domain", data

        enums = {
            name: EnumDefinition(name=name, values=values)
            for name, values in domain_data.get("enums", {}).items()
        }
        custom_types = domain_data.get("types", {})

        raw_entities = domain_data.get("entities", {})
        entity_defs: Dict[str, Dict] = {
            name: details for name, details in raw_entities.items()
        }

        entities = [
            self._build_entity(name, details, entity_defs, custom_types, enums)
            for name, details in raw_entities.items()
        ]

        return DomainDefinition(
            name=domain_name, enums=enums, entities=entities, custom_types=custom_types
        )

    def _resolve_base_type(self, attr: Dict, custom_types: Dict) -> str:
        attr_type = attr.get("type", "string")
        if attr_type == "enum":
            return "string"
        if attr_type == "relation":
            target_attr = custom_types.get("int", {})  # fallback handled later
            base = target_attr.get("base", "int") if isinstance(target_attr, dict) else "int"
            return base
        if attr_type in custom_types:
            custom = custom_types[attr_type]
            if isinstance(custom, dict) and "base" in custom:
                return custom["base"]
        return attr_type

    def _attribute_from_relation(
        self,
        name: str,
        attr: Dict,
        entities: Dict[str, Dict],
        custom_types: Dict,
        enums: Dict[str, EnumDefinition],
    ) -> AttributeDefinition:
        target = attr.get("target")
        target_field = attr.get("target_field", "id")
        target_entity = entities.get(target, {})
        target_attr = target_entity.get("attributes", {}).get(target_field, {"type": "int"})
        resolved_base = self._resolve_base_type(target_attr, custom_types)
        resolved = self._build_attribute(
            name,
            {
                "type": resolved_base,
                "nullable": attr.get("nullable", False),
                "primary_key": attr.get("primary_key", False),
            },
            custom_types,
            enums,
        )
        resolved.relation = (
            target_entity.get("storage", {}).get("table", target),
            target_field,
        )
        return resolved

    def _build_attribute(
        self,
        name: str,
        attr: Dict,
        custom_types: Dict,
        enums: Dict[str, EnumDefinition],
    ) -> AttributeDefinition:
        base_type = self._resolve_base_type(attr, custom_types)
        default_val = attr.get("default")
        primary_key = bool(attr.get("primary_key"))
        required = attr.get("required", False)
        nullable_flag = attr.get("nullable", not required)
        nullable = nullable_flag is not False and not primary_key
        autoincrement = bool(attr.get("autoincrement"))
        precision = attr.get("precision")
        scale = attr.get("scale")

        python_type = self._python_type(base_type)
        sqlalchemy_type = self._sqlalchemy_type(base_type, precision, scale)
        sqlite_type = self._sqlite_type(base_type, precision, scale)

        enum_name = attr.get("enum") if attr.get("type") == "enum" else None
        enum_values = enums.get(enum_name).values if enum_name in enums else None

        return AttributeDefinition(
            name=name,
            raw=attr,
            base_type=base_type,
            python_type=python_type,
            sqlalchemy_type=sqlalchemy_type,
            sqlite_type=sqlite_type,
            nullable=nullable,
            default=self._python_default(default_val),
            primary_key=primary_key,
            autoincrement=autoincrement,
            enum=enum_name,
            enum_values=enum_values,
            precision=precision,
            scale=scale,
        )

    def _build_entity(
        self,
        name: str,
        details: Dict,
        entities: Dict[str, Dict],
        custom_types: Dict,
        enums: Dict[str, EnumDefinition],
    ) -> EntityDefinition:
        table = details.get("storage", {}).get("table", name.lower())
        attrs = []
        for attr_name, attr in details.get("attributes", {}).items():
            if attr.get("type") == "relation":
                attrs.append(
                    self._attribute_from_relation(
                        attr_name, attr, entities, custom_types, enums
                    )
                )
            else:
                attrs.append(self._build_attribute(attr_name, attr, custom_types, enums))
        return EntityDefinition(
            name=name,
            table=table,
            attributes=attrs,
            indexes=details.get("indexes", []),
            methods=details.get("methods", []),
        )

    def _python_type(self, base_type: str) -> str:
        if base_type in BASE_TYPES:
            return BASE_TYPES[base_type]["python"]
        return "str"

    def _sqlalchemy_type(self, base_type: str, precision: Optional[int], scale: Optional[int]) -> str:
        if base_type == "decimal":
            p = precision or 12
            s = scale or 2
            return f"Numeric(precision={p}, scale={s})"
        return BASE_TYPES.get(base_type, BASE_TYPES["string"])["sqlalchemy"]

    def _sqlite_type(self, base_type: str, precision: Optional[int], scale: Optional[int]) -> str:
        if base_type == "decimal":
            p = precision or 12
            s = scale or 2
            return f"NUMERIC({p},{s})"
        return BASE_TYPES.get(base_type, BASE_TYPES["string"])["sqlite"]

    def _python_default(self, default: Optional[object]) -> Optional[str]:
        if default is None:
            return None
        return repr(default)


def _python_type_hint(attr: AttributeDefinition) -> str:
    return f"Optional[{attr.python_type}]" if attr.nullable else attr.python_type


def render_python_model_content(entity: EntityDefinition) -> str:
    lines = [
        f'"""SQLAlchemy model for {entity.name}."""',
        "from __future__ import annotations",
        "",
        "from typing import Optional",
        "from datetime import datetime",
        "from decimal import Decimal",
        "from uuid import UUID",
        "",
        "from sqlalchemy import (",
        "    Boolean,",
        "    Column,",
        "    DateTime,",
        "    Float,",
        "    ForeignKey,",
        "    Integer,",
        "    Numeric,",
        "    String,",
        "    Text,",
        "    Enum as SAEnum,",
        ")",
        "",
        "from .base import Base",
        "from . import enums",
        "",
        f"class {entity.name}(Base):",
        f"    \"\"\"{entity.name} table mapped to {entity.table}.\"\"\"",
        "",
        f"    __tablename__ = \"{entity.table}\"",
        "",
    ]

    for attr in entity.attributes:
        column_type = (
            f"SAEnum(enums.{attr.enum})" if attr.enum else attr.sqlalchemy_type
        )
        column_parts = [column_type]
        if attr.relation:
            column_parts.append(f'ForeignKey("{attr.relation[0]}.{attr.relation[1]}")')
        if attr.primary_key:
            column_parts.append("primary_key=True")
        if attr.autoincrement:
            column_parts.append("autoincrement=True")
        if not attr.nullable:
            column_parts.append("nullable=False")
        if attr.default is not None:
            column_parts.append(f"default={attr.default}")
        column_args = ", ".join(column_parts)
        lines.append(
            f"    {attr.name}: {_python_type_hint(attr)} = Column(\n        {column_args}\n    )"
        )
        lines.append("")

    if entity.methods:
        for method in entity.methods:
            lines.append(f"    def {method}(self) -> None:")
            lines.append("        \"\"\"Domain operation stub.\"\"\"")
            lines.append("        raise NotImplementedError")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_enums_content(enums: Dict[str, EnumDefinition]) -> str:
    lines = [
        '"""Auto-generated enumerations for the BotecoPro domain."""',
        "from __future__ import annotations",
        "",
        "from enum import Enum",
        "",
    ]
    for enum in enums.values():
        lines.append(f"class {enum.name}(str, Enum):")
        for value in enum.values:
            lines.append(f"    {value.upper().replace('-', '_')} = \"{value}\"")
        lines.append("")
        lines.append("")
    lines.append("__all__ = [")
    for enum in enums.values():
        lines.append(f'    "{enum.name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def render_base_content() -> str:
    return (
        '"""SQLAlchemy declarative base for generated models."""\n'
        "from __future__ import annotations\n\n"
        "from sqlalchemy.orm import declarative_base\n\n"
        "Base = declarative_base()\n"
    )


def render_init_content(entities: List[EntityDefinition]) -> str:
    lines = [
        '"""Auto-generated package containing SQLAlchemy models."""',
        "from __future__ import annotations",
        "",
        "from .base import Base",
        "from . import enums",
    ]
    for entity in entities:
        lines.append(f"from .{entity.table} import {entity.name}")
    lines.append("")
    lines.append("__all__ = [")
    lines.append('    "Base",')
    lines.append('    "enums",')
    for entity in entities:
        lines.append(f'    "{entity.name}",')
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def render_sql_content(entity: EntityDefinition) -> str:
    pk_columns = [attr.name for attr in entity.attributes if attr.primary_key]
    quoted_table = f'"{entity.table}"'
    lines = [
        f"-- Auto-generated SQLite DDL for {entity.table}",
        f"CREATE TABLE IF NOT EXISTS {quoted_table} (",
    ]
    column_defs: List[str] = []
    for attr in entity.attributes:
        col_name = f'"{attr.name}"'
        col = f"{col_name} {attr.sqlite_type}"
        if attr.enum_values:
            allowed = ", ".join([f"'{v}'" for v in attr.enum_values])
            col += f" CHECK ({col_name} IN ({allowed}))"
        if attr.primary_key and attr.autoincrement and len(pk_columns) == 1:
            col = f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT"
        elif attr.primary_key:
            col += " NOT NULL"
        if not attr.primary_key and not attr.nullable:
            col += " NOT NULL"
        if attr.raw.get("default") is not None:
            default_val = attr.raw.get("default")
            if isinstance(default_val, str):
                default_literal = f"'{default_val}'"
            elif isinstance(default_val, bool):
                default_literal = "1" if default_val else "0"
            else:
                default_literal = str(default_val)
            col += f" DEFAULT {default_literal}"
        column_defs.append(col)

    lines.append("  " + ",\n  ".join(column_defs))
    if len(pk_columns) > 1:
        quoted_pk = ", ".join([f'"{name}"' for name in pk_columns])
        lines.append(f"  ,PRIMARY KEY({quoted_pk})")

    fk_attrs = [attr for attr in entity.attributes if attr.relation]
    if fk_attrs:
        for fk in fk_attrs:
            lines.append(
                f"  ,FOREIGN KEY (\"{fk.name}\") REFERENCES \"{fk.relation[0]}\"(\"{fk.relation[1]}\")"
            )
    lines.append(");")

    index_counts: Dict[str, int] = {}
    for idx in entity.indexes:
        unique = "UNIQUE " if idx.get("unique") else ""
        cols = ",".join([f'"{c}"' for c in idx["columns"]])
        base_name = f"idx_{entity.table}_{'_'.join(idx['columns'])}"
        count = index_counts.get(base_name, 0)
        index_name = base_name if count == 0 else f"{base_name}_{count + 1}"
        index_counts[base_name] = count + 1
        lines.append(
            f"CREATE {unique}INDEX IF NOT EXISTS {index_name} ON {quoted_table} ({cols});"
        )

    return "\n".join(lines) + "\n"


class Generator:
    """Render Python models and SQLite DDL using templates."""

    def __init__(self, templates_path: Path):
        if Environment is not None:
            self.env = Environment(
                loader=FileSystemLoader(str(templates_path)),
                autoescape=select_autoescape(disabled_extensions=(".j2",)),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            self.env = None

    def render_python(self, entity: EntityDefinition, enums: Dict[str, EnumDefinition]) -> str:
        if self.env:
            template = self.env.get_template("python_model.j2")
            return template.render(entity=entity, enums=enums)
        return render_python_model_content(entity)

    def render_sql(self, entity: EntityDefinition) -> str:
        if self.env:
            template = self.env.get_template("sqlite_table.j2")
            return template.render(entity=entity)
        return render_sql_content(entity)

    def render_enums(self, enums: Dict[str, EnumDefinition]) -> str:
        if self.env:
            template = self.env.get_template("python_enums.j2")
            return template.render(enums=enums)
        return render_enums_content(enums)

    def render_init(self, entities: List[EntityDefinition]) -> str:
        if self.env:
            template = self.env.get_template("python_init.j2")
            return template.render(entities=entities)
        return render_init_content(entities)

    def render_base(self) -> str:
        if self.env:
            template = self.env.get_template("python_base.j2")
            return template.render()
        return render_base_content()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def generate(domain_path: Path, output_dir: Path) -> None:
    loader = DomainLoader(domain_path)
    domain = loader.load()

    generator = Generator(Path(__file__).parent / "templates")

    python_dir = output_dir / "python"
    sql_dir = output_dir / "sql"
    python_dir.mkdir(parents=True, exist_ok=True)
    sql_dir.mkdir(parents=True, exist_ok=True)

    write_file(python_dir / "base.py", generator.render_base())
    write_file(python_dir / "enums.py", generator.render_enums(domain.enums))

    for entity in domain.entities:
        write_file(
            python_dir / f"{entity.table}.py",
            generator.render_python(entity, domain.enums),
        )
        write_file(sql_dir / f"{entity.table}.sql", generator.render_sql(entity))

    write_file(python_dir / "__init__.py", generator.render_init(domain.entities))


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="BotecoPro domain generator")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Path to domain YAML file")
    parser.add_argument("--out", "-o", type=Path, required=True, help="Output directory")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    generate(args.input, args.out)


__all__ = ["generate", "main", "DomainLoader", "Generator"]
