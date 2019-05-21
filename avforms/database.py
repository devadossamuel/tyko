import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()


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


class Contact(Base):
    __tablename__ = "contact"
    id = db.Column(
        "contact_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)
    first_name = db.Column("first_name", db.String)
    last_name = db.Column("last_name", db.String)
    email_address = db.Column("email_address", db.String)


class Collection(Base):
    __tablename__ = "collection"
    id = db.Column(
        "collection_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)
    record_series = db.Column("record_series", db.String)
    collection_name = db.Column("collection_name", db.String)
    department = db.Column("department", db.String)
    contact = relationship("Contact")
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.contact_id"))
