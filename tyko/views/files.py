import flask.wrappers
from flask import views, request, url_for, jsonify, make_response

from tyko import data_provider
from tyko.data_provider import DataProvider


class ItemFilesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get(self, project_id, object_id, item_id):

        items_dp = data_provider.ItemDataConnector(
            self._data_provider.db_session_maker)

        item = items_dp.get(item_id, serialize=True)
        return jsonify({
            "files": item['files'],
            "total": len(item['files'])

        })

    def post(self, project_id, object_id, item_id):
        json_request = request.get_json()
        new_file_id = self._data_connector.create(
            item_id=item_id,
            file_name=json_request['file_name'],
            generation=json_request.get("generation")
        )['id']

        url = url_for("item_file_details",
                      project_id=project_id,
                      object_id=object_id,
                      item_id=item_id,
                      file_id=new_file_id
                      )

        return jsonify({
            "id": new_file_id,
            "url": url
        })


class FileAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get(self,
            project_id: int,
            object_id: int,
            item_id: int,
            file_id: int
            ) -> flask.wrappers.Response:
        return self._data_connector.get(file_id, serialize=True)

    def delete(self,
               project_id: int,
               object_id: int,
               item_id: int,
               file_id: int
               ) -> flask.wrappers.Response:

        self._data_connector.remove(item_id, file_id)
        res = self._data_connector.delete(file_id)
        if res is True:
            return make_response("", 202)
        return make_response("", 404)

    def put(self,
            project_id: int,
            object_id: int,
            item_id: int,
            file_id: int
            ) -> flask.wrappers.Response:

        json_request = request.get_json()
        return self._data_connector.update(file_id, changed_data=json_request)


class FileNoteAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def delete(self, file_id: int, note_id: int) -> flask.wrappers.Response:
        file_record = self._data_connector.remove_note(file_id, note_id)
        if file_record is True:
            return make_response("", 202)
        else:
            return make_response("Something went wrong", 500)

    def put(self, file_id: int, note_id: int) -> flask.wrappers.Response:
        json_request = request.get_json()
        changed_data = dict()
        changed_data['message'] = json_request['message']

        note_record = self._data_connector.edit_note(file_id, note_id, changed_data)
        return note_record


class FileNotesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get(self, file_id: int) -> flask.wrappers.Response:
        notes = self._data_connector.get(file_id, serialize=True)
        return jsonify({
            "notes": notes['notes'],
            "total": len(notes['notes'])
        })

    def post(self, file_id: int) -> flask.wrappers.Response:
        json_request = request.get_json()
        note_data = {
            "file_id": file_id,
            "message": json_request['message']

        }
        note_data_connector = \
            data_provider.FileNotesDataConnector(
                self._data_provider.db_session_maker)
        new_note = note_data_connector.create(**note_data)

        return jsonify(
            {
                "note": {
                    "url": {
                        "api": url_for("file_note",
                                       file_id=file_id,
                                       note_id=new_note['id']
                                       )
                    },
                    "id": new_note['id']
                }
             }
        )
