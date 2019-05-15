import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PreservationStaff(Base):
    __tablename__ = "preservation_staff"
    id = db.Column(
        "staff_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)
    first_name = db.Column("first_name", db.String)
    last_name = db.Column("last_name", db.String)
    email_address = db.Column("email_address", db.String)


def validate_tables(engine):

    expected_table_names = [
        "audio_video",
        "collection",
        "collection_contact",
        "film",
        "format",
        "grooved_disc",
        "item",
        "object",
        "open_reel",
        "preservation_staff",
        "project",
        "vendor",
        "vendor_contact",
        "vendor_item_transfers",
    ]

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
