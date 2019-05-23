import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


def init_database(engine):
    Base.metadata.create_all(bind=engine)

    initial_session = sessionmaker(bind=engine)
    session = initial_session()
    _populate_note_type_table(session)
    session.commit()
    session.close()
    if not(validate_tables(engine)):
        raise IOError("Newly created database is invalid")


def _populate_note_type_table(session):
    note_types = [
        "Inspection",
        "Playback"
    ]
    for note_type in note_types:
        new_note_type = NoteTypes(type_name=note_type)
        session.add(new_note_type)


def validate_tables(engine):

    expected_table_names = [
        "collection",
        "contact",
        "item",
        "note_types",
        "notes",
        "object",
        "project",
        # "audio_video",
        # "collection",
        # "collection_contact",
        # "film",
        # "format",
        # "grooved_disc",
        # "item",
        # "object",
        # "open_reel",
        # "preservation_staff",
        # "project",
        # "vendor",
        # "vendor_contact",
        # "vendor_item_transfers",
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


class Project(Base):
    __tablename__ = "project"

    id = db.Column(
        "project_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    code = db.Column("code", db.String)
    title = db.Column("title", db.String)
    current_location = db.Column("current_location", db.String)
    status = db.Column("status", db.String)
    specs = db.Column("specs", db.String)


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


class CollectionObject(Base):
    __tablename__ = "object"

    id = db.Column(
        "object_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column("name", db.String)

    collection_id = \
        db.Column(db.Integer, db.ForeignKey("collection.collection_id"))

    collection = relationship("Collection", foreign_keys=[collection_id])

    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"))
    project = relationship("Project", foreign_keys=[project_id])

    last_updated_id = \
        db.Column(db.Integer, db.ForeignKey("contact.contact_id"))
    last_updated = relationship("Contact", foreign_keys=[last_updated_id])


class CollectionItem(Base):
    __tablename__ = "item"

    id = db.Column("item_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.String)
    barcode = db.Column("barcode", db.String)
    file_name = db.Column("file_name", db.String)
    medusa_uuid = db.Column("medusa_uuid", db.String)
    original_rec_date = db.Column("original_rec_date", db.Date)
    original_return_date = db.Column("original_return_date", db.Date)

    collection_object_id = db.Column(db.Integer,
                                     db.ForeignKey("object.object_id"))

    collection_object = relationship("CollectionObject",
                                     foreign_keys=[collection_object_id])

    obj_sequence = db.Column("obj_sequence", db.Integer)


class Note(Base):
    __tablename__ = "notes"

    id = db.Column("note_id", db.Integer, primary_key=True, autoincrement=True)
    text = db.Column("text", db.Text)
    note_type_id = db.Column(db.Integer, db.ForeignKey("note_types.note_types_id"))
    note_type = relationship("NoteTypes", foreign_keys=[note_type_id])


class NoteTypes(Base):
    __tablename__ = "note_types"
    id = db.Column("note_types_id", db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column("type_name", db.String)
