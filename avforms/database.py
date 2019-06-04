import sys
from typing import Dict, Tuple, Any

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

AVTables = declarative_base()


def init_database(engine):
    AVTables.metadata.create_all(bind=engine)

    initial_session = sessionmaker(bind=engine)
    session = initial_session()
    _populate_note_type_table(session)
    _populate_format_types_table(session)

    session.commit()
    session.close()

    if not(validate_tables(engine)):
        raise IOError("Newly created database is invalid")

    if not(validate_enumerated_tables(engine)):
        raise IOError("Table data has changed")


def _populate_note_type_table(session):

    for note_type, note_metadata in note_types.items():
        note_id = note_metadata[0]

        new_note_type = NoteTypes(name=note_type, id=note_id)
        session.add(new_note_type)


def _populate_format_types_table(session):
    for format_type, format_metadata in format_types.items():
        format_id = format_metadata[0]

        new_format_type = FormatTypes(name=format_type, id=format_id)
        session.add(new_format_type)


def validate_enumerated_tables(engine):
    session = sessionmaker(bind=engine)()
    valid = True

    if not validate_enumerate_table_data(engine, FormatTypes, format_types):
        valid = False

    if not validate_enumerate_table_data(engine, NoteTypes, note_types):
        valid = False

    session.close()
    return valid


def validate_enumerate_table_data(engine, sql_table_type: AVTables,
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

    expected_table_names = [k for k in AVTables.metadata.tables.keys()]

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


item_has_notes_table = db.Table(
    "item_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("item.item_id")),
    db.Column("item_id", db.Integer, db.ForeignKey("notes.note_id"))
)


object_has_notes_table = db.Table(
    "object_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("object.object_id")),
    db.Column("object_id", db.Integer, db.ForeignKey("notes.note_id"))
)


class Contact(AVTables):
    __tablename__ = "contact"
    id = db.Column(
        "contact_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)
    first_name = db.Column("first_name", db.String)
    last_name = db.Column("last_name", db.String)
    email_address = db.Column("email_address", db.String)


class Project(AVTables):
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


class Collection(AVTables):
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


class CollectionObject(AVTables):
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

    notes = relationship("Note",
                         secondary=object_has_notes_table,
                         backref="object_sources"
                         )

    items = relationship("CollectionItem", backref="item_id")


class CollectionItem(AVTables):
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
    notes = relationship("Note",
                         secondary=item_has_notes_table,
                         backref="item_sources"
                         )

    treatment = relationship("Treatment", backref="treatment_id")

    format_type_id = db.Column(db.Integer,
                               db.ForeignKey("format_types.format_id"))

    format_type = relationship("FormatTypes", foreign_keys=[format_type_id])


class Note(AVTables):
    __tablename__ = "notes"

    id = db.Column("note_id", db.Integer, primary_key=True, autoincrement=True)
    text = db.Column("text", db.Text)

    note_type_id = db.Column(
        db.Integer, db.ForeignKey("note_types.note_types_id"))

    note_type = relationship("NoteTypes", foreign_keys=[note_type_id])


class NoteTypes(AVTables):
    __tablename__ = "note_types"
    id = db.Column(
        "note_types_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("type_name", db.String)


class Treatment(AVTables):
    __tablename__ = "treatment"
    id = db.Column(
        "treatment_id", db.Integer, primary_key=True, autoincrement=True)

    needed = db.Column("needed", db.Text)
    given = db.Column("given", db.Text)
    date = db.Column("date", db.Date)
    item_id = db.Column(db.Integer, db.ForeignKey("item.item_id"))


class FormatTypes(AVTables):
    __tablename__ = "format_types"

    id = db.Column(
        "format_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.String)


class OpenReel(AVTables):
    __tablename__ = "open_reel"

    item_id = db.Column(
        db.Integer, db.ForeignKey("item.item_id"), primary_key=True)

    item = relationship("CollectionItem", foreign_keys=[item_id])

    date_recorded = db.Column(
        "date_recorded", db.Date
    )

    track_count = db.Column("track_count", db.Text)
    tape_size = db.Column("tape_size", db.Text)
    reel_diam = db.Column("reel_diam", db.Integer)
    reel_type = db.Column("reel_type", db.Text)
    tape_thickness = db.Column("tape_thickness", db.Integer)
    tape_brand = db.Column("tape_brand", db.Text)
    base = db.Column("base", db.Text)
    wind = db.Column("wind", db.Text)
    track_speed = db.Column("track_speed", db.Text)
    track_configuration = db.Column("track_configuration", db.Text)
    track_duration = db.Column("track_duration", db.Text)
    generation = db.Column("generation", db.Text)


class Film(AVTables):
    __tablename__ = "film"

    item_id = db.Column(
        db.Integer, db.ForeignKey("item.item_id"), primary_key=True)

    item = relationship("CollectionItem", foreign_keys=[item_id])

    date_of_film = db.Column("date_of_film", db.Date)
    can_label = db.Column("can_label", db.Text)
    leader_label = db.Column("leader_label", db.Text)
    length = db.Column("length", db.Integer)
    duration = db.Column("duration", db.Text)
    format_gauge = db.Column("format_gauge", db.Integer)
    base = db.Column("base", db.Text)
    edge_code_date = db.Column("edge_code_date", db.Date)
    sound = db.Column("sound", db.Text)
    color = db.Column("color", db.Text)
    image_type = db.Column("image_type", db.Text)
    ad_test_date = db.Column("ad_test_date", db.Date)
    ad_test_level = db.Column("ad_test_level", db.Integer)


class GroovedDisc(AVTables):
    __tablename__ = "grooved_disc"

    item_id = db.Column(
        db.Integer, db.ForeignKey("item.item_id"), primary_key=True)

    item = relationship("CollectionItem", foreign_keys=[item_id])

    # This is a year
    date_recorded = db.Column("date_recorded", db.Integer)
    side = db.Column("side", db.Text)
    duration = db.Column("duration", db.Text)
    diameter = db.Column("diameter", db.Integer)
    disc_material = db.Column("disc_material", db.Text)
    base = db.Column("base", db.Text)
    playback_direction = db.Column("playback_direction", db.Text)
    playback_speed = db.Column("playback_speed", db.Text)


class AudioVideo(AVTables):
    __tablename__ = "audio_video"

    item_id = db.Column(
        db.Integer, db.ForeignKey("item.item_id"), primary_key=True)

    item = relationship("CollectionItem", foreign_keys=[item_id])
    date_recorded = db.Column("date_recorded", db.Date)
    side = db.Column("side", db.Text)
    duration = db.Column("duration", db.Text)
    format_subtype = db.Column("format_subtype", db.Text)


vendor_has_contacts_table = db.Table(
    "item_has_contacts",
    AVTables.metadata,
    db.Column("contact_id", db.Integer, db.ForeignKey("vendor.vendor_id")),
    db.Column("vendor_id", db.Integer, db.ForeignKey("contact.contact_id"))
)


class Vendor(AVTables):
    __tablename__ = "vendor"

    id = db.Column(
        "vendor_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)
    address = db.Column("address", db.Text)
    city = db.Column("city", db.Text)
    state = db.Column("state", db.Text)
    zipcode = db.Column("zipcode", db.Text)
    contacts = relationship("Contact",
                            secondary=vendor_has_contacts_table,
                            backref="vendor_id"
                            )


# =============================================================================
# Enumerated tables
# =============================================================================
#
# To keep the enumerated id tables consistent, the ids are hardcoded
#
# Important Note:
#
# Add to the bottom of this list, For compatibility reasons, do not
# edit existing value ids

note_types = {
    "Inspection": (0, ),
    "Playback": (1, ),
}


format_types = {
    "audio video": (0, AudioVideo),
    "audio": (1,),
    "video": (2,),
    "open reel": (3, OpenReel),
    "grooved disc": (4, GroovedDisc),
    "film": (5, Film)
}
# =============================================================================
