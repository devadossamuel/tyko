# pylint: disable=too-few-public-methods, invalid-name

import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

AVTables = declarative_base()

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
    first_name = db.Column("first_name", db.Text)
    last_name = db.Column("last_name", db.Text)
    email_address = db.Column("email_address", db.Text)


class Project(AVTables):
    __tablename__ = "project"

    id = db.Column(
        "project_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    project_code = db.Column("project_code", db.Text)
    title = db.Column("title", db.Text)
    current_location = db.Column("current_location", db.Text)
    status = db.Column("status", db.Text)
    specs = db.Column("specs", db.Text)

    def serialize(self):
        return {
            "id": self.id,
            "project_code": self.project_code,
            "current_location": self.current_location,
            "status": self.status,
            "title": self.title
        }


class Collection(AVTables):
    __tablename__ = "collection"
    id = db.Column(
        "collection_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)
    record_series = db.Column("record_series", db.Text)
    collection_name = db.Column("collection_name", db.Text)
    department = db.Column("department", db.Text)
    contact = relationship("Contact")
    contact_id = db.Column(db.Integer, db.ForeignKey("contact.contact_id"))

    def serialize(self):
        return {
            "id": self.id,
            "record_series": self.record_series,
            "collection_name": self.collection_name,
            "contact_id": self.contact_id,
            "department": self.department
        }


class CollectionObject(AVTables):
    __tablename__ = "object"

    id = db.Column(
        "object_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column("name", db.Text)

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

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.contact_id"))

    contact = relationship("Contact", foreign_keys=[contact_id])

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "collection_id": self.collection_id,
            "project_id": self.project_id,
            "last_updated_id": self.last_updated_id,
            "contact_id": self.contact_id
        }


class CollectionItem(AVTables):
    __tablename__ = "item"

    id = db.Column("item_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)
    barcode = db.Column("barcode", db.Text)
    file_name = db.Column("file_name", db.Text)
    medusa_uuid = db.Column("medusa_uuid", db.Text)
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

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "barcode": self.barcode,
            "file_name": self.file_name
        }


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

    name = db.Column("type_name", db.Text)


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

    name = db.Column("name", db.Text)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


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


vendor_transfer_has_an_object = db.Table(
    "vendor_transfer_has_an_object",
    AVTables.metadata,
    db.Column("object_id",
              db.Integer,
              db.ForeignKey("vendor_transfer.vendor_transfer_id")),
    db.Column("vendor_transfer_id",
              db.Integer,
              db.ForeignKey("object.object_id")
              )
)


class VendorTransfer(AVTables):
    __tablename__ = "vendor_transfer"

    id = db.Column(
        "vendor_transfer_id", db.Integer, primary_key=True, autoincrement=True)

    vendor_id = db.Column(
        db.Integer, db.ForeignKey("vendor.vendor_id")
    )
    vendor = relationship("Vendor", foreign_keys=[vendor_id])
    vendor_rec_date = db.Column("vendor_rec_date", db.Date)
    returned_rec_date = db.Column("returned_rec_date", db.Date)

    transfer_objects = relationship(
        "CollectionObject",
        secondary=vendor_transfer_has_an_object,
        backref="transfer_object"
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
    "Inspection": (1, ),
    "Playback": (2, ),
}


format_types = {
    "audio video": (1, AudioVideo),
    "audio": (2,),
    "video": (3,),
    "open reel": (4, OpenReel),
    "grooved disc": (5, GroovedDisc),
    "film": (6, Film)
}
# =============================================================================
