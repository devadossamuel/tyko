# pylint: disable=redefined-builtin, invalid-name

import abc
import hashlib
import json

from flask import jsonify, make_response, abort, request, url_for
from . import data_provider as dp
from . import pbcore


class AbsMiddlwareEntity(metaclass=abc.ABCMeta):
    def __init__(self, data_provider) -> None:
        self._data_provider = data_provider

    @abc.abstractmethod
    def get(self, serialize=False, **kwargs):
        """Add a new entity"""

    @abc.abstractmethod
    def delete(self, id):
        """CRU_D_ Delete"""

    @abc.abstractmethod
    def update(self, id):
        """CR_U_D update"""

    @abc.abstractmethod
    def create(self):
        """_C_RUD update"""


class Middleware:
    def __init__(self, data_provider: dp.DataProvider) -> None:
        self.data_provider = data_provider

    def get_formats(self, serialize=True):
        formats = self.data_provider.get_formats(serialize=serialize)
        if serialize:
            result = jsonify(formats)
        else:
            result = formats
        return result


class ObjectMiddlwareEntity(AbsMiddlwareEntity):

    def __init__(self, data_provider: dp.DataProvider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.ObjectDataConnector(data_provider.db_session_maker)

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            return self.object_by_id(id=kwargs["id"])

        objects = self._data_connector.get(serialize=serialize)

        if serialize:
            data = {
                "objects": objects,
                "total": len(objects)
            }
            response = make_response(jsonify(data, 200))

            json_data = json.dumps(data)
            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=300"
            return response

        result = objects
        return result

    def object_by_id(self, id):

        current_object = self._data_connector.get(id, serialize=True)

        if current_object:
            return jsonify({
                "object": current_object
            })

        return abort(404)

    def pbcore(self, id):
        xml = pbcore.create_pbcore_from_object(
            object_id=id,
            data_provider=self._data_provider)
        return xml
        # self._data_provider
        # return jsonify({})

    def delete(self, id):
        if self._data_connector.delete(id):
            return make_response("", 204)

        return make_response("", 404)

    def update(self, id):
        new_object = dict()

        if "name" in request.form:
            new_object["name"] = request.form.get("name")

        if "barcode" in request.form:
            new_object["barcode"] = request.form.get("barcode")

        updated_object = \
            self._data_connector.update(
                id, changed_data=new_object)

        if not updated_object:
            return make_response("", 204)

        return jsonify(
            {"object": updated_object}
        )

    def create(self):
        object_name = request.form["name"]
        barcode = request.form.get('barcode')
        new_object_id = self._data_connector.create(
            name=object_name,
            barcode=barcode
        )
        return jsonify({
            "id": new_object_id,
            "url": url_for("object_by_id", id=new_object_id)
        })


class CollectionMiddlwareEntity(AbsMiddlwareEntity):

    def __init__(self, data_provider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.CollectionDataConnector(data_provider.db_session_maker)

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            return self.collection_by_id(id=kwargs["id"])

        collections = self._data_connector.get(serialize=serialize)

        if serialize:
            data = {
                "collections": collections,
                "total": len((collections))
            }

            json_data = json.dumps(data)
            response = make_response(jsonify(data, 200))

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=300"
            return response

        result = collections
        return result

    def collection_by_id(self, id):
        current_collection = self._data_connector.get(id, serialize=True)
        if current_collection:
            return jsonify({
                "collection": current_collection
            })

        return abort(404)

    def delete(self, id):
        if self._data_connector.delete(id):
            return make_response("", 204)

        return make_response("", 404)

    def update(self, id):
        new_collection = dict()

        if "collection_name" in request.form:
            new_collection["collection_name"] = \
                request.form.get("collection_name")

        if "department" in request.form:
            new_collection["collection_name"] = request.form.get("department")

        updated_collection = \
            self._data_connector.update(
                id, changed_data=new_collection)

        if not updated_collection:
            return make_response("", 204)

        return jsonify(
            {"collection": updated_collection}
        )

    def create(self):
        collection_name = request.form["collection_name"]
        department = request.form.get("department")
        record_series = request.form.get("record_series")
        new_collection_id = \
            self._data_connector.create(
                collection_name=collection_name,
                department=department,
                record_series=record_series)

        return jsonify({
            "id": new_collection_id,
            "url": url_for("collection_by_id", id=new_collection_id)
        })


class ProjectMiddlwareEntity(AbsMiddlwareEntity):

    def __init__(self, data_provider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.ProjectDataConnector(data_provider.db_session_maker)

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            return self.get_project_by_id(kwargs["id"])

        projects = self._data_connector.get(serialize=serialize)

        if serialize:
            data = {
                "projects": projects,
                "total": len(projects)
            }
            json_data = json.dumps(data)
            response = make_response(jsonify(data, 200))

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=300"
            return response

        result = projects
        return result

    def get_project_by_id(self, id):
        current_project = self._data_connector.get(id, serialize=True)

        if current_project:
            return jsonify(
                {
                    "project": current_project
                }
            )

        return abort(404)

    def delete(self, id):
        if self._data_connector.delete(id):
            return make_response("", 204)

        return make_response("", 404)

    def update(self, id):
        new_project = dict()
        if "project_code" in request.form:
            new_project["project_code"] = request.form.get("project_code")

        if "current_location" in request.form:
            new_project["current_location"] = \
                request.form.get("current_location")

        if "status" in request.form:
            new_project["status"] = request.form.get("status")
        if "title" in request.form:
            new_project["title"] = request.form.get("title")
        #
        #     "project_code": request.form.get("project_code"),
        #     "current_location": request.form.get("current_location"),
        #     "status": request.form.get("status"),
        #     "title": request.form["title"]
        # }

        updated_project = \
            self._data_connector.update(
                id, changed_data=new_project)

        if not updated_project:
            return make_response("", 204)

        return jsonify(
            {"project": updated_project}
        )

    def create(self):
        project_code = request.form.get('project_code')
        title = request.form.get('title')
        if title is None:
            return make_response("Missing required data", 400)
        current_location = request.form.get('current_location')
        status = request.form.get('status')
        specs = request.form.get('specs')
        new_project_id = \
            self._data_connector.create(
                title=title,
                project_code=project_code,
                current_location=current_location,
                status=status,
                specs=specs
            )

        return jsonify(
            {
                "id": new_project_id,
                "url": url_for("project_by_id", id=new_project_id)
            }
        )


class ItemMiddlwareEntity(AbsMiddlwareEntity):
    def __init__(self, data_provider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.ItemDataConnector(data_provider.db_session_maker)

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            return self.item_by_id(kwargs["id"])

        items = self._data_connector.get(serialize=serialize)
        if serialize:
            data = {
                "items": items,
                "total": len(items)
            }

            json_data = json.dumps(data)
            response = make_response(jsonify(data, 200))

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=300"
            return response

        result = items
        return result

    def item_by_id(self, id):
        current_item = self._data_connector.get(id, serialize=True)

        if current_item:
            return jsonify(
                {
                    "item": current_item
                }
            )

        return abort(404)

    def delete(self, id):

        res = self._data_connector.delete(id)

        if res is True:
            return make_response("", 204)
        return make_response("", 404)

    def update(self, id):
        new_item = {
            "file_name": request.form.get("file_name"),
            "medusa_uuid": request.form.get("medusa_uuid")
        }
        replacement_item = self._data_connector.update(
            id, changed_data=new_item
        )

        return jsonify(
            {
                "item": replacement_item
            }
        )

    def create(self):
        name = request.form.get('name')
        file_name = request.form.get('file_name')
        medusa_uuid = request.form.get("medusa_uuid")
        new_item_id = self._data_connector.create(
            name=name,
            file_name=file_name,
            medusa_uuid=medusa_uuid
        )

        return jsonify(
            {
                "id": new_item_id,
                "url": url_for("item_by_id", id=new_item_id)
            }
        )
