from typing import Dict

import sqlalchemy as db
from sqlalchemy.orm import relationship

from tyko.schema.avtables import AVTables, SerializedData

project_has_notes_table = db.Table(
    "project_has_notes",
    AVTables.metadata,
    db.Column("notes_id", db.Integer, db.ForeignKey("notes.note_id")),
    db.Column("project_id", db.Integer, db.ForeignKey("project.project_id"))
)


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
    status = relationship("ProjectStatus")
    status_id = db.Column(
        db.Integer, db.ForeignKey("project_status_type.project_status_id"))
    specs = db.Column("specs", db.Text)

    notes = relationship(
        "Note",
        secondary=project_has_notes_table,
        backref="project_sources"
    )

    objects = relationship(
        "CollectionObject",
        backref="object_source"
    )

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        if self.status is not None:
            status_text = self.status.serialize()['name']
        else:
            status_text = None

        data: Dict[str, SerializedData] = {
            "project_id": self.id,
            "project_code": self.project_code,
            "current_location": self.current_location,
            "status": status_text,
            "title": self.title,
        }
        notes = []

        for note in self.notes:
            notes.append(note.serialize())
        data["notes"] = notes

        if recurse is True:
            child_objects = []
            for project_object in self.objects:
                project_object_data = project_object.serialize(recurse=False)
                del project_object_data['parent_project']
                child_objects.append(project_object_data)
            data["objects"] = child_objects

        return data


class ProjectStatus(AVTables):
    __tablename__ = "project_status_type"

    id = db.Column("project_status_id",
                   db.Integer, primary_key=True, autoincrement=True)

    name = db.Column("name", db.Text)

    def serialize(self, recurse=False) -> Dict[str, SerializedData]:
        return {
            "project_status_id": self.id,
            "name": self.name
        }
