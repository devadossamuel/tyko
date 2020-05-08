# pylint: disable=redefined-builtin, invalid-name
import abc
from abc import ABC
from datetime import datetime
from typing import List, Optional, Iterator

import sqlalchemy
from sqlalchemy.sql.expression import true
from sqlalchemy import orm

from .schema.collection import Collection
from .schema import formats
from .schema.instantiation import FileNotes, InstantiationFile, \
    FileAnnotation, FileAnnotationType
from .schema import CollectionItem
from .schema.notes import Note, NoteTypes
from .schema.objects import CollectionObject
from .schema.projects import Project, ProjectStatus
from .schema.formats import CassetteType, CassetteTapeType, \
    CassetteTapeThickness, AudioCassette, AVFormat
from .exceptions import DataError
from . import database
from tyko import utils

DATE_FORMAT = '%Y-%m-%d'


class AbsDataProviderConnector(metaclass=abc.ABCMeta):

    def __init__(self, session_maker) -> None:
        self.session_maker = session_maker

    @abc.abstractmethod
    def get(self, id=None, serialize=False):
        """Perform the get command"""

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        """Create a new entity"""

    @abc.abstractmethod
    def update(self, id, changed_data):
        """Update an existing entity"""

    @abc.abstractmethod
    def delete(self, id):
        """Delete an existing entity"""


class AbsNotesConnector(AbsDataProviderConnector, ABC):  # noqa: E501 pylint: disable=abstract-method
    @staticmethod
    def get_note_type(session, note_type_id):
        note_types = session.query(NoteTypes) \
            .filter(NoteTypes.id == note_type_id) \
            .all()

        if len(note_types) == 0:
            raise ValueError("Not a valid note_type")
        return note_types[0]

    @classmethod
    def new_note(cls, session, text: str, note_type_id: int):
        new_note = Note(
            text=text,
            note_type=cls.get_note_type(session, note_type_id)
        )
        session.add(new_note)
        return new_note


class ProjectDataConnector(AbsNotesConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_projects = session.query(Project)\
                .filter(Project.id == id)\
                .all()

        else:
            all_projects = session.query(Project).all()

        if serialize is True:
            serialized_projects = []
            for project in all_projects:
                serialized_project = project.serialize(recurse=True)
                serialized_projects.append(serialized_project)

            all_projects = serialized_projects
        session.close()

        if id is not None:
            return all_projects[0]

        return all_projects

    def get_all_project_status(self) -> List[ProjectStatus]:
        """Get the list of all possible statuses that a project can be

        Returns:
            All valid status types for projects

        """
        session = self.session_maker()
        try:
            return session.query(ProjectStatus).all()
        finally:
            session.close()

    def get_project_status_by_name(self, name: str,
                                   create_if_not_exists: bool = False
                                   ) -> ProjectStatus:
        """ Check if an existing status exists and if so, return that, if not
        and create_if_not_exists is false throw an DataError exception

        Args:
            name:
            create_if_not_exists:
        """
        session = self.session_maker()
        try:
            names = session.query(ProjectStatus)\
                .filter(ProjectStatus.name == name).all()

            if len(names) > 1:
                raise DataError(
                    "Database contained multiple matches for {}".format(name))
            if len(names) == 0:
                if create_if_not_exists is True:
                    new_project_status = ProjectStatus(name=name)
                    session.add(new_project_status)
                    return new_project_status

                if create_if_not_exists is False:
                    raise DataError("No valid project status")

            return names[0]
        finally:
            session.close()

    def create(self, *args, **kwargs):
        title = kwargs["title"]
        project_code = kwargs.get("project_code")
        current_location = kwargs.get("current_location")
        status = kwargs.get("status")
        specs = kwargs.get("specs")
        session = self.session_maker()

        try:
            new_project = Project(
                title=title,
                project_code=project_code,
                current_location=current_location,
                specs=specs
            )
            if status is not None:
                project_status = self.get_project_status_by_name(status)
                new_project.status = project_status

            session.add(new_project)
            session.flush()
            new_project_id = new_project.id
            session.commit()
            return new_project_id
        finally:
            session.close()

    def include_note(self, project_id, note_type_id, note_text):
        new_project_data = None
        session = self.session_maker()
        try:
            project = self._get_project(session, project_id)

            project.notes.append(
                self.new_note(session, note_text, note_type_id))

            session.commit()
            new_project = \
                session.query(Project).filter(Project.id == project_id).one()

            new_project_data = new_project.serialize()
        finally:
            session.close()
        return new_project_data

    def update_note(self, project_id, note_id, changed_data):
        session = self.session_maker()
        try:

            project = self._get_project(session, project_id)

            note = self._find_note(project, note_id)
            if "text" in changed_data:
                note.text = changed_data['text']
            if "note_type_id" in changed_data:

                note_type = session.query(NoteTypes).filter(
                    NoteTypes.id == changed_data['note_type_id']).one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_project = \
                session.query(Project).filter(Project.id == project_id).one()

            return new_project.serialize()
        finally:
            session.close()

    @staticmethod
    def _find_note(project, note_id):
        for note in project.notes:
            if note.id == note_id:
                return note
        raise ValueError("no matching note for project")

    def get_project(self, id=None, serialize=False):

        return self.get(id, serialize)

    def update(self, id, changed_data):
        updated_project = None
        project = self.get_project(id)

        if project:
            if "title" in changed_data:
                project.title = changed_data['title']

            if "current_location" in changed_data:
                project.current_location = changed_data['current_location']

            if "project_code" in changed_data:
                project.project_code = changed_data['project_code']

            if "status" in changed_data:
                if isinstance(changed_data['status'], str):
                    project.status = \
                        self.get_project_status_by_name(changed_data['status'])
                else:
                    project.status = changed_data['status']

            session = self.session_maker()
            session.add(project)
            session.commit()
            session.close()

            updated_project = session.query(Project)\
                .filter(Project.id == id)\
                .one()

        return updated_project.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()
            items_deleted = session.query(Project)\
                .filter(Project.id == id)\
                .delete()

            session.commit()
            session.close()
            return items_deleted > 0
        return False

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(NoteTypes).all()
        finally:
            session.close()

    def remove_note(self, project_id, note_id):
        session = self.session_maker()
        try:
            project = self._get_project(session, project_id)

            if len(project.notes) == 0:
                raise DataError(
                    "Project with ID: {} has no notes".format(project_id))

            # Find note that matches the note ID
            for note in project.notes:
                if note.id == note_id:
                    project.notes.remove(note)
                    break
            else:
                raise DataError(
                    message="Project id {} contains no note with an"
                            " id {}".format(project_id, note_id),
                    status_code=404
                )

            session.commit()
            return session.query(Project) \
                .filter(Project.id == project_id) \
                .one().serialize()
        finally:
            session.close()

    def add_object(self, project_id, data):
        session = self.session_maker()
        try:

            project = self._get_project(session, project_id)
            object_connector = ObjectDataConnector(self.session_maker)
            new_data = dict()
            for k, v in data.items():
                if isinstance(v, str) and v.strip() == "":
                    continue
                new_data[k] = v

            new_object_id = object_connector.create(**new_data)
            project.objects.append(object_connector.get(id=new_object_id))
            session.commit()
            return object_connector.get(id=new_object_id, serialize=True)
        finally:
            session.close()

    def remove_object(self, project_id, object_id):
        session = self.session_maker()
        try:
            project = self._get_project(session=session, project_id=project_id)
            for child_object in project.objects:
                if child_object.id == object_id:
                    project.objects.remove(child_object)
                    session.commit()
                    return session.query(Project) \
                        .filter(Project.id == project_id) \
                        .one().serialize()
            raise DataError(
                message="Project id {} contains no object with an"
                        " id {}".format(project_id, object_id),
                status_code=404
            )
        finally:
            session.close()

    @staticmethod
    def _get_project(session, project_id):
        projects = session.query(Project).filter(
            Project.id == project_id).all()

        if len(projects) == 0:
            raise DataError(
                message="Unable to locate project "
                        "with ID: {}".format(project_id),
                status_code=404
            )

        if len(projects) > 1:
            raise DataError(
                message="Found multiple projects with ID: {}".format(
                    project_id))

        return projects[0]


class ObjectDataConnector(AbsNotesConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                all_collection_object = \
                    session.query(CollectionObject).filter(
                        CollectionObject.id == id).all()
                if len(all_collection_object) == 0:
                    raise DataError(
                        message="Unable to find object: {}".format(id))
            else:
                all_collection_object = \
                    session.query(CollectionObject).filter(
                        CollectionObject.project is not None).all()
        except sqlalchemy.exc.DatabaseError as e:
            raise DataError(message="Unable to find object: {}".format(e))

        if serialize:
            serialized_all_collection_object = []
            for collection_object in all_collection_object:
                serialized_all_collection_object.append(
                    collection_object.serialize(False)
                )

            all_collection_object = serialized_all_collection_object
        session.close()

        if id is not None:
            return all_collection_object[0]

        return all_collection_object

    def create(self, *args, **kwargs):
        name = kwargs["name"]
        data = self.get_data(kwargs)
        new_object = CollectionObject(name=name)
        if 'originals_rec_date' in data:
            new_object.originals_rec_date = data['originals_rec_date']

        barcode = kwargs.get("barcode")
        if barcode is not None:
            new_object.barcode = barcode
        session = self.session_maker()
        if "collection_id" in kwargs and kwargs['collection_id'] is not None:
            collection = session.query(Collection).filter(
                Collection.id == kwargs['collection_id']).one()

            if collection is None:
                raise ValueError("Not a valid collection")
            new_object.collection = collection
        session.add(new_object)
        session.commit()
        object_id = new_object.id
        session.close()

        return object_id

    def update(self, id, changed_data):
        collection_object = self.get(id, serialize=False)

        session = self.session_maker()
        try:
            if collection_object:

                if "name" in changed_data:
                    collection_object.name = changed_data['name']

                if "barcode" in changed_data:
                    collection_object.barcode = changed_data['barcode']

                if "collection_id" in changed_data:
                    collection = session.query(Collection)\
                        .filter(Collection.id ==
                                changed_data['collection_id'])\
                        .one()

                    collection_object.collection = collection

                if 'originals_rec_date' in changed_data:
                    collection_object.originals_rec_date = \
                        datetime.strptime(
                            changed_data['originals_rec_date'],
                            DATE_FORMAT
                        )
                if 'originals_return_date' in changed_data:
                    collection_object.originals_return_date = \
                        datetime.strptime(
                            changed_data['originals_return_date'],
                            DATE_FORMAT
                        )

                session.add(collection_object)
                session.commit()

                updated_object = session.query(CollectionObject)\
                    .filter(CollectionObject.id == id)\
                    .one()
                return updated_object.serialize()

        finally:
            session.close()

    def delete(self, id):
        if id:
            session = self.session_maker()

            items_deleted = session.query(CollectionObject)\
                .filter(CollectionObject.id == id).delete()

            success = items_deleted > 0
            session.commit()
            return success
        return False

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(NoteTypes).all()
        finally:
            session.close()

    def add_note(self, object_id: int,
                 note_type_id: int, note_text) -> None:

        session = self.session_maker()
        try:
            collection_object = self._get_object(object_id, session=session)

            collection_object.notes.append(
                self.new_note(session, note_text, note_type_id)
            )
            session.commit()

            new_object = session.query(CollectionObject) \
                .filter(CollectionObject.id == object_id) \
                .one()

            return new_object.serialize()

        finally:
            session.close()

    def remove_note(self, object_id, note_id):
        session = self.session_maker()
        try:
            objects = session.query(CollectionObject)\
                .filter(CollectionObject.id == object_id)\
                .all()

            if len(objects) == 0:
                raise DataError(
                    message="Unable to locate collection object "
                            "with ID: {}".format(object_id),
                    status_code=404
                )

            if len(objects) > 1:
                raise DataError(
                    message="Found multiple objects with ID: {}".format(
                        object_id))

            collection_object = objects[0]

            if len(collection_object.notes) == 0:
                raise DataError(
                    "Object with ID: {} has no notes".format(object_id))

            # Find note that matches the note ID
            for note in collection_object.notes:
                if note.id == note_id:
                    collection_object.notes.remove(note)
                    break
            else:
                raise DataError(
                    message="Collection id {} contains no note with an"
                            " id {}".format(object_id, note_id),
                    status_code=404
                )

            session.commit()
            return session.query(CollectionObject) \
                .filter(CollectionObject.id == object_id) \
                .one()\
                .serialize()
        finally:
            session.close()

    def update_note(self, object_id, note_id, changed_data):
        session = self.session_maker()
        try:
            collection_object = self._get_object(object_id, session=session)

            note = self._find_note(collection_object, note_id)
            if "text" in changed_data:
                note.text = changed_data['text']
            if "note_type_id" in changed_data:

                note_type = session.query(NoteTypes)\
                    .filter(NoteTypes.id == changed_data['note_type_id']).one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_object = \
                session.query(CollectionObject).filter(
                    CollectionObject.id == object_id).one()

            return new_object.serialize()
        finally:
            session.close()

    @staticmethod
    def _get_object(object_id, session):
        collection_object = session.query(CollectionObject) \
            .filter(CollectionObject.id == object_id) \
            .all()
        if len(collection_object) == 0:
            raise ValueError("Not a valid object")
        collection_object = collection_object[0]
        return collection_object

    @staticmethod
    def _find_note(collection_object, note_id):
        for note in collection_object.notes:
            if note.id == note_id:
                return note
        raise ValueError("No matching note for object")

    def add_item(self, object_id, data):
        session = self.session_maker()
        try:
            matching_object = self._get_object(object_id, session)
            item_connector = ItemDataConnector(self.session_maker)
            new_item_id = item_connector.create(**data)['item_id']

            matching_object.collection_items.append(
                item_connector.get(id=new_item_id)
            )

            session.commit()
            return item_connector.get(id=new_item_id, serialize=True)
        finally:
            session.close()

    def remove_item(self, object_id, item_id):
        session = self.session_maker()
        try:
            matching_item = self._find_item(item_id, session)

            matching_object = self._find_object(
                object_id=object_id,
                session=session
            )
            matching_list = self._find_matching_section(matching_item,
                                                        matching_object)
            if matching_list is not None and matching_item in matching_list:
                matching_list.remove(matching_item)

            session.commit()
            return session.query(CollectionObject) \
                .filter(CollectionObject.id == object_id) \
                .one().serialize()

        finally:
            session.close()

    @staticmethod
    def _find_item(item_id, session) -> CollectionItem:
        matching_items = \
            session.query(AVFormat).filter(
                AVFormat.table_id == item_id).all()

        if len(matching_items) == 0:
            raise DataError(
                message="No items found with ID: {}".format(
                    item_id))

        if len(matching_items) > 1:
            raise DataError(
                message="Found multiple items with ID: {}".format(
                    item_id))
        return matching_items[0]

    @staticmethod
    def _find_object(object_id, session) -> CollectionObject:
        matching_objects = \
            session.query(CollectionObject).filter(
                CollectionObject.id == object_id).all()

        if len(matching_objects) == 0:
            raise DataError(
                message="No object found with ID: {}".format(
                    object_id))

        if len(matching_objects) > 1:
            raise DataError(
                message="Found multiple objects with ID: {}".format(
                    object_id))
        return matching_objects[0]

    @classmethod
    def get_data(cls, data):
        new_data = data.copy()
        if 'originals_rec_date' in data and \
                data['originals_rec_date'].strip() != "":

            new_data['originals_rec_date'] = \
                datetime.strptime(data['originals_rec_date'], '%Y-%m-%d')

        return new_data


    @staticmethod
    def _find_matching_section(matching_item,
                               matching_object) -> Optional[List[AVFormat]]:
        subtypes = [
            'audio_cassettes',
            'audio_videos',
            'collection_items',
            'films',
            'grooved_disc',
            'open_reels',
        ]

        for subtype_name in subtypes:
            subtype = getattr(matching_object, subtype_name)
            if matching_item in subtype:
                return subtype
        return None


class FileNotesDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                all_notes = \
                    session.query(FileNotes).filter(FileNotes.id == id).all()
            else:
                all_notes = \
                    session.query(CollectionObject).filter(
                        CollectionObject.project is not None).all()

            if serialize:
                serialized_notes = []
                for notes in all_notes:
                    serialized_notes.append(
                        notes.serialize(True)
                    )

                all_notes = serialized_notes
            if id is not None:
                return all_notes[0]

            return all_notes
        finally:
            session.close()

    def create(self, *args, **kwargs):
        session = self.session_maker()
        try:
            new_note = FileNotes(file_id=kwargs['file_id'],
                                 message=kwargs['message'])

            session.add(new_note)
            session.commit()
            return new_note.serialize()
        finally:
            session.close()

    def update(self, id, changed_data):
        session = self.session_maker()
        try:
            note_record = session.query(FileNotes) \
                .filter(FileNotes.id == id).one()

            if "message" in changed_data:
                note_record.message = changed_data['message']
            session.commit()
            return note_record.serialize()
        finally:
            session.close()

    def delete(self, id):
        session = self.session_maker()
        try:
            items_deleted = session.query(FileNotes)\
                .filter(FileNotes.id == id).delete()

            success = items_deleted > 0
            session.commit()
            return success

        finally:
            session.close()


class FilesDataConnector(AbsDataProviderConnector):
    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            matching_file = session.query(InstantiationFile)\
                .filter(InstantiationFile.file_id == id).one()

            if serialize is True:
                res = matching_file.serialize(recurse=True)
                return res

            return matching_file
        finally:
            session.close()

    def create(self, item_id, *args, **kwargs):
        name = kwargs['file_name']
        generation = kwargs['generation']
        session = self.session_maker()
        try:
            matching_item = session.query(CollectionItem)\
                .filter(CollectionItem.table_id == item_id).one()

            new_file = InstantiationFile(file_name=name)

            if generation is not None:
                new_file.generation = generation

            matching_item.files.append(new_file)
            session.flush()
            session.commit()
            return new_file.serialize()
        finally:
            session.close()

    def update(self, id, changed_data):
        session = self.session_maker()
        try:
            matching_file = session.query(InstantiationFile) \
                .filter(InstantiationFile.file_id == id).one()

            if "file_name" in changed_data:
                matching_file.file_name = changed_data['file_name']
            if "generation" in changed_data:
                matching_file.generation = changed_data['generation']
            session.commit()
            return matching_file.serialize()
        finally:
            session.close()

    def delete(self, id: int):
        session = self.session_maker()
        try:
            items_deleted = session.query(InstantiationFile)\
                .filter(InstantiationFile.file_id == id).delete()

            session.commit()
            return items_deleted > 0
        finally:
            session.close()

    def remove(self, item_id: int, file_id: int):
        session = self.session_maker()
        try:
            item = session.query(CollectionItem)\
                .filter(CollectionItem.table_id == item_id).one()

            for f in item.files:
                if f.file_id == file_id:
                    item.files.remove(f)
                    return True
            raise ValueError(f"Item {item_id} does not have a file with an"
                             f" id of {file_id}")
        finally:
            session.close()


class ItemDataConnector(AbsNotesConnector):

    @staticmethod
    def _get_all(session):
        res = list(session.query(formats.Film).all()) + \
              list(session.query(formats.AudioCassette).all()) + \
              list(session.query(formats.AudioVideo).all()) + \
              list(session.query(formats.GroovedDisc).all()) + \
              list(session.query(formats.OpenReel).all()) + \
              list(session.query(formats.CollectionItem).all())
        if len(res) == 0:
            res = list(session.query(formats.AVFormat)
                       .all())
        return res

    @staticmethod
    def _iterall(session) -> Iterator[formats.AVFormat]:
        yield from session.query(formats.Film).all()
        yield from session.query(formats.AudioCassette).all()
        yield from session.query(formats.AudioVideo).all()
        yield from session.query(formats.GroovedDisc).all()
        yield from session.query(formats.OpenReel).all()
        yield from session.query(formats.CollectionItem).all()

    @staticmethod
    def _get_one(session, table_id: int):

        res = list(session.query(formats.Film)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all()) + \
              list(session.query(formats.AudioCassette)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all()) + \
              list(session.query(formats.AudioVideo)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all()) + \
              list(session.query(formats.GroovedDisc)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all()) + \
              list(session.query(formats.OpenReel)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all()) + \
              list(session.query(formats.CollectionItem)
                   .filter(formats.AVFormat.table_id == table_id)
                   .all())
        if len(res) == 0:
            res = list(session.query(formats.AVFormat)
                       .filter(formats.AVFormat.table_id == table_id)
                       .all())
        return res

    @staticmethod
    def _serialize(items):
        serialized_all_collection_item = []
        for collection_item in items:
            serialized_all_collection_item.append(
                collection_item.serialize(true))

        return serialized_all_collection_item

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                all_collection_item = self._get_one(session, id)
            else:
                all_collection_item = self._get_all(session)

            if serialize:
                all_collection_item = self._serialize(all_collection_item)

            if id is not None:
                return all_collection_item[0]

            return all_collection_item
        finally:
            session.close()

    def add_note(self, item_id: int, note_text: str, note_type_id: int):
        session = self.session_maker()
        try:
            collection_item = self._get_item(item_id, session=session)

            collection_item.notes.append(
                self.new_note(session, note_text, note_type_id)
            )
            session.commit()
            return self._get_item(item_id, session=session).serialize()


        finally:
            session.close()

    def create(self, *args, **kwargs):
        session = self.session_maker()
        name = kwargs["name"]
        format_id = int(kwargs["format_id"])
        try:
            format_type = session.query(formats.FormatTypes)\
                .filter(formats.FormatTypes.id == format_id).one()

            new_item = CollectionItem(
                name=name,
                format_type=format_type
            )

            for instance_file in kwargs.get("files", []):
                new_file = InstantiationFile(file_name=instance_file['name'])

                new_item.files.append(new_file)
            # new_item.files.append(f)
            session.add(new_item)
            session.commit()
            return new_item.serialize()
        finally:
            session.close()

    def update(self, id, changed_data):
        updated_item = None
        item = self.get_item(id)
        if item:
            if "name" in changed_data:
                item.name = changed_data['name']

            if "obj_sequence" in changed_data:
                item.obj_sequence = int(changed_data["obj_sequence"])

            session = self.session_maker()

            session.add(item)
            session.commit()
            updated_item = session.query(CollectionItem)\
                .filter(CollectionItem.table_id == id)\
                .one()
        return updated_item.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()

            items_deleted = session.query(CollectionItem)\
                .filter(CollectionItem.table_id == id).delete()

            success = items_deleted > 0
            session.commit()
            return success
        return False

    def get_item(self, id=None, serialize=False):
        return self.get(id, serialize)

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(NoteTypes).all()
        finally:
            session.close()

    @staticmethod
    def _get_item(item_id, session):
        for i in ItemDataConnector._iterall(session):
            if i.table_id == item_id:
                return i
        raise ValueError("Not a valid item")

    def remove_note(self, item_id, note_id):
        session = self.session_maker()
        try:

            item = self._get_item(item_id, session)

            if len(item.notes) == 0:
                raise DataError(
                    "Item with ID: {} has no notes".format(item_id)
                )

            # Find note that matches the note ID
            for note in item.notes:
                if note.id == note_id:
                    item.notes.remove(note)
                    break
            else:
                raise DataError(
                    message="Item id {} contains no note with an"
                            " id {}".format(item_id, note_id),
                    status_code=404
                )

            session.commit()
            return self._get_item(item_id, session).serialize()
        finally:
            session.close()

    def update_note(self, item_id, note_id, changed_data):
        session = self.session_maker()
        try:
            item = self._get_item(item_id, session=session)

            note = self._find_note(item, note_id)
            if "text" in changed_data:
                note.text = changed_data['text']
            if "note_type_id" in changed_data:

                note_type = session.query(NoteTypes)\
                    .filter(NoteTypes.id == changed_data['note_type_id'])\
                    .one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_item = \
                session.query(CollectionItem).filter(
                    CollectionItem.table_id == item_id).one()

            return new_item.serialize()

        finally:
            session.close()

    @staticmethod
    def _find_note(item, note_id):
        for note in item.notes:
            if note.id == note_id:
                return note
        raise ValueError("No matching note for item")


class AudioCassetteDataConnector(ItemDataConnector):

    def create(self, *args, **kwargs):
        new_base_item = super().create(*args, **kwargs)
        session = self.session_maker()
        try:
            format_details = kwargs['format_details']
            base_object = session.query(CollectionObject)\
                .filter(CollectionObject.id == kwargs['object_id'])\
                .one()

            format_type_id = int(format_details['format_type_id'])

            format_type = session.query(CassetteType)\
                .filter(CassetteType.table_id == format_type_id)\
                .one()

            new_cassette = AudioCassette(
                name=new_base_item['name'],
                cassette_type=format_type,
                format_type_id=new_base_item['format_id']
            )

            self._add_optional_args(new_cassette, **format_details)

            base_object.audio_cassettes.append(new_cassette)
            session.add(new_cassette)
            session.commit()
            i = new_cassette.serialize()
            return i
        finally:
            session.close()

    def _add_optional_args(self, new_cassette, **params):
        tape_thickness_id = params.get('Tape Thickness')
        if tape_thickness_id is not None:
            new_cassette.tape_thickness_id = int(tape_thickness_id)

        date_inspected = params.get('DateInspected')
        if date_inspected is not None and date_inspected.strip() != "":
            new_cassette.inspection_date = \
                utils.create_precision_datetime(date_inspected)

        tape_type_id = params.get('Tape Type')
        if tape_type_id is not None:
            new_cassette.tape_type_id = int(tape_type_id)

        date_recorded = params.get("date_recorded")
        if date_recorded is not None:
            date_prec = utils.identify_precision(date_recorded)

            new_cassette.recording_date = utils.create_precision_datetime(
                date=date_recorded,
                precision=date_prec
            )
            new_cassette.recording_date_precision = date_prec


class CollectionDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_collections = session.query(Collection)\
                .filter(Collection.id == id)\
                .all()
        else:
            all_collections = \
                session.query(Collection).all()

        if serialize:
            serialized_collections = []
            for collection in all_collections:
                serialized_collections.append(collection.serialize())
            all_collections = serialized_collections

        session.close()

        if id is not None:
            return all_collections[0]

        return all_collections

    def create(self, *args, **kwargs):
        collection_name = kwargs.get("collection_name")
        department = kwargs.get("department")
        record_series = kwargs.get("record_series")

        new_collection = Collection(
            collection_name=collection_name,
            department=department,
            record_series=record_series

        )

        session = self.session_maker()
        session.add(new_collection)
        session.commit()
        new_collection_id = new_collection.id
        session.close()

        return new_collection_id

    def update(self, id, changed_data):
        updated_collection = None
        collection = self.get(id, serialize=False)

        if collection:
            if "collection_name" in changed_data:
                collection.collection_name = changed_data["collection_name"]

            if "department" in changed_data:
                collection.department = changed_data["department"]

            if "record_series" in changed_data:
                collection.record_series = changed_data["record_series"]

            session = self.session_maker()

            session.add(collection)
            session.commit()
            updated_collection = session.query(Collection)\
                .filter(Collection.id == id)\
                .one()

        return updated_collection.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()

            collections_deleted = session.query(Collection)\
                .filter(Collection.id == id).delete()

            success = collections_deleted > 0
            session.commit()
            return success
        return False


class NotesDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_notes = session.query(Note) \
                .filter(Note.id == id) \
                .all()
        else:
            all_notes = \
                session.query(Note).all()

        if serialize:
            serialized_notes = []
            for note in all_notes:
                note_data = note.serialize()

                projects_mentioned = [
                    project.id for project in note.project_sources
                ]
                note_data['parent_project_ids'] = projects_mentioned

                objects_mentioned = [
                    obj.id for obj in note.object_sources
                ]
                note_data['parent_object_ids'] = objects_mentioned

                items_mentioned = [
                    obj.id for obj in note.item_source
                ]
                note_data['parent_item_ids'] = items_mentioned

                serialized_notes.append(note_data)
            all_notes = serialized_notes

        session.close()

        if id is not None:
            return all_notes[0]

        return all_notes

    def create(self, *args, **kwargs):
        note_types_id = kwargs.get("note_types_id")
        text = kwargs.get("text")

        new_note = Note(
            text=text,
            note_type_id=note_types_id
        )

        session = self.session_maker()
        session.add(new_note)
        session.commit()
        new_note_id = new_note.id
        session.close()
        return new_note_id

    def update(self, id, changed_data):
        updated_note = None
        note = self.get(id, serialize=False)

        if note:
            session = self.session_maker()
            if "text" in changed_data:
                note.text = changed_data['text']

            if 'note_type_id' in changed_data:
                note_types = session.query(NoteTypes)\
                    .filter(NoteTypes.id == changed_data['note_type_id'])

                note_type = note_types.one()
                note.note_type = note_type

            session.add(note)
            session.commit()
            session.close()

            updated_note = session.query(Note) \
                .filter(Note.id == id) \
                .one()
        return updated_note.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()
            items_deleted = session.query(Note) \
                .filter(Note.id == id) \
                .delete()

            session.commit()
            session.close()
            return items_deleted > 0
        return False


class DataProvider:
    def __init__(self, engine):
        self.engine = engine
        self.db_engine = engine
        # self.init_database()
        self.db_session_maker = orm.sessionmaker(bind=self.db_engine)

    def init_database(self):
        database.init_database(self.engine)

    def get_formats(self, id=None, serialize=False):
        try:
            session = self.db_session_maker()

            if id:
                all_formats = session.query(formats.FormatTypes)\
                    .filter(formats.FormatTypes.id == id)\
                    .all()
            else:
                all_formats = session.query(formats.FormatTypes).all()
            session.close()

        except sqlalchemy.exc.DatabaseError as e:
            raise DataError("Enable to get all format. Reason: {}".format(e))

        if serialize:
            return [format_.serialize() for format_ in all_formats]

        return all_formats


def get_schema_version(db_engine: sqlalchemy.engine.Engine) -> Optional[str]:
    """Get the alembic_version version of a given database.

    Args:
        db_engine:

    Returns:
        Returns a version if exists but returns None is the alembic_version is
        empty.

    """
    results = db_engine.execute("SELECT * FROM alembic_version").first()
    if results is None:
        return None
    return results.version_num


class FileAnnotationsConnector(AbsDataProviderConnector):
    def get_single_annotations(self, annotation_id, serialize):
        session = self.session_maker()
        try:
            annotation = session.query(FileAnnotation)\
                .filter(FileAnnotation.id == annotation_id)\
                .one()
            if serialize is True:
                return annotation.serialize()
            return annotation
        finally:
            session.close()

    def get_all_annotations(self, serialize):
        session = self.session_maker()
        try:
            annotations = []

            for annotation in session.query(FileAnnotationType)\
                    .filter(FileAnnotationType.active == true()):

                if serialize:
                    annotations.append(annotation.serialize())
                else:
                    annotations.append(annotation)
            return annotations
        finally:
            session.close()

    def get(self, id=None, serialize=False):
        if id is None:
            return self.get_all_annotations(serialize)
        return self.get_single_annotations(id, serialize)

    def create(self, *args, **kwargs):
        file_id = kwargs['file_id']
        content = kwargs['content']
        annotation_type_id = kwargs['annotation_type_id']
        session = self.session_maker()
        try:
            new_data = FileAnnotation(file_id=file_id,
                                      annotation_content=content,
                                      type_id=annotation_type_id)

            session.add(new_data)
            session.flush()
            session.refresh(new_data)
            annotation_id = new_data.id
            session.commit()
            return annotation_id
        finally:
            session.close()

    def update(self, id, changed_data):
        session = self.session_maker()
        try:
            annotation = \
                session.query(FileAnnotation)\
                .filter(FileAnnotation.id == id)\
                .one()

            if "content" in changed_data:
                annotation.annotation_content = changed_data['content']
            if "type_id" in changed_data:
                annotation.type_id = changed_data['type_id']
            session.commit()
            return annotation.serialize()
        finally:
            session.close()

    def delete(self, id):
        session = self.session_maker()
        try:
            items_deleted = session.query(FileAnnotation)\
                .filter(FileAnnotation.id == id)\
                .delete()
            session.commit()
            session.close()
            return items_deleted > 0
        finally:
            session.close()


class FileAnnotationTypeConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        # TODO: FileAnnotationTypeConnector.get()
        pass

    def create(self, *args, **kwargs):
        annotation_message = kwargs['text']
        session = self.session_maker()
        try:
            new_annotation_type = FileAnnotationType(
                name=annotation_message,
                active=True
            )

            session.add(new_annotation_type)
            session.flush()
            session.refresh(new_annotation_type)
            session.commit()
            return new_annotation_type.serialize()

        finally:
            session.close()

    def update(self, id, changed_data):
        # TODO: FileAnnotationTypeConnector.update()
        pass

    def delete(self, id):
        """
        Sets the annotation type to inactive, not really deleting it.
        Args:
            id:

        Returns:
            bool: true if successful

        """
        session = self.session_maker()
        try:
            annotation_type = session.query(FileAnnotationType) \
                .filter(FileAnnotationType.id == id).one()

            annotation_type.active = False
            session.commit()
            return True
        finally:
            session.close()


class CassetteTypeConnector(AbsDataProviderConnector):
    table = CassetteType

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                cassette_types = session.query().filter(
                    self.table.table_id == id
                )
            else:
                cassette_types = session.query(self.table).all()
            if serialize is False:
                return cassette_types

            enum_types = []
            for i in cassette_types:
                enum_types.append(i.serialize())

            if id is not None:
                return enum_types[0]
            return enum_types
        finally:
            session.close()

    def create(self, *args, **kwargs):
        name = kwargs["name"]
        session = self.session_maker()
        try:
            if self.entry_already_exists(name, session) is True:
                raise ValueError(
                    "Already a value stored for {}".format(self.table))
            new_cassette_type = self.table(name=name)
            session.add(new_cassette_type)
            session.flush()
            session.commit()
            return new_cassette_type.serialize()
        finally:
            session.close()

    def entry_already_exists(self, name, session):
        return session.query(self.table).filter(
            self.table.name == name).count() > 0

    def update(self, id, changed_data):
        # TODO: CassetteTypeConnector.update()
        pass

    def delete(self, id):
        # TODO: CassetteTypeConnector.delete()
        pass


class CassetteTapeTypeConnector(AbsDataProviderConnector):
    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                cassette_types = session.query(CassetteTapeType).filter(
                    CassetteTapeType.table_id == id
                )
            else:
                cassette_types = session.query(CassetteTapeType).all()
            if serialize is False:
                return cassette_types

            enum_types = []
            for i in cassette_types:
                enum_types.append(i.serialize())

            if id is not None:
                return enum_types[0]
            return enum_types
        finally:
            session.close()

    def create(self, *args, **kwargs):
        # TODO: CassetteTypeConnector.create()
        pass

    def update(self, id, changed_data):
        # TODO: CassetteTypeConnector.update()
        pass

    def delete(self, id):
        # TODO: CassetteTypeConnector.delete()
        pass


class CassetteTapeThicknessConnector(AbsDataProviderConnector):
    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                cassette_types = session.query(CassetteTapeThickness).filter(
                    CassetteTapeThickness.table_id == id
                )
            else:
                cassette_types = session.query(CassetteTapeThickness).all()
            if serialize is False:
                return cassette_types

            enum_types = []
            for i in cassette_types:
                enum_types.append(i.serialize())

            if id is not None:
                return enum_types[0]
            return enum_types
        finally:
            session.close()

    def create(self, *args, **kwargs):
        # TODO: CassetteTypeConnector.create()
        pass

    def update(self, id, changed_data):
        # TODO: CassetteTypeConnector.update()
        pass

    def delete(self, id):
        # TODO: CassetteTypeConnector.delete()
        pass
