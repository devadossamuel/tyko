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
    def __init__(self, parent: middleware.ObjectMiddlwareEntity) -> None:
        self._parent_object = parent

    def delete(self, project_id, object_id, item_id):  # noqa: E501  pylint: disable=W0613,C0301
        return self._parent_object.remove_item(object_id=object_id,
                                               item_id=item_id)


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
