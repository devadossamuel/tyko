from typing import Dict

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData


class Note(AVTables):
    __tablename__ = "notes"

    id = db.Column("note_id", db.Integer, primary_key=True, autoincrement=True)
    text = db.Column("text", db.Text, nullable=False)

    note_type_id = db.Column(
        db.Integer, db.ForeignKey("note_types.note_types_id"))

    note_type = relationship("NoteTypes", foreign_keys=[note_type_id])

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        data: Dict[str, SerializedData] = {
            "note_id": self.id,
            "text": self.text,
            "note_type_id": self.note_type_id,

        }
        if self.note_type is not None:
            data["note_type"] = self.note_type.name
        return data


class NoteTypes(AVTables):
    __tablename__ = "note_types"
    id = db.Column(
        "note_types_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("type_name", db.Text)

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "note_types_id": self.id,
            "name": self.name
        }

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
note_types = {
    "Inspection": (1, ),
    "Playback": (2, ),
    "Project": (3, ),
    "Other": (4, ),
}
