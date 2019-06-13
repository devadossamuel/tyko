import sqlalchemy as db

import avforms.database

# TODO: FILL in this Information
DATABASE_CONNECTION = "mysql+mysqldb://avuser:avpsw@db:3306/av_preservation"


def main() -> None:
    engine = db.create_engine(DATABASE_CONNECTION)
    avforms.database.init_database(engine)
    is_valid = avforms.database.validate_tables(engine)
    # with engine.connect() as connection:
