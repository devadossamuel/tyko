from typing import Dict

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData

item_has_notes_table = db.Table(
    "item_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("notes.note_id")),
    db.Column("item_id", db.Integer, db.ForeignKey("item.item_id"))
)


class CollectionItem(AVTables):
    __tablename__ = "item"

    id = db.Column("item_id", db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)
    medusa_uuid = db.Column("medusa_uuid", db.Text)

    collection_object_id = db.Column("object_id",
                                     db.Integer,
                                     db.ForeignKey("object.object_id"),
                                     )

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
    files = relationship("InstantiationFile", backref="file_source")

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        notes = [note.serialize() for note in self.notes]
        files = []
        for file_ in self.files:
            if recurse is True:
                files.append(file_.serialize(recurse=True))
            else:
                files.append({
                    "name": file_.file_name,
                    "id": file_.file_id,
                    "generation": file_.generation

                })

        data: Dict[str, SerializedData] = {
            "item_id": self.id,
            "name": self.name,
            "files": files,
            "medusa_uuid": self.medusa_uuid,
            "obj_sequence": self.obj_sequence,
            "parent_object_id": self.collection_object_id,
            "notes": notes
        }
        try:
            data["format"] = self.format_type.serialize()
            data["format_id"] = self.format_type_id
        except AttributeError:
            data["format"] = None
            data["format_id"] = None

        return data


item_has_contacts_table = db.Table(
    "item_has_contacts",
    AVTables.metadata,
    db.Column("contact_id", db.Integer, db.ForeignKey("item.item_id")),
    db.Column("item_id", db.Integer, db.ForeignKey("contact.contact_id"))
)
