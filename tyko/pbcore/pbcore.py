from importlib.resources import read_text
from jinja2 import Template
from tyko.data_provider import DataProvider, ObjectDataConnector


def create_pbcore_from_object(object_id: int,
                              data_provider: DataProvider) -> str:
    template = Template(read_text("tyko.pbcore.templates", "pbcore.xml"))

    connector = ObjectDataConnector(data_provider.session)
    resulting_object = connector.get(object_id)[0]

    xml = template.render(
        name=resulting_object.name,
        object_id=resulting_object.id)

    return xml
