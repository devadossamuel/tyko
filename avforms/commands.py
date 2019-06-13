import avforms.database
import sqlalchemy as db
from typing import NamedTuple, Dict, Callable


class Command(NamedTuple):
    help_documentation: str
    func: Callable


# TODO: FILL in this Information
DATABASE_CONNECTION = "mysql+mysqldb://avuser:avpsw@db:3306/av_preservation"


def initialize():
    print("Initializing database")
    engine = db.create_engine(DATABASE_CONNECTION)
    avforms.database.init_database(engine)
    if not avforms.database.validate_tables(engine):
        raise Exception("Initializing database failed")


commands: Dict[str, Command] = {
    "init": Command("initialize the database", initialize)
}
