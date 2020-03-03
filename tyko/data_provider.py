# pylint: disable=redefined-builtin, invalid-name
import abc

import sqlalchemy
from sqlalchemy import orm
from .exceptions import DataError
from . import scheme
from . import database


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


class ProjectDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_projects = session.query(scheme.Project)\
                .filter(scheme.Project.id == id)\
                .all()

        else:
            all_projects = session.query(scheme.Project).all()

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

    def create(self, *args, **kwargs):
        title = kwargs["title"]
        project_code = kwargs.get("project_code")
        current_location = kwargs.get("current_location")
        status = kwargs.get("status")
        specs = kwargs.get("specs")
        new_project = scheme.Project(
            title=title,
            project_code=project_code,
            current_location=current_location,
            status=status,
            specs=specs
        )
        session = self.session_maker()
        try:
            session.add(new_project)
            session.commit()
            new_project_id = new_project.id
            return new_project_id
        finally:
            session.close()

    def include_note(self, project_id, note_type_id, note_text):
        new_project_data = None
        session = self.session_maker()
        try:
            projects = session.query(scheme.Project) \
                .filter(scheme.Project.id == project_id) \
                .all()
            if len(projects) == 0:
                raise ValueError("Not a valid project")

            project = projects[0]

            note_types = session.query(scheme.NoteTypes) \
                .filter(scheme.NoteTypes.id == note_type_id) \
                .all()

            if len(note_types) == 0:
                raise ValueError("Not a valid note_type")

            note_type = note_types[0]

            new_note = scheme.Note(
                text=note_text,
                note_type=note_type
            )
            session.add(new_note)
            project.notes.append(new_note)
            session.commit()
            new_project = \
                session.query(scheme.Project).filter(
                    scheme.Project.id == project_id).one()

            new_project_data = new_project.serialize()
        finally:
            session.close()
        return new_project_data

    def update_note(self, project_id, note_id, changed_data):
        session = self.session_maker()
        try:
            projects = session.query(scheme.Project) \
                .filter(scheme.Project.id == project_id) \
                .all()
            if len(projects) == 0:
                raise ValueError("Not a valid project")

            project = projects[0]

            note = self._find_note(project, note_id)
            if "text" in changed_data:
                note.text = changed_data['text']
            if "note_type_id" in changed_data:

                note_type = session.query(scheme.NoteTypes).filter(
                    scheme.NoteTypes.id == changed_data['note_type_id']).one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_project = \
                session.query(scheme.Project).filter(
                    scheme.Project.id == project_id).one()

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
                project.status = changed_data['status']

            session = self.session_maker()
            session.add(project)
            session.commit()
            session.close()

            updated_project = session.query(scheme.Project)\
                .filter(scheme.Project.id == id)\
                .one()

        return updated_project.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()
            items_deleted = session.query(scheme.Project)\
                .filter(scheme.Project.id == id)\
                .delete()

            session.commit()
            session.close()
            return items_deleted > 0
        return False

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(scheme.NoteTypes).all()
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
            return session.query(scheme.Project) \
                .filter(scheme.Project.id == project_id) \
                .one().serialize()
        finally:
            session.close()

    def add_object(self, project_id, data):
        session = self.session_maker()
        try:
            projects = session.query(scheme.Project) \
                .filter(scheme.Project.id == project_id) \
                .all()
            if len(projects) == 0:
                raise ValueError("Not a valid project")

            project = projects[0]

            object_connector = ObjectDataConnector(self.session_maker)
            new_object_id = object_connector.create(**data)
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
                    return session.query(scheme.Project) \
                        .filter(scheme.Project.id == project_id) \
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
        projects = session.query(scheme.Project).filter(
            scheme.Project.id == project_id).all()

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


class ObjectDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        try:
            if id is not None:
                all_collection_object = \
                    session.query(scheme.CollectionObject).filter(
                        scheme.CollectionObject.id == id).all()
                if len(all_collection_object) == 0:
                    raise DataError(
                        message="Unable to find object: {}".format(id))
            else:
                all_collection_object = \
                    session.query(scheme.CollectionObject).all()
        except sqlalchemy.exc.DatabaseError as e:
            raise DataError(message="Unable to find object: {}".format(e))

        if serialize:
            serialized_all_collection_object = []
            for collection_object in all_collection_object:
                serialized_all_collection_object.append(
                    collection_object.serialize(True)
                )

            all_collection_object = serialized_all_collection_object
        session.close()

        if id is not None:
            return all_collection_object[0]

        return all_collection_object

    def create(self, *args, **kwargs):
        name = kwargs["name"]

        new_object = scheme.CollectionObject(
            name=name,
        )

        barcode = kwargs.get("barcode")
        if barcode is not None:
            new_object.barcode = barcode
        session = self.session_maker()
        if "collection_id" in kwargs:
            collection = session.query(scheme.Collection).filter(
                scheme.Collection.id == kwargs['collection_id']).one()

            if collection is None:
                raise ValueError("Not a valid collection")
            new_object.collection = collection
        session.add(new_object)
        session.commit()
        object_id = new_object.id
        session.close()

        return object_id

    def update(self, id, changed_data):
        updated_object = None
        collection_object = self.get(id, serialize=False)

        if collection_object:
            if "name" in changed_data:
                collection_object.name = changed_data['name']
            if "barcode" in changed_data:
                collection_object.barcode = changed_data['barcode']

            session = self.session_maker()
            session.add(collection_object)
            session.commit()
            session.close()

            updated_object = session.query(scheme.CollectionObject)\
                .filter(scheme.CollectionObject.id == id)\
                .one()

        return updated_object.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()

            items_deleted = session.query(scheme.CollectionObject)\
                .filter(scheme.CollectionObject.id == id).delete()

            success = items_deleted > 0
            session.commit()
            return success
        return False

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(scheme.NoteTypes).all()
        finally:
            session.close()

    def add_note(self, object_id: int,
                 note_type_id: int, note_text) -> None:

        session = self.session_maker()
        try:
            collection_object = self._get_object(object_id, session=session)

            note_types = session.query(scheme.NoteTypes) \
                .filter(scheme.NoteTypes.id == note_type_id) \
                .all()

            if len(note_types) == 0:
                raise ValueError("Not a valid note_type")

            note_type = note_types[0]

            new_note = scheme.Note(
                text=note_text,
                note_type=note_type
            )
            session.add(new_note)
            collection_object.notes.append(new_note)
            session.commit()

            new_object = session.query(scheme.CollectionObject) \
                .filter(scheme.CollectionObject.id == object_id) \
                .one()

            return new_object.serialize()

        finally:
            session.close()

    def remove_note(self, object_id, note_id):
        session = self.session_maker()
        try:
            objects = session.query(scheme.CollectionObject).filter(
                scheme.CollectionObject.id == object_id).all()

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
            return session.query(scheme.CollectionObject) \
                .filter(scheme.CollectionObject.id == object_id) \
                .one().serialize()
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

                note_type = session.query(scheme.NoteTypes).filter(
                    scheme.NoteTypes.id == changed_data['note_type_id']).one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_object = \
                session.query(scheme.CollectionObject).filter(
                    scheme.CollectionObject.id == object_id).one()

            return new_object.serialize()
        finally:
            session.close()

    @staticmethod
    def _get_object(object_id, session):
        collection_object = session.query(scheme.CollectionObject) \
            .filter(scheme.CollectionObject.id == object_id) \
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
            new_item_id = item_connector.create(**data)
            matching_object.items.append(item_connector.get(id=new_item_id))
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

            if matching_item not in matching_object.items:
                raise DataError(
                    message="Item with ID: {} is not a child of object with "
                            "ID: {}".format(item_id, object_id)
                )
            matching_object.items.remove(matching_item)
            session.commit()
            return session.query(scheme.CollectionObject) \
                .filter(scheme.CollectionObject.id == object_id) \
                .one().serialize()

        finally:
            session.close()

    @staticmethod
    def _find_item(item_id, session) -> scheme.CollectionItem:
        matching_items = \
            session.query(scheme.CollectionItem).filter(
                scheme.CollectionItem.id == item_id).all()

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
    def _find_object(object_id, session) -> scheme.CollectionObject:
        matching_objects = \
            session.query(scheme.CollectionObject).filter(
                scheme.CollectionObject.id == object_id).all()

        if len(matching_objects) == 0:
            raise DataError(
                message="No object found with ID: {}".format(
                    object_id))

        if len(matching_objects) > 1:
            raise DataError(
                message="Found multiple objects with ID: {}".format(
                    object_id))
        return matching_objects[0]


class ItemDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()

        if id:
            all_collection_item = session.query(scheme.CollectionItem)\
                .filter(scheme.CollectionItem.id == id)\
                .all()
        else:
            all_collection_item = \
                session.query(scheme.CollectionItem).all()

        if serialize:
            serialized_all_collection_item = []

            for collection_item in all_collection_item:
                serialized_all_collection_item.append(
                    collection_item.serialize())

            all_collection_item = serialized_all_collection_item
        session.close()

        if id is not None:
            return all_collection_item[0]

        return all_collection_item

    def add_note(self, item_id: int, note_text: str, note_type_id: int):
        session = self.session_maker()
        try:
            collection_item = self._get_item(item_id, session=session)

            note_types = session.query(scheme.NoteTypes) \
                .filter(scheme.NoteTypes.id == note_type_id) \
                .all()

            if len(note_types) == 0:
                raise ValueError("Not a valid note_type")

            note_type = note_types[0]

            new_note = scheme.Note(
                text=note_text,
                note_type=note_type
            )
            session.add(new_note)
            collection_item.notes.append(new_note)
            session.commit()

            new_item = session.query(scheme.CollectionItem) \
                .filter(scheme.CollectionItem.id == item_id) \
                .one()

            return new_item.serialize()

        finally:
            session.close()

    def create(self, *args, **kwargs):
        session = self.session_maker()
        name = kwargs["name"]
        format_id = kwargs["format_id"]
        format_type = session.query(scheme.FormatTypes)\
            .filter(scheme.FormatTypes.id == format_id).one()

        file_name = kwargs.get("file_name")
        medusa_uuid = kwargs.get("medusa_uuid")
        new_item = scheme.CollectionItem(
            name=name,
            file_name=file_name,
            medusa_uuid=medusa_uuid,
            format_type=format_type
        )

        session.add(new_item)
        session.commit()
        new_item_id = new_item.id
        session.close()

        return new_item_id

    def update(self, id, changed_data):
        updated_item = None
        item = self.get_item(id)
        if item:
            if "name" in changed_data:
                item.name = changed_data['name']

            if "file_name" in changed_data:
                item.file_name = changed_data["file_name"]

            if "medusa_uuid" in changed_data:
                item.medusa_uuid = changed_data["medusa_uuid"]

            if "obj_sequence" in changed_data:
                item.obj_sequence = int(changed_data["obj_sequence"])

            session = self.session_maker()

            session.add(item)
            session.commit()
            updated_item = session.query(scheme.CollectionItem)\
                .filter(scheme.CollectionItem.id == id)\
                .one()
        return updated_item.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()

            items_deleted = session.query(scheme.CollectionItem)\
                .filter(scheme.CollectionItem.id == id).delete()

            success = items_deleted > 0
            session.commit()
            return success
        return False

    def get_item(self, id=None, serialize=False):
        return self.get(id, serialize)

    def get_note_types(self):
        session = self.session_maker()
        try:
            return session.query(scheme.NoteTypes).all()
        finally:
            session.close()

    @staticmethod
    def _get_item(item_id, session):
        collection_items = session.query(scheme.CollectionItem) \
            .filter(scheme.CollectionItem.id == item_id) \
            .all()
        if len(collection_items) == 0:
            raise ValueError("Not a valid item")
        collection_item = collection_items[0]
        return collection_item

    def remove_note(self, item_id, note_id):
        session = self.session_maker()
        try:
            collection_items = session.query(scheme.CollectionItem).filter(
                scheme.CollectionItem.id == item_id).all()

            if len(collection_items) == 0:
                raise DataError(
                    message="Unable to locate item "
                            "with ID: {}".format(collection_items),
                    status_code=404
                )

            if len(collection_items) > 1:
                raise DataError(
                    message="Found multiple items with ID: {}".format(
                        item_id))

            item = collection_items[0]

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
            return session.query(scheme.CollectionItem) \
                .filter(scheme.CollectionItem.id == item_id) \
                .one().serialize()
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

                note_type = session.query(scheme.NoteTypes).filter(
                    scheme.NoteTypes.id == changed_data['note_type_id']).one()

                if note_type is not None:
                    note.note_type = note_type

            session.commit()
            new_item = \
                session.query(scheme.CollectionItem).filter(
                    scheme.CollectionItem.id == item_id).one()
            return new_item.serialize()

        finally:
            session.close()

    @staticmethod
    def _find_note(item, note_id):
        for note in item.notes:
            if note.id == note_id:
                return note
        raise ValueError("No matching note for item")


class CollectionDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_collections = session.query(scheme.Collection)\
                .filter(scheme.Collection.id == id)\
                .all()
        else:
            all_collections = \
                session.query(scheme.Collection).all()

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

        new_collection = scheme.Collection(
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

            session = self.session_maker()

            session.add(collection)
            session.commit()
            updated_collection = session.query(scheme.Collection)\
                .filter(scheme.Collection.id == id)\
                .one()
        return updated_collection.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()

            collections_deleted = session.query(scheme.Collection)\
                .filter(scheme.Collection.id == id).delete()

            success = collections_deleted > 0
            session.commit()
            return success
        return False


class NotesDataConnector(AbsDataProviderConnector):

    def get(self, id=None, serialize=False):
        session = self.session_maker()
        if id:
            all_notes = session.query(scheme.Note) \
                .filter(scheme.Note.id == id) \
                .all()
        else:
            all_notes = \
                session.query(scheme.Note).all()

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
                    obj.id for obj in note.item_sources
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

        new_note = scheme.Note(
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
                note_types = session.query(scheme.NoteTypes).filter(
                    scheme.NoteTypes.id == changed_data['note_type_id'])

                note_type = note_types.one()
                note.note_type = note_type

            session.add(note)
            session.commit()
            session.close()

            updated_note = session.query(scheme.Note) \
                .filter(scheme.Note.id == id) \
                .one()
        return updated_note.serialize()

    def delete(self, id):
        if id:
            session = self.session_maker()
            items_deleted = session.query(scheme.Note) \
                .filter(scheme.Note.id == id) \
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
                all_formats = session.query(scheme.FormatTypes)\
                    .filter(scheme.FormatTypes.id == id)\
                    .all()
            else:
                all_formats = session.query(scheme.FormatTypes).all()
            session.close()

        except sqlalchemy.exc.DatabaseError as e:
            raise DataError("Enable to get all format. Reason: {}".format(e))

        if serialize:
            return [format_.serialize() for format_ in all_formats]

        return all_formats
