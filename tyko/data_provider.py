# pylint: disable=redefined-builtin, invalid-name
import sqlalchemy
from sqlalchemy import orm
import abc
import tyko


class DataError(Exception):
    status_code = 500

    def __init__(self, message="Problem accessing data",
                 status_code=None, payload=None, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload


class AbsDataProvider(metaclass=abc.ABCMeta):

    def __init__(self, session) -> None:
        self._session = session

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


class ProjectData(AbsDataProvider):

    def get(self, id=None, serialize=False):
        if id:
            all_projects = self._session.query(tyko.scheme.Project)\
                .filter(tyko.scheme.Project.id == id)\
                .all()

        else:
            all_projects = self._session.query(tyko.scheme.Project).all()
        if serialize:
            return [project.serialize() for project in all_projects]
        else:
            return all_projects

    def create(self, *args, **kwargs):
        title = kwargs["title"]
        project_code = kwargs.get("project_code")
        current_location = kwargs.get("current_location")
        status = kwargs.get("status")
        specs = kwargs.get("specs")
        new_project = tyko.scheme.Project(
            title=title,
            project_code=project_code,
            current_location=current_location,
            status=status,
            specs=specs
        )
        self._session.add(new_project)
        self._session.commit()

        return new_project.id

    def get_project(self, id=None, serialize=False):
        return self.get(id, serialize)

    def update(self, id, changed_data):
        updated_project = None
        projects = self.get_project(id)
        project = None

        if len(projects) != 1:
            return updated_project
        else:
            project = projects[0]

        if project:
            project.title = changed_data['title']
            project.current_location = changed_data['current_location']
            project.status = changed_data['status']
            self._session.add(project)
            self._session.commit()
            updated_project = self.get_project(id)[0]

        return updated_project.serialize()

    def delete(self, id):
        if id:
            items_deleted = \
                self.session.query(tyko.scheme.Project)\
                    .filter(tyko.scheme.Project.id == id)\
                    .delete()
            return items_deleted > 0
        return False


class ObjectData(AbsDataProvider):

    def get(self, id=None, serialize=False):
        if id:
            all_collection_object = \
                self._session.query(tyko.scheme.CollectionObject) \
                    .filter(tyko.scheme.CollectionObject.id == id) \
                    .all()
        else:
            all_collection_object = \
                self._session.query(tyko.scheme.CollectionObject).all()

        if serialize:
            return [
                collection_object.serialize()
                for collection_object in all_collection_object
            ]
        else:
            return all_collection_object

    def create(self, *args, **kwargs):
        # TODO!
        name = kwargs["name"]
        new_object = tyko.scheme.CollectionObject(
            name=name,
        )
        self._session.add(new_object)
        self._session.commit()

        return new_object.id

    def update(self, id, changed_data):
        # TODO!
        pass

    def delete(self, id):
        # TODO!
        pass


class ItemData(AbsDataProvider):

    def get(self, id=None, serialize=False):
        if id:
            all_collection_item = \
                self._session.query(tyko.scheme.CollectionItem)\
                    .filter(tyko.scheme.CollectionItem.id == id)\
                    .all()
        else:
            all_collection_item = \
                self._session.query(tyko.scheme.CollectionItem).all()

        if serialize:
            return [
                collection_item.serialize()
                for collection_item in all_collection_item
            ]
        else:
            return all_collection_item

    def create(self, *args, **kwargs):
        name = kwargs["name"]
        barcode = kwargs.get("barcode")
        file_name = kwargs.get("file_name")
        new_item = tyko.scheme.CollectionItem(
            name=name,
            barcode=barcode,
            file_name=file_name
        )
        self._session.add(new_item)
        self._session.commit()
        return new_item.id

    def update(self, id, changed_data):
        # TODO!
        pass

    def delete(self, id):
        # TODO!
        pass


class CollectionData(AbsDataProvider):

    def get(self, id=None, serialize=False):
        if id:
            all_collections = \
                self._session.query(tyko.scheme.Collection)\
                    .filter(tyko.scheme.Collection.id == id)\
                    .all()
        else:
            all_collections = \
                self._session.query(tyko.scheme.Collection).all()

        if serialize:
            return [collection.serialize() for collection in all_collections]
        else:
            return all_collections

    def create(self, *args, **kwargs):
        collection_name = kwargs.get("collection_name")
        department = kwargs.get("department")
        record_series = kwargs.get("record_series")

        new_collection = tyko.scheme.Collection(
            collection_name=collection_name,
            department=department,
            record_series=record_series

        )
        self._session.add(new_collection)
        self._session.commit()
        return new_collection.id

    def update(self, id, changed_data):
        # TODO:!!!
        pass

    def delete(self, id):
        # TODO!
        pass


class DataProvider:
    def __init__(self, engine):
        self.engine = engine
        self.db_engine = sqlalchemy.create_engine(engine)
        self.init_database()
        db_session = orm.sessionmaker(bind=self.db_engine)
        self.session = db_session()

        self.entities = dict()
        for k, v in tyko.ENTITIES.items():
            self.entities[k] = v[1](self.session)

    def init_database(self):
        db_engine = sqlalchemy.create_engine(self.engine)
        tyko.database.init_database(db_engine)

    def get_formats(self, serialize=False):
        try:
            all_formats = self.session.query(tyko.scheme.FormatTypes).all()
        except sqlalchemy.exc.DatabaseError as e:
            raise DataError("Enable to get all format. Reason: {}".format(e))

        if serialize:
            return [format_.serialize() for format_ in all_formats]
        else:
            return all_formats
