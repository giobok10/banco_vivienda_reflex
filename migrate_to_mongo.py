"""Migration script: SQLModel (relational) -> MongoDB.

This script extracts rows from SQLModel-managed tables and loads them into
MongoDB collections. It preserves primary keys as `_id` and can be re-run
safely because it performs upserts instead of blind inserts.

Usage:
    python migrate_to_mongo.py

Environment variables (from `.env`):
    DATABASE_URL   SQLAlchemy URL for source relational DB
    MONGO_URI      MongoDB connection string (e.g. Atlas URI)
    MONGO_DB_NAME  (optional) target DB name in MongoDB
"""

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne
from sqlalchemy import create_engine
from sqlmodel import Session, select

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SQL_URL = os.getenv("DATABASE_URL")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not SQL_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in .env")

# ---------------------------------------------------------------------------
# Setup connections
# ---------------------------------------------------------------------------
# Source relational engine
engine = create_engine(SQL_URL)


def resolve_mongo_db_name(uri: str, env_db_name: str | None) -> str:
    """Resolve MongoDB DB name from env override, URI path, or fallback."""
    if env_db_name:
        return env_db_name
    parsed = urlparse(uri)
    path = parsed.path.lstrip("/")
    if path:
        return path.split("?")[0]
    return "banco_vivienda"


mongo_client = MongoClient(MONGO_URI, uuidRepresentation="standard")
mongo_client.admin.command("ping")
mongo_db = mongo_client[resolve_mongo_db_name(MONGO_URI, MONGO_DB_NAME)]

# ---------------------------------------------------------------------------
# Import model definitions – they are registered with Reflex's ModelRegistry
# ---------------------------------------------------------------------------
from banco_vivienda_reflex.models import (
    Usuario,
    Rol,
    Cliente,
    Cuenta,
    Prestamo,
    Pago,
    Telefono,
    Direccion,
    Bitacora,
)

# Mapping from SQLModel class to Mongo collection name (lowercase plural)
MODEL_COLLECTION_MAP = {
    Usuario: "usuarios",
    Rol: "roles",
    Cliente: "clientes",
    Cuenta: "cuentas",
    Prestamo: "prestamos",
    Pago: "pagos",
    Telefono: "telefonos",
    Direccion: "direcciones",
    Bitacora: "bitacora",
}

def migrate_model(session: Session, model, collection_name: str) -> int:
    """Fetch all rows for model and upsert into the target collection.

    Primary key values are kept as ``_id`` in MongoDB to preserve identity.
    ``None`` primary keys (new objects) are omitted – they should not appear in
    a production dump.
    """
    stmt = select(model)
    rows = session.exec(stmt).all()
    operations: list[ReplaceOne] = []
    for row in rows:
        # Compatible conversion for SQLModel/Pydantic variants.
        if hasattr(row, "model_dump"):
            data = row.model_dump()
        else:
            data = row.dict()
        # Rename primary key to _id for MongoDB
        pk_name = next(
            field.name
            for field in model.__table__.columns
            if field.primary_key
        )
        pk_value = data.pop(pk_name)
        if pk_value is None:
            continue
        data["_id"] = pk_value
        operations.append(ReplaceOne({"_id": pk_value}, data, upsert=True))
    if not operations:
        print(f"No data found for model {model.__name__}.")
        return 0
    mongo_db[collection_name].bulk_write(operations, ordered=False)
    print(f"Migrated {len(operations)} documents into '{collection_name}'.")
    return len(operations)


def ensure_indexes() -> None:
    """Create helpful indexes for common lookups."""
    mongo_db["usuarios"].create_index("id_rol")
    mongo_db["clientes"].create_index("id_usuario")
    mongo_db["clientes"].create_index("dpi", unique=True)
    mongo_db["cuentas"].create_index("id_cliente")
    mongo_db["prestamos"].create_index("id_cliente")
    mongo_db["pagos"].create_index("id_prestamo")
    mongo_db["telefonos"].create_index("id_cliente")
    mongo_db["direcciones"].create_index("id_cliente")
    mongo_db["bitacora"].create_index("id_usuario")
    mongo_db["bitacora"].create_index("fecha")

def main():
    total = 0
    with Session(engine) as session:
        for model, coll in MODEL_COLLECTION_MAP.items():
            total += migrate_model(session, model, coll)
    ensure_indexes()
    print(f"Migration completed. Documents processed: {total}.")

if __name__ == "__main__":
    main()
