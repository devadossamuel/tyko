import sys
from typing import Dict, Tuple, Any, Type

import sqlalchemy as db
from sqlalchemy.orm.session import sessionmaker

from tyko import schema


def init_database(engine) -> None:
    # if engine.dialect.has_table(engine, "audio_video"):
    #     return
    print("Creating all tables")
    schema.AVTables.metadata.create_all(bind=engine)
    initial_session = sessionmaker(bind=engine)
    session = initial_session()
    if not engine.dialect.has_table(engine, "alembic_version"):
        version_table = db.Table(
            "alembic_version", schema.AVTables.metadata,
            db.Column("version_num", db.String(length=32), primary_key=True)
        )
        schema.AVTables.metadata.create_all(bind=engine)
        set_version_sql = \
            version_table.insert().values(version_num=schema.ALEMBIC_VERSION)  # noqa: E501 pylint: disable=E1120
        session.execute(set_version_sql)

    session.commit()

    for i in session.query(schema.NoteTypes):
        session.delete(i)
    _populate_note_type_table(session)

    for i in session.query(schema.FormatTypes):
        session.delete(i)

    _populate_format_types_table(session)

    _populate_starting_project_status(
        session, project_status_table=schema.ProjectStatus)

    session.commit()
    session.close()

    if not validate_tables(engine):
        raise IOError("Newly created database is invalid")

    if not validate_enumerated_tables(engine):
        raise IOError("Table data has changed")


def _populate_note_type_table(session):
    print("Populating NoteTypes Table")
    for note_type, note_metadata in schema.note_types.items():
        note_id = note_metadata[0]

        new_note_type = schema.NoteTypes(name=note_type, id=note_id)
        session.add(new_note_type)


def _populate_starting_project_status(
        session,
        project_status_table: Type[schema.ProjectStatus]) -> None:

    print("Populating {} Table".format(project_status_table.__tablename__))
    statuses = ['In progress', "Complete", "No work done"]
    for status in statuses:
        new_status = project_status_table(name=status)
        session.add(new_status)


def _populate_format_types_table(session):
    print("Populating project_status_type Table")
    for format_type, format_metadata in schema.format_types.items():
        format_id = format_metadata[0]

        new_format_type = schema.FormatTypes(name=format_type, id=format_id)
        session.add(new_format_type)


def validate_enumerated_tables(engine):
    session = sessionmaker(bind=engine)()
    valid = True

    if not validate_enumerate_table_data(
            engine, schema.FormatTypes, schema.format_types):

        valid = False

    if not validate_enumerate_table_data(
            engine, schema.NoteTypes, schema.note_types):

        valid = False

    session.close()
    return valid


def validate_enumerate_table_data(engine,
                                  sql_table_type: Type[schema.AVTables],
                                  expected_table: Dict[str, Tuple[int, Any]]
                                  ) -> bool:

    session = sessionmaker(bind=engine)()
    valid = True

    for table_entry in session.query(sql_table_type):
        expected_item = expected_table.get(table_entry.name)

        if expected_item is None:
            return False

        expected_id = expected_item[0]

        if expected_id != table_entry.id:
            print(f"Type {table_entry.name} does not match expected id. "
                  f"expected {expected_id}. "
                  f"got {table_entry.id}.",
                  file=sys.stderr)
            valid = False

    session.close()
    return valid


def validate_tables(engine):

    expected_table_names = []
    for k in schema.AVTables.metadata.tables.keys():
        expected_table_names.append(k)

    valid = True

    for table in db.inspect(engine).get_table_names():
        if table not in expected_table_names:
            print("Unexpected table found: {}".format(table))
            valid = False
        else:
            expected_table_names.remove(table)

    if len(expected_table_names) > 0:
        print("Missing tables [{}]".format(",".join(expected_table_names)))
        valid = False
    return valid
