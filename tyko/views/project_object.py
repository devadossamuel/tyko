from flask import views, jsonify, make_response, url_for

from tyko import middleware


class ProjectObjectAPI(views.MethodView):
    def __init__(self, project: middleware.ProjectMiddlwareEntity) -> None:
        self._project = project

    def get(self, project_id, object_id):

        p = self._project.get_project_by_id(id=project_id)
        for o in p['objects']:
            if object_id == o['object_id']:
                for item in o['items']:
                    routes = {
                        "frontend": url_for(
                            "page_project_object_item_details",
                            project_id=project_id,
                            object_id=object_id,
                            item_id=item['item_id']
                        ),
                        "api": url_for(
                            "object_item",
                            project_id=project_id,
                            object_id=object_id,
                            item_id=item['item_id']
                        )
                    }
                    item['routes'] = routes
                return jsonify(
                    {
                        **o,
                        "parent_project_id": project_id
                    }
                )
        return make_response("no matching item", 404)

    def delete(self, project_id, object_id):
        return self._project.remove_object(project_id, object_id)


class ObjectApi(views.MethodView):
    def __init__(self,
                 object_middleware: middleware.ObjectMiddlwareEntity) -> None:

        self._object_middleware = object_middleware

    def delete(self, object_id: int):
        return self._object_middleware.delete(id=object_id)

    def get(self, object_id: int):
        return self._object_middleware.get(id=object_id)

    def put(self, object_id: int):
        return self._object_middleware.update(id=object_id)


class ProjectObjectNotesAPI(views.MethodView):

    def __init__(self,
                 project_object: middleware.ObjectMiddlwareEntity) -> None:

        self._project_object = project_object

    def delete(self, project_id, object_id, note_id):  # pylint: disable=W0613
        return self._project_object.remove_note(object_id, note_id)

    def put(self, project_id, object_id, note_id):  # pylint: disable=W0613
        return self._project_object.update_note(object_id, note_id)
