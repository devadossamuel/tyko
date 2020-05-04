from importlib.resources import read_text
from jinja2 import Template
from tyko.data_provider import DataProvider, ObjectDataConnector, \
    FilesDataConnector, ProjectDataConnector


def resolve_project_data(project_connector, unresolved_object: dict):
    project_id = unresolved_object.get("parent_project_id")
    if project_id is None:
        return None
    return project_connector.get(project_id, serialize=True)


def create_pbcore_from_object(object_id: int,
                              data_provider: DataProvider) -> str:
    template = Template(
        read_text("tyko.pbcore.templates", "pbcore.xml"),
        keep_trailing_newline=True
    )

    connector = ObjectDataConnector(data_provider.db_session_maker)
    resulting_object = connector.get(object_id, serialize=True)
    file_connector = FilesDataConnector(data_provider.db_session_maker)
    project_connector = ProjectDataConnector(data_provider.db_session_maker)
    resulting_object['project'] = resolve_project_data(project_connector, resulting_object)
    for item in resulting_object.get("items", []):
        item['files'] = resolve_files(file_connector, item)

    xml = template.render(
        obj=resulting_object,
        identifier_source="University of Illinois at Urbana-Champaign"
    )

    return xml


def resolve_files(file_connector, item):
    # The files comibg back aren't complete, get the rest of the metadata
    # before passing it on to the PBCore template
    resolved_files = []
    for item_file in item.get("files", []):
        file_id = item_file['id']
        res = file_connector.get(file_id, serialize=True)
        resolved_files.append(res)
    return resolved_files
