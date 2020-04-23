from flask import views

from tyko import middleware


class ProjectObjectAPI(views.MethodView):
    def __init__(self, project: middleware.ProjectMiddlwareEntity) -> None:
        self._project = project

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
