import functools
import flask.wrappers
from flask import views, request, url_for, jsonify, make_response

from tyko import data_provider
from tyko.data_provider import DataProvider


class ItemFilesAPI(views.MethodView):
    class Decorators:  # pylint: disable=too-few-public-methods
        @classmethod
        def validate(cls, func):
            @functools.wraps(func)
            def wrapper(self, project_id, object_id, item_id):
                file_id = int(request.args['id'])

                if self._has_matching_file(project_id, object_id,  # noqa: E501 pylint: disable=W0212
                                           item_id, file_id) is False:
                    raise AttributeError("Record mismatch")
                return func(self, project_id, object_id, item_id)

            return wrapper

    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FilesDataConnector(provider.db_session_maker)

    def get_by_id(self, file_id):
        return self._data_connector.get(int(file_id), serialize=True)

    @Decorators.validate
    def get(self, project_id, object_id, item_id) -> flask.Response:  # noqa: E501 pylint: disable=W0613
        file_id = request.args.get("id")
        if file_id is not None:
            return self.get_by_id(int(file_id))
        return self.get_all(item_id)

    def get_all(self, item_id):
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

        url = url_for("item_files",
                      project_id=project_id,
                      object_id=object_id,
                      item_id=item_id,
                      id=new_file_id
                      )

        return jsonify({
            "id": new_file_id,
            "url": url
        })

    @Decorators.validate
    def put(self, project_id, object_id, item_id) -> flask.Response:  # noqa: E501 pylint: disable=W0613
        file_id = int(request.args['id'])
        json_request = request.get_json()
        return self._data_connector.update(file_id,
                                           changed_data=json_request)

    @Decorators.validate
    def delete(self, project_id, object_id, item_id) -> flask.Response:  # noqa: E501 pylint: disable=W0613
        file_id = int(request.args['id'])

        self._data_connector.remove(item_id, file_id)
        res = self._data_connector.delete(file_id)
        if res is True:
            return make_response("", 202)
        return make_response("", 404)

    def _has_matching_file(self,
                           project_id: int,
                           object_id: int,
                           item_id: int,
                           file_id: int
                           ) -> bool:
        """Check if there is a matching file that matches all the ids"""

        project_connector = data_provider.ProjectDataConnector(
            self._data_provider.db_session_maker)
        item_connector = data_provider.ItemDataConnector(
            self._data_provider.db_session_maker)

        project = project_connector.get(project_id, serialize=True)

        for obj in filter(lambda obj: obj['object_id'] == object_id,
                          project['objects']):
            for item in filter(lambda i: i['item_id'] == item_id,
                               obj['items']):

                matching_files = list(
                    filter(lambda f: f['id'] == file_id, item_connector.get(
                        item['item_id'], serialize=True)['files']))
                return len(matching_files) == 1

        return False


class FileNotesAPI(views.MethodView):
    def __init__(self, provider: DataProvider) -> None:
        self._data_provider = provider
        self._data_connector = \
            data_provider.FileNotesDataConnector(provider.db_session_maker)

    def get(self, file_id: int) -> flask.Response:
        note_id = request.args.get("id")
        if note_id is not None:
            return self.get_one_by_id(file_id, int(note_id))
        return self.get_all(file_id)

    def get_one_by_id(self, file_id, note_id):
        if self._file_has_matching_note(file_id, note_id) is False:
            raise AttributeError(
                f"File {file_id} has no note with id {note_id}")

        return self._data_connector.get(note_id, serialize=True)

    def get_all(self, file_id):
        data_connector = \
            data_provider.FilesDataConnector(
                self._data_provider.db_session_maker)

        notes = data_connector.get(file_id, serialize=True)
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
        new_note = self._data_connector.create(**note_data)

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
        note_id = int(request.args["id"])

        if self._file_has_matching_note(file_id, note_id) is False:
            raise AttributeError(
                f"File {file_id} has no note with id {note_id}")

        json_request = request.get_json()
        changed_data = dict()
        changed_data['message'] = json_request['message']
        return self._data_connector.update(note_id, changed_data)

    def _file_has_matching_note(self, file_id: int, note_id: int) -> bool:
        provider = data_provider.FilesDataConnector(
            self._data_provider.db_session_maker)

        matching_file = provider.get(file_id, serialize=True)
        for note in matching_file['notes']:
            if note['id'] == note_id:
                return True
        return False

    def delete(self, file_id: int) -> flask.Response:
        note_id = int(request.args["id"])
        if self._file_has_matching_note(file_id, note_id) is False:
            raise AttributeError(
                f"File {file_id} has no note with id {note_id}")

        note_data_connector = \
            data_provider.FileNotesDataConnector(
                self._data_provider.db_session_maker)
        file_record = note_data_connector.delete(note_id)
        if file_record is True:
            return make_response("", 202)
        return make_response("Something went wrong when trying to remove note",
                             500)


class FileAnnotationsAPI(views.MethodView):
    class Decorators:  # pylint: disable=too-few-public-methods
        @classmethod
        def validate(cls, func):
            @functools.wraps(func)
            def wrapper(self, file_id, *args, **kwargs):
                annotation_id = request.args.get('id')
                if annotation_id:
                    connector = data_provider.FileAnnotationsConnector(
                        self._data_provider.db_session_maker)  # noqa: E501 pylint: disable=W0212
                    annotation = connector.get(annotation_id, serialize=True)
                    if annotation['file_id'] != file_id:
                        raise AttributeError(
                            "File id does not match annotation id")
                return func(self, file_id, *args, **kwargs)

            return wrapper

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

    @Decorators.validate
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

    @Decorators.validate
    def delete(self, file_id: int) -> flask.Response:  # pylint: disable=W0613
        annotation_id = request.args['id']
        connector = data_provider.FileAnnotationsConnector(
            self._data_provider.db_session_maker)

        successfully_deleted = connector.delete(annotation_id)
        if successfully_deleted is True:
            return make_response("", 202)
        return make_response(
            "Something went wrong trying to delete file annotation", 500)

    @Decorators.validate
    def put(self, file_id: int) -> flask.Response:  # pylint: disable=W0613
        annotation_id = request.args["id"]
        json_request = request.get_json()
        changed_data = {
            'content': json_request.get('content'),
            'type_id': int(json_request.get('type_id')),
        }
        connector = data_provider.FileAnnotationsConnector(
            self._data_provider.db_session_maker)
        return connector.update(annotation_id, changed_data)


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
        return make_response("Something went wrong trying to remove file "
                             "annotation type", 500)

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
