from typing import Dict, Optional, List

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData

object_has_notes_table = db.Table(
    "object_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("notes.note_id")),
    db.Column("object_id", db.Integer, db.ForeignKey("tyko_object.object_id"))
)


class CollectionObject(AVTables):
    __tablename__ = "tyko_object"

    id = db.Column(
        "object_id",
        db.Integer,
        primary_key=True,
        autoincrement=True)

    name = db.Column("name", db.Text)
    barcode = db.Column("barcode", db.Text)
    collection_id = \
        db.Column(db.Integer, db.ForeignKey("collection.collection_id"))

    collection = relationship("Collection", foreign_keys=[collection_id])

    project_id = db.Column(db.Integer, db.ForeignKey("project.project_id"))
    project = relationship("Project", foreign_keys=[project_id])
    originals_rec_date = db.Column("originals_rec_date", db.Date)
    originals_return_date = db.Column("originals_return_date", db.Date)
    notes = relationship("Note",
                         secondary=object_has_notes_table,
                         backref="object_sources"
                         )


    contact_id = db.Column(db.Integer, db.ForeignKey("contact.contact_id"))

    contact = relationship("Contact", foreign_keys=[contact_id])
    audio_cassettes = relationship("AudioCassette", back_populates="object")
    collection_items = relationship("CollectionItem", back_populates="object")
    open_reels = relationship("OpenReel", back_populates="object")
    films = relationship("Film", back_populates="object")
    audio_videos = relationship("AudioVideo", back_populates="object")
    groove_disks = relationship("GroovedDisc", back_populates="object")

    def all_items(self):
        r = self.collection_items \
            + self.audio_cassettes \
            + self.films \
            + self.audio_videos \
            + self.groove_disks \
            + self.open_reels \
            + self.collection_items
        return r

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:

        data: Dict[str, SerializedData] = {"object_id": self.id,
                                           "name": self.name,
                                           "barcode": self.barcode,
                                           "items": self.get_items(recurse)}

        if recurse is True:
            data["notes"] = [note.serialize() for note in self.notes]
        else:
            data['notes'] = [{"note_id": note.id} for note in self.notes]
        if recurse:
            data["collection"] = self.get_collection(True)
        else:
            data["collection_id"] = self.get_collection(False)

        if self.contact is not None:
            contact = self.contact.serialize()
        else:
            contact = None
        data["contact"] = contact

        if recurse is True:
            if self.project is not None:
                data["project"] = self.project.serialize(recurse=False)
            else:
                data["project"] = None
        else:
            if self.project is not None:
                data["parent_project_id"] = self.project.id
            else:
                data["parent_project_id"] = None

        data["originals_rec_date"] = \
            self.serialize_date(self.originals_rec_date)

        data["originals_return_date"] = \
            self.serialize_date(self.originals_return_date)

        return data

    def get_collection(self, recurse: bool) -> Optional[dict]:
        if self.collection is not None:
            if recurse is True:
                return self.collection.serialize()
            return self.collection.id
        return None

    def get_items(self, recurse):
        def sorter(collection_items):
            no_sequence = set()
            has_sequence = set()
            for collection_item in collection_items:
                if collection_item.obj_sequence is None:
                    no_sequence.add(collection_item)
                else:
                    has_sequence.add(collection_item)

            resulting_sorted_list = \
                sorted(list(has_sequence), key=lambda x: x.obj_sequence)

            resulting_sorted_list += list(no_sequence)
            return resulting_sorted_list

        items: List[SerializedData] = []

        for item in sorter(self.all_items()):
            if recurse is True:
                item_data = item.serialize()
                del item_data['parent_object_id']
                items.append(item_data)

            else:
                items.append({
                    "item_id": item.table_id,
                    "name": item.name,
                    "format":
                        item.format_type.serialize()
                        if item.format_type is not None else None
                })
        return items
