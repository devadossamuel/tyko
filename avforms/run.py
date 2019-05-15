import sqlalchemy as db
from avforms import database

# TODO: FILL in this Information
DATABASE_CONNECTION = ""


def main():
    engine = db.create_engine(DATABASE_CONNECTION)

    database.validate_tables(engine)
    # with engine.connect() as connection:
