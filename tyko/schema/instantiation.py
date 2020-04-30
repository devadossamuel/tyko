from typing import Dict

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData


class InstantiationFile(AVTables):
    __tablename__ = "instantiation_files"

    file_id = db.Column(
        "file_id", db.Integer, primary_key=True, autoincrement=True)

    file_name = db.Column("file_name", db.Text, nullable=False)

    source = db.Column("source", db.Text,
                       default="University of Illinois library",
                       nullable=True)

    generation = db.Column("generation", db.Text)

    filesize = db.Column("filesize", db.Integer)
    filesize_unit = db.Column("filesize_unit", db.Text)
    item_id = db.Column(db.Integer, db.ForeignKey("formats.item_id"))
    notes = relationship(
        "FileNotes",
        backref="file_note_source"
    )
    annotations = relationship(
        "FileAnnotation",
        backref="file_annotation_source"
    )

    def _create_notes(self, resolve_data: bool):
        for file_note in self.notes:
            if resolve_data:
                yield file_note.serialize()
            else:
                yield {
                    "note_id": file_note.id
                }

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "id": self.file_id,
            "file_name": self.file_name,
            "generation": self.generation,
            "notes": list(self._create_notes(recurse)),
            "annotations": list(self._create_annotations(recurse))
        }

    def _create_annotations(self, resolve_data: bool):
        for annotation in self.annotations:
            if resolve_data:
                yield annotation.serialize()
            else:
                yield {
                    "annotation_id": annotation.id
                }


class FileNotes(AVTables):
    __tablename__ = "file_notes"
    id = db.Column(
        "note_id", db.Integer, primary_key=True, autoincrement=True)
    message = db.Column("message", db.Text, nullable=False)
    file_id = db.Column(db.Integer,
                        db.ForeignKey("instantiation_files.file_id"))

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "id": self.id,
            "message": self.message,
            "file_id": self.file_id,
        }


class FileAnnotationType(AVTables):

    __tablename__ = "file_annotation_types"
    id = db.Column(
        "type_id", db.Integer, primary_key=True, autoincrement=True)
    name = db.Column("name", db.Text, nullable=False)
    active = db.Column("active", db.Boolean, nullable=False, default=True)

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "type_id": self.id,
            "name": self.name,
            "active": self.active
        }


class FileAnnotation(AVTables):
    __tablename__ = "file_annotations"

    id = db.Column(
        "annotation_id", db.Integer, primary_key=True, autoincrement=True)
    file_id = db.Column(db.Integer,
                        db.ForeignKey("instantiation_files.file_id"))

    type_id = db.Column(db.Integer,
                        db.ForeignKey("file_annotation_types.type_id"))

    annotation_type = relationship("FileAnnotationType",
                                   foreign_keys=[type_id])

    annotation_content = db.Column("content", db.Text, nullable=False)

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "id": self.id,
            "type": self.annotation_type.serialize(recurse),
            "content": self.annotation_content,
            "file_id": self.file_id
        }
