"""Read-only VALEXII LUX source catalogue. No network, inference or publication authority."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit

VALID_SYSTEMS = {"AUREX", "XAELI", "DISPATER", "MEDAURUS", "LUX", "VALEXII Core"}
VALID_KINDS = {"catalogue", "standard", "software", "index", "repository", "book", "paper", "artifact"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
 id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE,
 kind TEXT NOT NULL, purpose TEXT NOT NULL, systems TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status='DISCOVERED'),
 admission TEXT NOT NULL CHECK(admission='NOT_ADMITTED'),
 rights TEXT NOT NULL CHECK(rights='NOT_REVIEWED'),
 full_text_downloaded INTEGER NOT NULL CHECK(full_text_downloaded=0)
);
CREATE INDEX IF NOT EXISTS idx_sources_title ON sources(title);
"""

def validate(record: dict) -> dict:
    required = {"id", "title", "url", "systems", "purpose", "kind", "status",
                "admission", "rights", "full_text_downloaded"}
    if set(record) != required:
        raise ValueError("Unexpected or missing fields")
    if not all(isinstance(record[k], str) and record[k].strip()
               for k in ("id", "title", "url", "purpose", "kind")):
        raise ValueError("Invalid text field")
    if len(record["id"]) > 100 or len(record["title"]) > 500 or len(record["purpose"]) > 2000:
        raise ValueError("Field exceeds limit")
    parsed = urlsplit(record["url"])
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Source URL must be a canonical HTTPS URL")
    if not isinstance(record["systems"], list) or not record["systems"] or not set(record["systems"]) <= VALID_SYSTEMS:
        raise ValueError("Unknown system")
    if record["kind"] not in VALID_KINDS:
        raise ValueError("Unknown source kind")
    if (record["status"], record["admission"], record["rights"], record["full_text_downloaded"]) != (
        "DISCOVERED", "NOT_ADMITTED", "NOT_REVIEWED", False
    ):
        raise ValueError("Cannot grant admission, rights or download authority through import")
    return record

def import_jsonl(db_path: str | Path, jsonl_path: str | Path) -> int:
    """Validate all records before modifying the database; reject duplicates."""
    records = [validate(json.loads(line)) for line in Path(jsonl_path).read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [r["id"] for r in records]
    urls = [r["url"] for r in records]
    if len(set(ids)) != len(ids) or len(set(urls)) != len(urls):
        raise ValueError("Duplicate source identifier or URL")
    with sqlite3.connect(db_path) as db:
        db.executescript(SCHEMA)
        for r in records:
            db.execute("""INSERT INTO sources
                (id,title,url,kind,purpose,systems,status,admission,rights,full_text_downloaded)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                title=excluded.title, url=excluded.url, kind=excluded.kind,
                purpose=excluded.purpose, systems=excluded.systems
                WHERE sources.status='DISCOVERED' AND sources.admission='NOT_ADMITTED'
                AND sources.rights='NOT_REVIEWED' AND sources.full_text_downloaded=0""",
                (r["id"],r["title"],r["url"],r["kind"],r["purpose"],json.dumps(r["systems"]),
                 r["status"],r["admission"],r["rights"],0))
    return len(records)

def search(db_path: str | Path, query: str = "", system: str | None = None, limit: int = 50) -> list[dict]:
    if system is not None and system not in VALID_SYSTEMS:
        raise ValueError("Unknown system")
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Limit out of bounds")
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT * FROM sources WHERE (title LIKE ? OR purpose LIKE ?) ORDER BY title LIMIT ?",
                          (f"%{query}%",f"%{query}%",limit)).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["systems"] = json.loads(item["systems"])
        item["full_text_downloaded"] = bool(item["full_text_downloaded"])
        if system is None or system in item["systems"]:
            result.append(item)
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="lux_sources.sqlite")
    parser.add_argument("--import-file")
    parser.add_argument("--search", default="")
    parser.add_argument("--system")
    args = parser.parse_args()
    if args.import_file:
        print(json.dumps({"imported": import_jsonl(args.db, args.import_file)}))
    else:
        print(json.dumps(search(args.db, args.search, args.system), indent=2))
