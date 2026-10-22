
import json
import sqlite3
from pathlib import Path


DEFAULT_DB_PATH = "data/research_memory.db"


def save_research_memory(
    content,
    memory_type="note",
    metadata=None,
    db_path=DEFAULT_DB_PATH,
):
    """Persist a research note, hypothesis, result, or decision."""

    if not isinstance(content, str) or not content.strip():
        raise ValueError("content must be a non-empty string")

    if not isinstance(memory_type, str) or not memory_type.strip():
        raise ValueError("memory_type must be a non-empty string")

    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("metadata must be a dictionary")

    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    metadata_json = json.dumps(metadata or {})

    with sqlite3.connect(path) as connection:
        cursor = connection.execute(
            """
            CREATE TABLE IF NOT EXISTS research_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
            """
        )

        cursor = connection.execute(
            """
            INSERT INTO research_memories (content, memory_type, metadata)
            VALUES (?, ?, ?)
            """,
            (content.strip(), memory_type.strip(), metadata_json),
        )

        memory_id = cursor.lastrowid

    return memory_id


def search_research_memory(
    query,
    memory_type=None,
    limit=10,
    db_path=DEFAULT_DB_PATH,
):
    """Search saved research memories by matching text."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be at least 1")

    path = Path(db_path)

    if not path.is_file():
        return []

    sql = """
        SELECT id, content, memory_type, metadata
        FROM research_memories
        WHERE content LIKE ?
    """
    parameters = [f"%{query.strip()}%"]

    if memory_type is not None:
        sql += " AND memory_type = ?"
        parameters.append(memory_type)

    sql += " ORDER BY id DESC LIMIT ?"
    parameters.append(limit)

    with sqlite3.connect(path) as connection:
        rows = connection.execute(sql, parameters).fetchall()

    return [
        {
            "id": row[0],
            "content": row[1],
            "memory_type": row[2],
            "metadata": json.loads(row[3]),
        }
        for row in rows
    ]
