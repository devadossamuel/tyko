from importlib.resources import read_text
from jinja2 import Template
from tyko.data_provider import DataProvider, ObjectDataConnector


def create_pbcore_from_object(object_id: int,
                              data_provider: DataProvider) -> str:
    template = Template(
        read_text("tyko.pbcore.templates", "pbcore.xml"),
        keep_trailing_newline=True
    )

    connector = ObjectDataConnector(data_provider.db_session_maker)
    resulting_object = connector.get(object_id, serialize=True)

    xml = template.render(
        name=resulting_object['name'],
        object_id=resulting_object['object_id'],
        parts=resulting_object['items'],
        notes=resulting_object['notes']
    )

    return xml
