import sys
import traceback
from typing import Dict, Any

from flask import views, make_response, jsonify, request, url_for

from tyko import middleware, data_provider


class ObjectItemNotesAPI(views.MethodView):
    def __init__(self, item: middleware.ItemMiddlwareEntity) -> None:
        self._item = item

    def put(self, project_id, object_id, item_id, note_id):  # noqa: E501 pylint: disable=W0613,C0301
        return self._item.update_note(item_id, note_id)

    def delete(self, project_id, object_id, item_id, note_id):  # noqa: E501  pylint: disable=W0613,C0301
        return self._item.remove_note(item_id, note_id)


class ObjectItemAPI(views.MethodView):
    def __init__(self, provider) -> None:

        self._provider = provider

    def post(self, project_id, object_id):  # noqa: E501  pylint: disable=W0613,C0301
        current_project = middleware.ProjectMiddlwareEntity(
            self._provider).get_project_by_id(project_id)
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
            new_item_data = {
                "name": request_data["name"],
                "format_id": request_data["format_id"],
                "files": request_data.get("files", [])

            }
        except KeyError as e:
            traceback.print_exc(file=sys.stderr)
            return make_response(
                "missing required value {}".format(e), 400)

        format_type = self._provider.get_formats(
            request_data["format_id"], serialize=True)[0]
        connectors = {
            "audio cassette": data_provider.AudioCassetteDataConnector,
            'casette tape': data_provider.AudioCassetteDataConnector,

        }
        connector_class = connectors.get(format_type['name'])
        if connector_class is not None:
            connector = connector_class(self._provider.db_session_maker)
            new_item = connector.create(**request_data, object_id=object_id)
        else:
            data_connector = \
                data_provider.ObjectDataConnector(
                    self._provider.db_session_maker)

            new_item = data_connector.add_item(
                object_id=object_id,
                data=new_item_data)
        try:
            return jsonify(
                {
                    "item": new_item,
                    'routes': {
                        "frontend": url_for("page_project_object_item_details",
                                            object_id=object_id,
                                            project_id=project_id,
                                            item_id=new_item['item_id']
                                            ),
                        "api": url_for("object_item",
                                       object_id=object_id,
                                       project_id=project_id,
                                       item_id=new_item['item_id']
                                       )
                    }
                }
            )
        except AttributeError:
            traceback.print_exc(file=sys.stderr)
            return make_response("Invalid item data", 400)

    def get(self, project_id, object_id):  # noqa: E501  pylint: disable=W0613,C0301
        item_id = int(request.args.get("item_id"))

        connector = data_provider.ItemDataConnector(
            self._provider.db_session_maker)

        i = connector.get(id=item_id, serialize=True)
        if i['parent_object_id'] != object_id:
            raise AttributeError("object id doesn't match item id")
        for note in i['notes']:
            note['route'] = self.get_note_routes(
                note,
                object_id=object_id,
                project_id=project_id,
                item_id=item_id
            )
        return i

    @staticmethod
    def get_note_routes(note, item_id, object_id,
                        project_id) -> Dict[str, str]:

        return {
            "api": url_for("item_notes",
                           note_id=note['note_id'],
                           item_id=item_id,
                           object_id=object_id,
                           project_id=project_id)
        }

    def delete(self, project_id, object_id):  # noqa: E501  pylint: disable=W0613,C0301
        item_id = int(request.args.get("item_id"))
        parent_object = middleware.ObjectMiddlwareEntity(self._provider)
        return parent_object.remove_item(object_id=object_id, item_id=item_id)


class ItemAPI(views.MethodView):
    WRITABLE_FIELDS = [
        "name",
        "medusa_uuid",
        "obj_sequence",
        "files"
    ]

    def __init__(self, provider: data_provider.DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.ItemDataConnector(provider.db_session_maker)

    @classmethod
    def create_changed_data(cls, json_request) -> Dict[str, Any]:

        new_item = dict()
        for field in cls.WRITABLE_FIELDS:
            if field == "obj_sequence":
                continue
            if field in json_request:
                new_item[field] = json_request.get(field)

        if "obj_sequence" in json_request:
            obj_sequence = json_request.get("obj_sequence")
            new_item["obj_sequence"] = int(obj_sequence)
        return new_item

    def put(self, item_id):
        json_request = request.json
        try:
            new_item = self.create_changed_data(json_request)

        except ValueError as reason:
            return make_response(
                "Cannot update item. Reason: {}".format(reason), 400)

        replacement_item = self._data_connector.update(
            item_id, changed_data=new_item
        )
        if not replacement_item:
            return make_response("", 204)
        return jsonify(
            {
                "item": replacement_item
            }
        )

    def get(self, item_id):
        item = self._data_connector.get(item_id, True)
        object_provider = data_provider.ObjectDataConnector(
            self._data_provider.db_session_maker)

        if 'parent_object_id' in item and item['parent_object_id'] is not None:
            parent_project = \
                object_provider.get(id=item['parent_object_id'],
                                    serialize=True)['parent_project_id']

            for f in item['files']:
                f['routes'] = {
                    "frontend": url_for("page_file_details",
                                        item_id=item['item_id'],
                                        object_id=item['parent_object_id'],
                                        project_id=parent_project,
                                        file_id=f["id"]),
                    "api": url_for("item_files",
                                   item_id=item['item_id'],
                                   object_id=item['parent_object_id'],
                                   project_id=parent_project, id=f["id"])

                }

        data = {
            "item": item
        }

        response = make_response(jsonify(data), 200)
        return response

    def delete(self, item_id):
        res = self._data_connector.delete(item_id)

        if res is True:
            return make_response("", 204)
        return make_response("", 404)
