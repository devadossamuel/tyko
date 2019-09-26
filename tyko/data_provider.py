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
                serialized_projects.append(project.serialize())
            all_projects = serialized_projects
        session.close()
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

        session.add(new_project)
        session.commit()
        new_project_id = new_project.id
        session.close()
        return new_project_id

    def get_project(self, id=None, serialize=False):
        return self.get(id, serialize)

    def update(self, id, changed_data):
        updated_project = None
        projects = self.get_project(id)

        if len(projects) != 1:
            return updated_project

        project = projects[0]

        if project:
            if "title" in changed_data:
                project.title = changed_data['title']

            if "current_location" in changed_data:
                project.current_location = changed_data['current_location']

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

            session.close()
            return items_deleted > 0
        return False


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
                    collection_object.serialize()
                )

            all_collection_object = serialized_all_collection_object
        session.close()
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
        session.add(new_object)
        session.commit()
        object_id = new_object.id
        session.close()

        return object_id

    def update(self, id, changed_data):
        updated_object = None
        objects = self.get(id, serialize=False)

        if len(objects) != 1:
            return updated_object

        collection_object = objects[0]

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
        return all_collection_item

    def create(self, *args, **kwargs):
        name = kwargs["name"]
        file_name = kwargs.get("file_name")
        medusa_uuid = kwargs.get("medusa_uuid")
        new_item = scheme.CollectionItem(
            name=name,
            file_name=file_name,
            medusa_uuid=medusa_uuid
        )

        session = self.session_maker()
        session.add(new_item)
        session.commit()
        new_item_id = new_item.id
        session.close()

        return new_item_id

    def update(self, id, changed_data):
        updated_item = None
        items = self.get_item(id)
        if len(items) != 1:
            return None

        item = items[0]
        if item:
            item.file_name = changed_data["file_name"]
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
        session.close()
        if serialize:
            return [collection.serialize() for collection in all_collections]

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
        collections = self.get(id, serialize=False)

        if len(collections) != 1:
            return None

        collection = collections[0]
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


class DataProvider:
    def __init__(self, engine):
        self.engine = engine
        self.db_engine = engine
        # self.init_database()
        self.db_session_maker = orm.sessionmaker(bind=self.db_engine)

    def init_database(self):
        database.init_database(self.engine)

    def get_formats(self, serialize=False):
        try:
            session = self.db_session_maker()
            all_formats = session.query(scheme.FormatTypes).all()
            session.close()

        except sqlalchemy.exc.DatabaseError as e:
            raise DataError("Enable to get all format. Reason: {}".format(e))

        if serialize:
            return [format_.serialize() for format_ in all_formats]

        return all_formats
