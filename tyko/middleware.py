# pylint: disable=redefined-builtin, invalid-name

import abc
import hashlib
import json
import sys
import traceback
from typing import List, Dict, Any

from flask import jsonify, make_response, abort, request, url_for

from . import data_provider as dp
from . import pbcore
from .exceptions import DataError

CACHE_HEADER = "private, max-age=0"


class AbsMiddlwareEntity(metaclass=abc.ABCMeta):
    WRITABLE_FIELDS: List[str] = []

    @classmethod
    def validate_writable_fields(cls, original_method):
        def validate(org_cls, json_request, *args, **kwargs):
            invalid_names_found = []
            for k in json_request.keys():
                if k not in org_cls.WRITABLE_FIELDS:
                    invalid_names_found.append(k)
            if invalid_names_found:
                raise ValueError(
                    f"Invalid field(s) {', '.join(invalid_names_found)}")

            return original_method(org_cls, json_request, *args, **kwargs)

        return validate

    @classmethod
    def field_can_edit(cls, field) -> bool:
        return field in cls.WRITABLE_FIELDS

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

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:
        invalid_names_found = []
        for k in json_request.keys():
            if k not in cls.WRITABLE_FIELDS:
                invalid_names_found.append(k)

        if invalid_names_found:
            raise ValueError(
                f"Invalid field(s) {', '.join(invalid_names_found)}. "
                f"only {', '.join(cls.WRITABLE_FIELDS)} can be modified."
            )

        return dict()


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

    def get_formats_by_id(self, id):
        formats = self.data_provider.get_formats(id=id, serialize=True)
        return jsonify(formats)


class ObjectMiddlwareEntity(AbsMiddlwareEntity):
    WRITABLE_FIELDS = [
        "name",
        "barcode",
        "collection_id",
        'originals_rec_date',
        'originals_return_date'
    ]

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
            response = make_response(jsonify(data), 200)

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

    def add_item(self, project_id, object_id):

        project_json = ProjectMiddlwareEntity(
            self._data_provider).get_project_by_id(project_id).get_json()

        current_project = project_json['project']

        # make sure that the project has that object
        for child_object in current_project['objects']:
            if child_object['object_id'] == object_id:
                break
        else:
            return make_response(
                f"Project with id {project_id} does not have an object with an"
                f" id of {object_id}",
                404)
        request_data = request.get_json()

        try:
            try:
                new_item_data = {
                    "name": request_data["name"],
                    "format_id": request_data["format_id"],
                    "file_name": request_data.get("file_name"),

                }
            except KeyError as e:
                traceback.print_exc(file=sys.stderr)
                return make_response(
                    "missing required value {}".format(e), 400)

            new_item = self._data_connector.add_item(
                object_id=object_id,
                data=new_item_data)

            return jsonify(
                {
                    "item": new_item
                }
            )
        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid item data", 400)

    def pbcore(self, id):
        xml = pbcore.create_pbcore_from_object(
            object_id=id,
            data_provider=self._data_provider)
        response = make_response(xml, 200)
        response.headers["Content-type"] = "text/xml"
        return response

    def delete(self, id):
        if self._data_connector.delete(id):
            return make_response("", 204)

        return make_response("", 404)

    def update(self, id):
        json_request = request.json
        try:
            new_object = self.create_changed_data(json_request)
        except ValueError as reason:
            return make_response(
                "Cannot update object field: {}".format(reason), 400)

        updated_object = \
            self._data_connector.update(
                id, changed_data=new_object)

        if not updated_object:
            return make_response("", 204)

        return jsonify(
            {"object": updated_object}
        )

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:
        new_object = super().create_changed_data(json_request)
        if "name" in request.json:
            new_object["name"] = json_request["name"]
        if "barcode" in json_request:
            new_object["barcode"] = json_request['barcode']
        if "collection_id" in json_request:
            new_object['collection_id'] = json_request['collection_id']
        if "originals_rec_date" in json_request:
            new_object['originals_rec_date'] = json_request[
                'originals_rec_date']
        if 'originals_return_date' in json_request:
            new_object['originals_return_date'] = json_request[
                'originals_return_date']
        return new_object

    def create(self, data=None):
        data = data or request.get_json()
        object_name = data["name"]
        barcode = data.get('barcode')
        collection_id = data.get('collection_id')
        new_object_id = self._data_connector.create(
            name=object_name,
            barcode=barcode,
            collection_id=collection_id
        )
        return jsonify({
            "id": new_object_id,
            "url": url_for("object_by_id", id=new_object_id)
        })

    def add_note(self, project_id, object_id):  # pylint: disable=W0613
        data = request.get_json()
        try:
            note_type_id = int(data.get("note_type_id"))
            note_text = data.get("text")
            update_object = \
                self._data_connector.add_note(
                    object_id=object_id,
                    note_type_id=note_type_id,
                    note_text=note_text)
            return jsonify(
                {
                    "object": update_object
                }
            )
        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid note data", 400)

    def remove_note(self, object_id, note_id):
        updated_object = self._data_connector.remove_note(
            object_id=object_id,
            note_id=note_id
        )

        return make_response(
            jsonify({
                "object": updated_object
            }),
            202
        )

    def update_note(self, object_id, note_id):
        data = request.get_json()
        updated_object = \
            self._data_connector.update_note(object_id=object_id,
                                             note_id=note_id,
                                             changed_data=data)
        if not updated_object:
            return make_response("", 204)

        return jsonify(
            {"object": updated_object}
        )

    def remove_item(self, object_id, item_id):
        updated_object = self._data_connector.remove_item(
            object_id=object_id,
            item_id=item_id
        )
        return make_response(
            jsonify({
                "object": updated_object
            }),
            202
        )


class CollectionMiddlwareEntity(AbsMiddlwareEntity):
    WRITABLE_FIELDS = [
        "collection_name",
        "record_series",
        "department"
    ]

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
            response = make_response(jsonify(data), 200)

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = CACHE_HEADER
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

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:
        new_collection = super().create_changed_data(json_request)
        if "collection_name" in json_request:
            new_collection["collection_name"] = json_request["collection_name"]

        if "department" in json_request:
            new_collection["department"] = json_request["department"]

        if "record_series" in json_request:
            new_collection["record_series"] = json_request["record_series"]
        return new_collection

    def update(self, id):
        json_request = request.get_json()

        try:
            new_collection = self.create_changed_data(json_request)
        except ValueError as reason:
            return make_response(
                "Cannot update collection: Reason".format(reason), 400)

        updated_collection = \
            self._data_connector.update(
                id, changed_data=new_collection)

        if not updated_collection:
            return make_response("", 204)

        return jsonify(
            {"collection": updated_collection}
        )

    def create(self):
        data = request.get_json()
        collection_name = data["collection_name"]
        department = data.get("department")
        record_series = data.get("record_series")
        new_collection_id = \
            self._data_connector.create(
                collection_name=collection_name,
                department=department,
                record_series=record_series)

        return jsonify({
            "id": new_collection_id,
            "url": url_for("collection_by_id", id=new_collection_id),
            "frontend_url": url_for("page_collection_details",
                                    collection_id=new_collection_id)
        })


class ProjectMiddlwareEntity(AbsMiddlwareEntity):
    WRITABLE_FIELDS = [
        "title",
        "project_code",
        "status",
        "current_location"
    ]

    def __init__(self, data_provider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.ProjectDataConnector(data_provider.db_session_maker)

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            return self.get_project_by_id(kwargs["id"])

        limit = request.args.get("limit")
        offset = request.args.get("offset")
        projects = self._data_connector.get(serialize=serialize)
        total_projects = len(projects)
        if limit:
            offset_value = int(offset)
            limit_value = int(limit)
            projects = projects[offset_value:limit_value+offset_value]

        if serialize:
            data = {
                "projects": projects,
                "total": total_projects
            }
            json_data = json.dumps(data)
            response = make_response(jsonify(data), 200)

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = CACHE_HEADER
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

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:
        new_project = super().create_changed_data(json_request)

        if "project_code" in json_request:
            new_project["project_code"] = json_request.get("project_code")

        if "current_location" in json_request:
            new_project["current_location"] = \
                json_request.get("current_location")

        if "status" in json_request:
            new_project["status"] = json_request.get("status")

        if "title" in request.json:
            new_project["title"] = json_request.get("title")
        return new_project

    def update(self, id):

        json_request = request.json
        try:
            new_project = self.create_changed_data(json_request)
        except ValueError as reason:
            return make_response(
                "Cannot update project. Reason: {}".format(reason), 400)

        updated_project = \
            self._data_connector.update(
                id, changed_data=new_project)

        if not updated_project:
            return make_response("", 204)

        return jsonify(
            {"project": updated_project}
        )

    def create(self):
        data = request.get_json()
        title = data['title']
        project_code = data.get('project_code')
        current_location = data.get('current_location')
        status = data.get('status')
        specs = data.get('specs')
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

    def update_note(self, project_id, note_id):

        data = request.get_json()
        note_id_value = int(note_id)
        updated_project = \
            self._data_connector.update_note(project_id=project_id,
                                             note_id=note_id_value,
                                             changed_data=data)
        if not updated_project:
            return make_response("", 204)

        return jsonify(
            {"project": updated_project}
        )

    def remove_note(self, project_id, note_id):
        updated_project = self._data_connector.remove_note(
            project_id=project_id,
            note_id=note_id
        )

        return make_response(
            jsonify({
                "project": updated_project
            }),
            202
        )

    def add_note(self, project_id):

        data = request.get_json()
        try:
            note_type_id = data.get("note_type_id")
            note_text = data.get("text")
            updated_project = \
                self._data_connector.include_note(
                    project_id=project_id,
                    note_type_id=note_type_id,
                    note_text=note_text)

            return jsonify(
                {
                    "project": updated_project
                }
            )
        except ValueError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid contents", 400)

        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid note data", 400)

    def add_object(self, project_id):
        try:

            new_data = self.get_new_data(request.get_json())
            new_object = self._data_connector.add_object(project_id,
                                                         data=new_data)
            return jsonify(
                {
                    "object": new_object
                }
            )

        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid data", 400)
        except KeyError as e:
            traceback.print_exc(file=sys.stderr)
            return make_response("Missing required data: {}".format(e), 400)

    def remove_object(self, project_id, object_id):
        try:
            updated_project = self._data_connector.remove_object(
                project_id=project_id, object_id=object_id)

            return make_response(
                jsonify({
                    "project": updated_project
                }),
                202
            )
        except DataError as e:
            return make_response(e.message, e.status_code)

    def get_new_data(self, data):
        new_data = data.copy()
        if 'collectionId' in data:
            new_data['collection_id'] = int(data['collectionId'])

        return new_data


class ItemMiddlwareEntity(AbsMiddlwareEntity):
    WRITABLE_FIELDS = [
        "name",
        "file_name",
        "medusa_uuid",
        "obj_sequence"
    ]

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
            response = make_response(jsonify(data), 200)

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = CACHE_HEADER
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

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:
        new_item = super().create_changed_data(json_request)

        for field in cls.WRITABLE_FIELDS:
            if field == "obj_sequence":
                continue
            if field in json_request:
                new_item[field] = json_request.get(field)

        if "obj_sequence" in json_request:
            obj_sequence = json_request.get("obj_sequence")
            new_item["obj_sequence"] = int(obj_sequence)
        return new_item

    def update(self, id):
        json_request = request.json
        try:
            new_item = self.create_changed_data(json_request)

        except ValueError as reason:
            return make_response(
                "Cannot update item. Reason: {}".format(reason), 400)

        replacement_item = self._data_connector.update(
            id, changed_data=new_item
        )
        if not replacement_item:
            return make_response("", 204)
        return jsonify(
            {
                "item": replacement_item
            }
        )

    def add_note(self, item_id):
        data = request.get_json()
        try:
            note_type_id = int(data.get("note_type_id"))
            note_text = data.get("text")
            update_item = \
                self._data_connector.add_note(
                    item_id=item_id,
                    note_type_id=note_type_id,
                    note_text=note_text)
            return jsonify(
                {
                    "item": update_item
                }
            )
        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid data", 400)

    def create(self):
        data = request.get_json()
        name = data['name']
        format_id = data['format_id']
        file_name = data.get('file_name')
        medusa_uuid = data.get("medusa_uuid")
        new_item_id = self._data_connector.create(
            name=name,
            file_name=file_name,
            medusa_uuid=medusa_uuid,
            format_id=format_id
        )

        return jsonify(
            {
                "id": new_item_id,
                "url": url_for("item_by_id", id=new_item_id)
            }
        )

    def remove_note(self, item_id, note_id):
        updated_item = self._data_connector.remove_note(
            item_id=item_id,
            note_id=note_id
        )

        return make_response(
            jsonify({
                "item": updated_item
            }),
            202
        )

    def update_note(self, item_id, note_id):
        data = request.get_json()
        updated_object = \
            self._data_connector.update_note(item_id=item_id,
                                             note_id=note_id,
                                             changed_data=data)
        if not updated_object:
            return make_response("", 204)

        return jsonify(
            {"item": updated_object}
        )


class NotestMiddlwareEntity(AbsMiddlwareEntity):
    WRITABLE_FIELDS = [
        "text",
        "note_type_id"
    ]

    def __init__(self, data_provider) -> None:
        super().__init__(data_provider)

        self._data_connector = \
            dp.NotesDataConnector(data_provider.db_session_maker)

    @staticmethod
    def resolve_parents(source: dict) -> dict:
        newone = source.copy()
        parent_routes = []

        for pid in source.get('parent_project_ids', []):
            parent_routes.append(f"{url_for('projects')}/{pid}")

        for pid in source.get('parent_object_ids', []):
            parent_routes.append(f"{url_for('object')}/{pid}")

        for pid in source.get('parent_item_ids', []):
            parent_routes.append(f"{url_for('item')}/{pid}")

        newone['parents'] = parent_routes
        return newone

    def get(self, serialize=False, **kwargs):
        if "id" in kwargs:
            note = self._data_connector.get(kwargs['id'], serialize=True)
            note_data = self.resolve_parents(note)
            del note_data['parent_project_ids']
            del note_data['parent_object_ids']
            del note_data['parent_item_ids']

            return jsonify({
                "note": note_data
            })

        notes = self._data_connector.get(serialize=serialize)
        if serialize:
            note_data = []
            for n in notes:
                new_data = n.copy()
                del new_data['parent_project_ids']
                del new_data['parent_object_ids']
                del new_data['parent_item_ids']
                note_data.append(new_data)
            data = {
                "notes": note_data,
                "total": len(note_data)
            }
            json_data = json.dumps(data)
            response = make_response(jsonify(data), 200)

            hash_value = \
                hashlib.sha256(bytes(json_data, encoding="utf-8")).hexdigest()

            response.headers["ETag"] = str(hash_value)
            response.headers["Cache-Control"] = "private, max-age=0"
            return response
        return notes

    def delete(self, id):
        res = self._data_connector.delete(id)

        if res is True:
            return make_response("", 204)
        return make_response("", 404)

    def update(self, id):
        new_object = dict()
        json_request = request.get_json()
        for k, _ in json_request.items():
            if not self.field_can_edit(k):
                return make_response(
                    "Cannot update note field: {}".format(k), 400)

        if "text" in json_request:
            new_object["text"] = json_request.get("text")
        if 'note_type_id' in json_request:
            new_object['note_type_id'] = int(json_request['note_type_id'])

        updated_note = \
            self._data_connector.update(
                id, changed_data=new_object)

        if not updated_note:
            return make_response("", 204)

        return jsonify(
            {"note": updated_note}
        )

    def create(self):
        data = request.get_json()
        note_type = int(data['note_type_id'])
        text = data['text']
        new_note_id = self._data_connector.create(
            text=text, note_types_id=note_type
        )
        return jsonify(
            {
                "id": new_note_id,
                "url": url_for("note_by_id", id=new_note_id)
            }
        )
