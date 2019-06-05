import sqlalchemy as db

import avforms.database

# TODO: FILL in this Information
DATABASE_CONNECTION = ""


def main() -> None:
    engine = db.create_engine(DATABASE_CONNECTION)

    avforms.database.validate_tables(engine)
    # with engine.connect() as connection:
