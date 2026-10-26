
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
        connection.execute(
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
        WHERE content LIKE ? COLLATE NOCASE
    """
    parameters = [f"%{query.strip()}%"]

    if memory_type is not None:
        if not isinstance(memory_type, str) or not memory_type.strip():
            raise ValueError("memory_type must be a non-empty string")
        sql += " AND memory_type = ?"
        parameters.append(memory_type.strip())

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


def build_research_context(
    query,
    max_chars=4000,
    limit=50,
    db_path=DEFAULT_DB_PATH,
):
    """
    Build a bounded context from matching saved research memories.

    Newer matching memories are considered first. A memory is included
    only if its formatted representation fits within max_chars.

    This uses character limits as a simple approximation, not a
    model-specific token counter.
    """

    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")

    if (
        not isinstance(max_chars, int)
        or isinstance(max_chars, bool)
        or max_chars < 1
    ):
        raise ValueError("max_chars must be a positive integer")

    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        raise ValueError("limit must be at least 1")

    memories = search_research_memory(
        query=query,
        limit=limit,
        db_path=db_path,
    )

    selected = []
    used_chars = 0

    for memory in memories:
        entry = (
            f"[{memory['memory_type']} | ID: {memory['id']}]\n"
            f"{memory['content']}"
        )

        separator = "\n\n" if selected else ""
        required_chars = len(separator) + len(entry)

        if used_chars + required_chars > max_chars:
            continue

        selected.append(entry)
        used_chars += required_chars

    return "\n\n".join(selected)
