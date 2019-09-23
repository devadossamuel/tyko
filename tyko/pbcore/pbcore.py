from importlib.resources import read_text
from jinja2 import Template
from tyko.data_provider import DataProvider, ObjectDataConnector
from tyko.exceptions import DataError


def create_pbcore_from_object(object_id: int,
                              data_provider: DataProvider) -> str:
    template = Template(read_text("tyko.pbcore.templates", "pbcore.xml"))

    connector = ObjectDataConnector(data_provider.session)
    resulting_objects = connector.get(object_id)
    if len(resulting_objects) == 0:
        raise DataError("Invalid object id")
    xml = template.render(
        name=resulting_objects[0].name,
        object_id=resulting_objects[0].id)

    return xml
