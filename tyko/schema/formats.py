import datetime
import warnings
from abc import ABC

from typing import Optional, Tuple, TYPE_CHECKING, Mapping
import re
import sqlalchemy as db
from sqlalchemy.orm import relationship
from tyko import utils
from tyko.schema.avtables import AVTables, SerializedData

if TYPE_CHECKING:
    from tyko.schema.objects import CollectionObject  # noqa: F401
    from tyko.schema.treatment import Treatment  # noqa: F401
    from tyko.schema.instantiation import InstantiationFile  # noqa: F401
    from tyko.schema.notes import Note  # noqa: F401


item_has_notes_table = db.Table(
    "item_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("notes.note_id")),
    db.Column("item_id", db.Integer, db.ForeignKey("formats.item_id"))
)


class AVFormat(AVTables):
    __tablename__ = 'formats'
    name = db.Column("name", db.Text)
    type = db.Column(db.Text())
    FK_TABLE_ID = "formats.item_id"
    table_id = db.Column(
        "item_id",
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    __mapper_args__ = {
        'polymorphic_identity': 'formats',
        'polymorphic_on': type
    }
    obj_sequence = db.Column("obj_sequence", db.Integer)

    object_id = db.Column(db.Integer, db.ForeignKey("tyko_object.object_id"))

    notes = relationship("Note",
                         secondary=item_has_notes_table,
                         backref="item_source"
                         )

    format_type_id = db.Column(db.Integer,
                               db.ForeignKey("format_types.format_id"))

    format_type = relationship("FormatTypes", foreign_keys=[format_type_id])
    files = relationship("InstantiationFile", backref="file_source")
    treatment = relationship("Treatment", backref="treatment_id")

    def _iter_files(self, recurse=False):
        for file_ in self.files:
            if recurse is True:
                yield file_.serialize(recurse=True)
            else:
                yield {
                    "name": file_.file_name,
                    "id": file_.file_id,
                    "generation": file_.generation
                }

    def _iter_notes(self):
        yield from self.notes

    def format_details(self) -> Mapping[str, SerializedData]:
        return dict()

    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:

        data = {
            "item_id": self.table_id,
            "name": self.name,
            "files": list(self._iter_files(recurse)),
            "parent_object_id": self.object_id,
            "obj_sequence": self.obj_sequence,
        }
        notes = []
        for note in self._iter_notes():
            notes.append(note.serialize())
        data['notes'] = notes
        try:
            data["format"] = self.format_type.serialize()
            data["format_id"] = self.format_type_id
        except AttributeError:
            data["format"] = None
            data["format_id"] = None
        data['format_details'] = self.format_details()
        return data


class FormatTypes(AVTables):
    __tablename__ = "format_types"

    id = db.Column(
        "format_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)

    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:
        return {
            "format_types_id": self.id,
            "name": self.name
        }


# ###############################  AV Formats #################################

class OpenReel(AVFormat):
    __tablename__ = "open_reels"
    __mapper_args__ = {'polymorphic_identity': 'open_reels'}
    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)
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

    object = relationship("CollectionObject",
                          back_populates="open_reels")

    def format_details(self) -> Mapping[str, SerializedData]:
        return {
            "date_recorded": utils.serialize_precision_datetime(
                self.date_recorded)
            if self.date_recorded is not None else None,
            "track_count": self.track_count,
            "tape_size": self.tape_size,
            "reel_diam": self.reel_diam,
            "reel_type": self.reel_type,
            "tape_thickness": self.tape_thickness,
            "tape_brand": self.tape_brand,
            "base": self.base,
            "wind": self.wind,
            "track_speed": self.track_speed,
            "track_configuration": self.track_configuration,
            "track_duration": self.track_duration,
            "generation": self.generation
        }


class Film(AVFormat, ABC):

    __tablename__ = "films"
    __mapper_args__ = {
        'polymorphic_identity': 'films'
    }

    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)

    object = relationship("CollectionObject",
                          back_populates="films")

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

    def format_details(self) -> Mapping[str, SerializedData]:
        return {
            "date_of_film":
                utils.serialize_precision_datetime(self.date_of_film)
                if self.date_of_film is not None else None,
            "can_label": self.can_label,
            "leader_label": self.leader_label,
            "length": self.length,
            "duration": self.duration,
            "format_gauge": self.format_gauge,
            "base": self.base,
            "edge_code_date":
                utils.serialize_precision_datetime(
                    self.edge_code_date)
                if self.edge_code_date is not None else None,
            "sound": self.sound,
            "color": self.color,
            "image_type": self.image_type,
            "ad_test_date":
                utils.serialize_precision_datetime(
                    self.ad_test_date)
                if self.ad_test_date is not None else None,
            "ad_test_level": self.ad_test_level
        }


class GroovedDisc(AVFormat, ABC):
    __tablename__ = "grooved_discs"
    __mapper_args__ = {'polymorphic_identity': 'grooved_discs'}
    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)

    object = relationship("CollectionObject",
                          back_populates="groove_disks")

    # This is a year
    date_recorded = db.Column("date_recorded", db.Integer)
    side = db.Column("side", db.Text)
    duration = db.Column("duration", db.Text)
    diameter = db.Column("diameter", db.Integer)
    disc_material = db.Column("disc_material", db.Text)
    base = db.Column("base", db.Text)
    playback_direction = db.Column("playback_direction", db.Text)
    playback_speed = db.Column("playback_speed", db.Text)

    def format_details(self) -> Mapping[str, SerializedData]:
        return {
            "date_recorded": self.date_recorded,
            "side": self.side,
            "duration": self.duration,
            "diameter": self.diameter,
            "disc_material": self.disc_material,
            "base": self.base,
            "playback_direction": self.playback_direction,
            "playback_speed": self.playback_speed
        }


class AudioVideo(AVFormat):
    __tablename__ = "audio_videos"
    __mapper_args__ = {'polymorphic_identity': 'audio_videos'}
    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)

    object = relationship("CollectionObject",
                          back_populates="audio_videos")

    av_date_recorded = db.Column("date_recorded", db.Date)
    side = db.Column("side", db.Text)
    duration = db.Column("duration", db.Text)
    format_subtype = db.Column("format_subtype", db.Text)

    def format_details(self) -> Mapping[str, SerializedData]:
        return {
            "date_recorded":
                utils.serialize_precision_datetime(
                    self.av_date_recorded)
                if self.av_date_recorded is not None else None,
            "side": self.side,
            "duration": self.duration,
            "format_subtype": self.format_subtype

        }


class AudioCassette(AVFormat, ABC):
    __tablename__ = 'audio_cassettes'
    __mapper_args__ = {'polymorphic_identity': 'audio_cassettes'}

    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)

    object = relationship("CollectionObject",
                          back_populates="audio_cassettes")

    cassette_format_type_id = db.Column(
        db.Integer,
        db.ForeignKey("cassette_types.table_id")
    )

    cassette_type = relationship("CassetteType")

    tape_type_id = db.Column(db.Integer,
                             db.ForeignKey("cassette_tape_types.table_id"))

    tape_type = relationship("CassetteTapeType")

    tape_thickness_id = \
        db.Column(db.Integer,
                  db.ForeignKey("cassette_tape_thickness.table_id"))

    tape_thickness = relationship("CassetteTapeThickness")

    inspection_date = db.Column("inspection_date", db.Date)
    recording_date = db.Column("recording_date", db.Date)
    recording_date_precision = db.Column("recording_date_precision",
                                         db.Integer, default=3)

    # REGEX
    REGEX_DAY_MONTH_YEAR = re.compile(r"^([0-1][0-9])-([0-2][0-9])-([0-9]){4}")
    REGEX_YEAR_ONLY = re.compile(r"^([1-9]){4}$")
    REGEX_MONTH_YEAR = re.compile(r"^([0-1][0-9])-([0-9]){4}$")

    @classmethod
    def serialize_date(cls, date: Optional[datetime.date],
                       precision=3) -> str:
        warnings.warn(
            "Use utils.serialize_precision_datetime instead",
            DeprecationWarning
        )

        if isinstance(date, datetime.date):
            if precision == 3:
                return date.strftime("%m-%d-%Y")

            if precision == 2:
                return date.strftime("%m-%Y")

            if precision == 1:
                return date.strftime("%Y")

        raise AttributeError("Unable to serialize date {}".format(date))

    @classmethod
    def encode_date(cls, date_string: str) -> Tuple[datetime.datetime, int]:
        warnings.warn("use utils.serialize_precision_datetime instead",
                      DeprecationWarning)

        if cls.REGEX_DAY_MONTH_YEAR.match(date_string):
            return datetime.datetime.strptime(date_string, "%m-%d-%Y"), 3

        if cls.REGEX_MONTH_YEAR.match(date_string):
            return datetime.datetime.strptime(date_string, "%m-%Y"), 2

        if cls.REGEX_YEAR_ONLY.match(date_string):
            return datetime.datetime.strptime(date_string, "%Y"), 1

        raise AttributeError("Unknown date format: {}".format(date_string))

    def format_details(self) -> Mapping[str, SerializedData]:

        serialized_data = {
            "cassette_type": self.cassette_type.serialize(),
            "inspection_date":
                utils.serialize_precision_datetime(
                    self.inspection_date)
                if self.inspection_date is not None else None,
            "date_recorded":
                utils.serialize_precision_datetime(
                    self.recording_date,
                    self.recording_date_precision)
                if self.recording_date is not None
                else None,
        }

        if self.tape_type is not None:
            serialized_data["tape_type"] = self.tape_type.serialize()
        else:
            serialized_data["tape_type"] = None

        if self.tape_thickness is not None:
            serialized_data["tape_thickness"] = self.tape_thickness.serialize()
        else:
            serialized_data["tape_thickness"] = None

        return serialized_data


class CollectionItem(AVFormat):
    __tablename__ = "items"
    __mapper_args__ = {'polymorphic_identity': 'items'}
    table_id = db.Column(db.Integer, db.ForeignKey(AVFormat.FK_TABLE_ID),
                         primary_key=True)

    object = relationship("CollectionObject",
                          back_populates="collection_items")

    def format_details(self) -> Mapping[str, SerializedData]:
        return dict()

# ############################ End of AV Formats ##############################


class CassetteType(AVTables):
    __tablename__ = "cassette_types"
    table_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column("name", db.Text)

    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:
        return {
            "name": self.name,
            "id": self.table_id
        }


class CassetteTapeType(AVTables):
    __tablename__ = "cassette_tape_types"
    table_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column("name", db.Text)

    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:
        return {
            "name": self.name,
            "id": self.table_id
        }


class CassetteTapeThickness(AVTables):
    __tablename__ = "cassette_tape_thickness"
    table_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    value = db.Column("value", db.Text)
    unit = db.Column("unit", db.Text)

    def serialize(self, recurse=False) -> Mapping[str, SerializedData]:
        return {
            "value": self.value,
            "unit": self.unit,
            "id": self.table_id
        }


item_has_contacts_table = db.Table(
    "item_has_contacts",
    AVTables.metadata,
    db.Column("contact_id", db.Integer, db.ForeignKey("formats.item_id")),
    db.Column("item_id", db.Integer, db.ForeignKey("contact.contact_id"))
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


# =============================================================================


format_types = {
    "audio video": (1, AudioVideo),
    "audio": (2,),
    "video": (3,),
    "open reel": (4, OpenReel),
    "grooved disc": (5, GroovedDisc),
    "film": (6, Film),
    "audio cassette": (7, AudioCassette)
}
