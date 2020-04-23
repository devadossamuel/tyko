from flask import views

from tyko import middleware


class ProjectNotesAPI(views.MethodView):

    def __init__(self, project: middleware.ProjectMiddlwareEntity) -> None:
        super().__init__()
        self._project = project

    def put(self, project_id, note_id):
        return self._project.update_note(project_id, note_id)

    def delete(self, project_id, note_id):
        return self._project.remove_note(project_id, note_id)


class ProjectsAPI(views.MethodView):
    def __init__(self, project: middleware.ProjectMiddlwareEntity) -> None:
        self._project = project

    def get(self):
        return self._project.get(True)


class ProjectAPI(views.MethodView):
    def __init__(self, project: middleware.ProjectMiddlwareEntity) -> None:
        self._project = project

    def put(self, project_id: int):
        return self._project.update(project_id)

    def delete(self, project_id: int):
        return self._project.delete(id=project_id)

    def get(self, project_id: int):
        return self._project.get(id=project_id)
