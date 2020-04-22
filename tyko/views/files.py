import flask.wrappers
from flask import views, request, url_for, jsonify, make_response

from tyko import data_provider
from tyko.data_provider import DataProvider


class ItemFilesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get(self, project_id, object_id, item_id) -> flask.Response:

        items_dp = data_provider.ItemDataConnector(
            self._data_provider.db_session_maker)

        item = items_dp.get(item_id, serialize=True)
        return jsonify({
            "files": item['files'],
            "total": len(item['files'])

        })

    def post(self, project_id, object_id, item_id) -> flask.Response:
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
            ) -> flask.Response:
        return self._data_connector.get(file_id, serialize=True)

    def delete(self,
               project_id: int,
               object_id: int,
               item_id: int,
               file_id: int
               ) -> flask.Response:

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
            ) -> flask.Response:

        json_request = request.get_json()
        return self._data_connector.update(file_id, changed_data=json_request)


class FileNotesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get(self, file_id: int) -> flask.Response:
        note_id = request.args.get("id")
        if note_id is not None:
            return self.get_one_by_id(file_id, note_id)
        return self.get_all(file_id)

    def get_one_by_id(self, file_id, note_id):
        dc = data_provider.FileNotesDataConnector(
            self._data_provider.db_session_maker)

        res = dc.get(note_id, serialize=True)
        return res

    def get_all(self, file_id):
        notes = self._data_connector.get(file_id, serialize=True)
        return jsonify({
            "notes": notes['notes'],
            "total": len(notes['notes'])
        })

    def post(self, file_id: int) -> flask.Response:
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
                        "api": url_for("file_notes",
                                       file_id=file_id,
                                       id=new_note['id']
                                       )
                    },
                    "id": new_note['id']
                }
            }
        )

    def put(self, file_id: int) -> flask.Response:
        note_id = request.args["id"]
        json_request = request.get_json()
        changed_data = dict()
        changed_data['message'] = json_request['message']

        note_record = \
            self._data_connector.edit_note(file_id, note_id, changed_data)

        return note_record

    def delete(self, file_id: int) -> flask.Response:
        note_id = int(request.args["id"])
        file_record = self._data_connector.remove_note(file_id, note_id)
        if file_record is True:
            return make_response("", 202)
        return make_response("Something went wrong", 500)


class FileAnnotationsAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider

    def get(self, file_id: int) -> flask.Response:
        file_connector = data_provider.FilesDataConnector(
            self._data_provider.db_session_maker)
        res = file_connector.get(file_id, serialize=True)

        return jsonify({
            "annotations": res['annotations'],
            "total": len(res['annotations'])
        })

    def post(self, file_id: int) -> flask.Response:
        json_request = request.get_json()
        annotation_connector = \
            data_provider.FileAnnotationsConnector(
                self._data_provider.db_session_maker)
        new_annotation_id = annotation_connector.create(
            file_id=file_id,
            content=json_request['content'],
            annotation_type_id=json_request['type_id']
        )
        return jsonify({
            "fileAnnotation": {
                "id": new_annotation_id,
                "url": {
                    "api": url_for("file_annotations",
                                   file_id=file_id,
                                   annotation_id=new_annotation_id)
                }
            },
        })

    def delete(self, file_id: int) -> flask.Response:
        annotation_id = request.args['id']
        connector = data_provider.FileAnnotationsConnector(
            self._data_provider.db_session_maker)

        annotation = connector.get(annotation_id, serialize=True)

        if annotation['file_id'] != file_id:
            return make_response("File id does not match annotation id", 400)

        successfully_deleted = connector.delete(annotation_id)
        if successfully_deleted is True:
            return make_response("", 202)
        return make_response("Something went wrong", 500)

    def put(self, file_id: int) -> flask.Response:
        annotation_id = request.args["id"]
        json_request = request.get_json()
        changed_data = {
            'content': json_request.get('content'),
            'type_id': int(json_request.get('type_id')),
        }
        return self._connector.update(annotation_id, changed_data)


class FileAnnotationTypesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider

    def get(self) -> flask.Response:
        connector = data_provider.FileAnnotationsConnector(
            self._data_provider.db_session_maker)
        all_types = connector.get(serialize=True)
        return jsonify({
            "annotation_types": all_types,
            "total": len(all_types)
        })

    def delete(self) -> flask.Response:
        annotation_id = request.args["id"]
        connector = data_provider.FileAnnotationTypeConnector(
            self._data_provider.db_session_maker)
        successful = connector.delete(annotation_id)
        if successful is True:
            return make_response("", 202)
        return make_response("Something went wrong", 500)

    def post(self) -> flask.Response:
        json_request = request.get_json()
        annotation_connector = \
            data_provider.FileAnnotationTypeConnector(
                self._data_provider.db_session_maker)

        new_annotation_type = \
            annotation_connector.create(text=json_request['text'])

        return jsonify({
            "fileAnnotationType": {
                "id": new_annotation_type['type_id'],
                "url": url_for("file_annotation_types",
                               id=new_annotation_type['type_id'])
                }
        })
