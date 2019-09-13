# pylint: disable=redefined-builtin, invalid-name

import abc
import hashlib
import json

from flask import jsonify, make_response, abort, request, url_for
from typing import Mapping

import tyko.entities
import tyko.data_provider
from tyko.data_provider import DataProvider


class AbsMiddlwareEntity(metaclass=abc.ABCMeta):
    def __init__(self,
                 data_provider: tyko.data_provider.DataProvider) -> None:
        self._data_provider = data_provider

    @abc.abstractmethod
    def get(self, serialize=False, *args, **kwargs):
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
    def __init__(self, data_provider: DataProvider) -> None:
        self.data_provider = data_provider

        self.entities: Mapping[str, AbsMiddlwareEntity] = dict()
        for entity in tyko.ENTITIES.keys():
            self.entities[entity] = \
                tyko.entities.load_entity(
                    entity, self.data_provider).middleware()

    def get_formats(self, serialize=True):
        formats = self.data_provider.get_formats(serialize=serialize)
        if serialize:
            result = jsonify(formats)
        else:
            result = formats
        return result


class ObjectMiddlwareEntity(AbsMiddlwareEntity):

    def get(self, serialize=False, *args, **kwargs):
        if "id" in kwargs:
            return self.object_by_id(id=kwargs["id"])

        objects = \
            self._data_provider.entities["object"].get(serialize=serialize)

        if serialize:
            data = {
                "objects": objects,
                "total": len(objects)
            }
            json_data = json.dumps(data)
            response = make_response(jsonify(data, 200))

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=300"
            return response

        result = objects
        return result

    def object_by_id(self, id):
        current_object = \
            self._data_provider.entities['object'].get(id, serialize=True)

        if current_object:
            return jsonify({
                "object": current_object
            })

        abort(404)

    def delete(self, id):
        """TODO"""

    def update(self, id):
        """TODO"""

    def create(self):
        """TODO"""
        object_name = request.form["name"]
        new_object_id = self._data_provider.entities['object'].create(
            name=object_name
        )
        return jsonify({
            "id": new_object_id,
            "url": url_for("object_by_id", id=new_object_id)
        })


class CollectionMiddlwareEntity(AbsMiddlwareEntity):

    def get(self, serialize=False, *args, **kwargs):
        if "id" in kwargs:
            return self.collection_by_id(id=kwargs["id"])

        collections = \
            self._data_provider.entities['collection'].get(serialize=serialize)

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
        current_collection = \
            self._data_provider.entities['collection'].get(id,
                                                           serialize=True)
        if current_collection:
            return jsonify({
                "collection": current_collection
            })

        abort(404)

    def delete(self, id):
        """TODO"""

    def update(self, id):
        """TODO"""

    def create(self):
        collection_name = request.form["collection_name"]
        department = request.form.get("department")
        record_series = request.form.get("record_series")
        new_collection_id = \
            self._data_provider.entities['collection'].create(
                collection_name=collection_name,
                department=department,
                record_series=record_series)

        return jsonify({
            "id": new_collection_id,
            "url": url_for("collection_by_id", id=new_collection_id)
        })


class ProjectMiddlwareEntity(AbsMiddlwareEntity):

    def get(self, serialize=False, *args, **kwargs):
        if "id" in kwargs:
            return self.get_project_by_id(kwargs["id"])

        projects = \
            self._data_provider.entities['project'].get(serialize=serialize)

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
        current_project = \
            self._data_provider.entities['project'].get(id, serialize=True)

        if current_project:
            return jsonify(
                {
                    "project": current_project
                }
            )

        abort(404)

    def delete(self, id):
        if self._data_provider.entities['project'].delete(id):
            return make_response("", 204)

        return make_response("", 404)

    def update(self, id):
        new_project = {
            "project_code": request.form["project_code"],
            "current_location": request.form["current_location"],
            "status": request.form["status"],
            "title": request.form["title"]
        }
        updated_project = \
            self._data_provider.entities['project'].update(
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
            self._data_provider.entities['project'].create(
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

    def get(self, serialize=False, *args, **kwargs):
        if "id" in kwargs:
            return self.item_by_id(kwargs["id"])

        items = self._data_provider.entities['item'].get(serialize=serialize)
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
        current_item = \
            self._data_provider.entities['item'].get(id, serialize=True)

        if current_item:
            return jsonify(
                {
                    "item": current_item
                }
            )

        abort(404)

    def delete(self, id):
        pass

    def update(self, id):
        pass

    def create(self):
        name = request.form.get('name')
        barcode = request.form.get('barcode')
        file_name = request.form.get('file_name')
        new_item_id = self._data_provider.entities['item'].create(
            name=name,
            barcode=barcode,
            file_name=file_name
        )

        return jsonify(
            {
                "id": new_item_id,
                "url": url_for("item_by_id", id=new_item_id)
            }
        )
