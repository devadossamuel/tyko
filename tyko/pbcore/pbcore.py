from importlib.resources import read_text
from jinja2 import Template
from tyko.data_provider import DataProvider, ObjectDataConnector, \
    FilesDataConnector


def create_pbcore_from_object(object_id: int,
                              data_provider: DataProvider) -> str:
    template = Template(
        read_text("tyko.pbcore.templates", "pbcore.xml"),
        keep_trailing_newline=True
    )

    connector = ObjectDataConnector(data_provider.db_session_maker)
    resulting_object = connector.get(object_id, serialize=True)
    file_connector = FilesDataConnector(data_provider.db_session_maker)

    for item in resulting_object.get("items", []):
        # The files comibg back aren't complete, get the rest of the metadata
        # before passing it on to the PBCore template
        resolved_files = []

        for item_file in item.get("files", []):
            file_id = item_file['id']
            res = file_connector.get(file_id, serialize=True)
            resolved_files.append(res)
        item['files'] = resolved_files

    xml = template.render(
        obj=resulting_object
    )

    return xml
