from typing import Dict, Optional, List

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData

object_has_notes_table = db.Table(
    "object_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("notes.note_id")),
    db.Column("object_id", db.Integer, db.ForeignKey("object.object_id"))
)


class CollectionObject(AVTables):
    __tablename__ = "object"

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

    items = relationship("CollectionItem", backref="item_id")

    contact_id = db.Column(db.Integer, db.ForeignKey("contact.contact_id"))

    contact = relationship("Contact", foreign_keys=[contact_id])

    audio_cassettes = relationship("AudioCassette")

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:

        data: Dict[str, SerializedData] = {"object_id": self.id,
                                           "name": self.name,
                                           "barcode": self.barcode,
                                           "items": self.get_items(recurse)}

        if recurse is True:
            data["notes"] = [note.serialize() for note in self.notes]

        data["collection"] = self.get_collection(recurse)

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
                data["parent_project"] = self.project.id
            else:
                data["parent_project"] = None

        data["originals_rec_date"] = \
            self.serialize_date(self.originals_rec_date)

        data["originals_return_date"] = \
            self.serialize_date(self.originals_return_date)

        return data

    def get_collection(self, recurse: bool) -> Optional[dict]:
        if self.collection is not None:
            if recurse is True:
                return self.collection.serialize()
            return None
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
        for item in sorter(self.items):
            if recurse is True:
                item_data = item.serialize()
                del item_data['parent_object_id']
                items.append(item_data)

            else:
                items.append({
                    "item_id": item.id,
                    "name": item.name
                })
        return items
