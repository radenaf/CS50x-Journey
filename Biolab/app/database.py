from sqlalchemy import inspect, text

from app import db


def ensure_development_schema():
    """Bridge the initial prototype SQLite schema to the current model schema."""
    if db.engine.dialect.name != "sqlite":
        return

    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    columns = {table: {column["name"] for column in inspector.get_columns(table)} for table in tables}
    additions = {
        "pcr_experiment": {
            "pcr_type": "VARCHAR(80) NOT NULL DEFAULT 'Custom PCR'",
            "target": "VARCHAR(160)",
            "reaction_volume_ul": "FLOAT NOT NULL DEFAULT 25",
            "instrument": "VARCHAR(160)",
            "experiment_date": "DATE NOT NULL DEFAULT '2026-08-15'",
            "replicate_type": "VARCHAR(40) NOT NULL DEFAULT 'None'",
            "technical_replicates": "INTEGER NOT NULL DEFAULT 1",
            "biological_replicates": "INTEGER NOT NULL DEFAULT 1",
            "sample_count": "INTEGER NOT NULL DEFAULT 0",
            "positive_controls": "INTEGER NOT NULL DEFAULT 0",
            "negative_controls": "INTEGER NOT NULL DEFAULT 0",
            "ntcs": "INTEGER NOT NULL DEFAULT 0",
            "master_mix_excess_percent": "FLOAT NOT NULL DEFAULT 10",
            "extra_reactions": "INTEGER NOT NULL DEFAULT 0",
        },
        "pcr_template": {"pcr_type": "VARCHAR(80) NOT NULL DEFAULT 'Custom PCR'", "target": "VARCHAR(160)", "instrument": "VARCHAR(160)", "protocol_json": "TEXT"},
        "sample": {"specimen_id": "VARCHAR(160)", "sample_type": "VARCHAR(80)", "result": "VARCHAR(160)", "notes": "TEXT"},
        "control": {"result": "VARCHAR(160)", "notes": "TEXT"},
        "reagent": {"volume_per_reaction_ul": "FLOAT NOT NULL DEFAULT 0", "category": "VARCHAR(40) NOT NULL DEFAULT 'Other'", "include_in_master_mix": "BOOLEAN NOT NULL DEFAULT 1", "experiment_id": "INTEGER"},
        "pcr_program": {"experiment_id": "INTEGER"},
        "pcr_cycle_group": {"program_id": "INTEGER"},
        "pcr_step": {"name": "VARCHAR(160) NOT NULL DEFAULT 'Step'", "step_type": "VARCHAR(40) NOT NULL DEFAULT 'step'", "goto_step": "INTEGER", "repeat_count": "INTEGER NOT NULL DEFAULT 0", "cycle_group_id": "INTEGER"},
        "plate": {"experiment_id": "INTEGER"},
        "plate_well": {"target": "VARCHAR(160)", "sample_id": "INTEGER", "control_id": "INTEGER"},
    }

    with db.engine.begin() as connection:
        for table, table_additions in additions.items():
            if table not in tables:
                continue
            for name, definition in table_additions.items():
                if name not in columns[table]:
                    connection.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {definition}'))
