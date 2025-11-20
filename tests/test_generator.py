from pathlib import Path
import py_compile
import sqlite3

from botecopro_meta.generator import generate


def test_generate_outputs(tmp_path: Path) -> None:
    domain_path = Path(__file__).resolve().parent.parent / "db-meta" / "tables" / "001_domain.yaml"
    output_dir = tmp_path / "generated"

    generate(domain_path, output_dir)

    python_dir = output_dir / "python"
    sql_dir = output_dir / "sql"

    # Basic Python artifacts
    assert (python_dir / "base.py").exists()
    assert (python_dir / "enums.py").exists()

    model_files = list(python_dir.glob("*.py"))
    assert model_files, "Expected model files to be generated"

    for py_file in model_files:
        py_compile.compile(str(py_file), doraise=True)

    # SQLite DDL can be applied
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON;")
    for sql_file in sorted(sql_dir.glob("*.sql")):
        conn.executescript(sql_file.read_text())

    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table';")}
    assert "category" in tables
    assert "order_item" in tables

    category_info = conn.execute("PRAGMA table_info('category')").fetchall()
    column_names = [row[1] for row in category_info]
    assert {"id", "name"}.issubset(column_names)

    fk_list = conn.execute("PRAGMA foreign_key_list('order_item')").fetchall()
    assert any(fk[2] == "order" for fk in fk_list)

    conn.close()
