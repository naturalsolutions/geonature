"""Migration SRID - Partie 1 : Géométries

Revision ID: 0001_change_srid_geometry_only
Revises:
Create Date: 2025-06-24
"""

from __future__ import annotations
from alembic import op, context
from sqlalchemy.sql import text
import os
import logging
import time
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

logger = logging.getLogger("alembic")

revision = "0001_no_srid"
down_revision = None
branch_labels = ("no_srid",)
depends_on = None

SCRIPTS_SQL_PATH_UPGRADE = [
    "../../data/change_srid/01_drop_constraints.sql",
    "../../data/change_srid/02_drop_index.sql",
    "../../data/change_srid/03_drop_views_and_triggers.sql",
    "../../data/change_srid/04b_alter_types_no_srid.sql",
    "../../data/change_srid/05_create_views.sql",
    "../../data/change_srid/06_create_index_and_triggers.sql",
]

SCRIPTS_SQL_PATH_DOWNGRADE = [
    "../../data/change_srid/01_drop_constraints.sql",
    "../../data/change_srid/02_drop_index.sql",
    "../../data/change_srid/03_drop_views_and_triggers.sql",
    "../../data/change_srid/04a_alter_types_with_srid.sql",
    "../../data/change_srid/05_create_views.sql",
    "../../data/change_srid/06_create_index_and_triggers.sql",
    "../../data/change_srid/07_create_constraints.sql",
]


def _run_sql_files_with_progress(bind, files, params):
    base_dir = os.path.dirname(__file__)
    for rel in files:
        path = os.path.join(base_dir, rel)
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()

        statements = [s.strip() for s in sql.split(";") if s.strip()]
        logger.info(f"[SQL] {rel} — {len(statements)} statements")
        pbar = tqdm(
            total=len(statements), desc=os.path.basename(rel), unit="stmt", dynamic_ncols=True
        )

        for i, stmt in enumerate(statements, 1):
            preview = stmt.replace("\n", " ")[:80]
            t0 = time.time()
            bind.execute(text(stmt), params or {})
            dt = time.time() - t0
            logger.info(f"[SQL] stmt {i}/{len(statements)} ({preview}…) OK in {dt:.2f}s")
            pbar.update(1)

        pbar.close()


def upgrade():
    bind = op.get_bind()
    logger.info("🗺️ Migration vers SRID = 0")
    with logging_redirect_tqdm():
        _run_sql_files_with_progress(
            bind, SCRIPTS_SQL_PATH_UPGRADE, {"new_srid": 0}
        )
    logger.info("=== Fin migration vers SRID 0 ===")


def get_input_srid(bind):
    args = context.get_x_argument(as_dictionary=True)
    if "srid" not in args:
        raise ValueError("❌ Paramètre requis : -x srid=<valeur entière>")

    try:
        srid = int(args["srid"])
    except ValueError:
        raise ValueError(f"❌ SRID invalide : {args['srid']} (doit être un entier)")

    if srid < 0:
        raise ValueError("❌ SRID doit être >= 0")

    # 🔍 Vérification dans spatial_ref_sys
    if srid != 0:
        exists = bind.execute(
            text("SELECT 1 FROM spatial_ref_sys WHERE srid = :srid"),
            {"srid": srid}
        ).scalar()
        if not exists:
            raise ValueError(f"❌ SRID {srid} introuvable dans spatial_ref_sys")
    
    return srid


def downgrade():
    bind = op.get_bind()
    srid = get_input_srid(bind)
    logger.info(f"🗺️ Migration vers SRID = {srid}")
    with logging_redirect_tqdm():
        _run_sql_files_with_progress(bind, SCRIPTS_SQL_PATH_DOWNGRADE, {"new_srid": srid})
    logger.info(f"=== Fin migration vers SRID {srid} ===")
