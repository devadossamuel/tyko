import json

import pytest
import flask
import sqlalchemy
import urllib.request
import os

from flask_sqlalchemy import SQLAlchemy
from lxml import etree

import tyko
import tyko.exceptions
import tyko.database
from tyko import pbcore, data_provider, schema

PBCORE_XSD_URL = "https://raw.githubusercontent.com/PBCore-AV-Metadata/PBCore_2.1/master/pbcore-2.1.xsd"
if os.path.exists("pbcore-2.1.xsd"):
    with open("pbcore-2.1.xsd", "r") as f:
        PBCORE_XSD = f.read()
else:
    with urllib.request.urlopen(PBCORE_XSD_URL) as f:
        assert f.code == 200
        PBCORE_XSD = str(f.read(), encoding="utf8")
        with open("pbcore-2.1.xsd", "w") as wf:
            wf.write(PBCORE_XSD)

assert PBCORE_XSD is not None
xsd = etree.XML(PBCORE_XSD)
PBCORE_SCHEMA = etree.XMLSchema(xsd)



def test_pbcore_fail_invalid_id():
    db = sqlalchemy.create_engine("sqlite:///:memory:")
    empty_data_provider = data_provider.DataProvider(db)

    with pytest.raises(tyko.exceptions.DataError):
        pbcore.create_pbcore_from_object(object_id=1, data_provider=empty_data_provider)


def test_pbcore_valid_id(tmpdir):
    app = flask.Flask(__name__, template_folder="../tyko/"
                                                "templates")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db = SQLAlchemy(app)
    tyko.create_app(app, verify_db=False)
    tyko.database.init_database(db.engine)
    app.config["TESTING"] = True
    with app.test_client() as server:
        sample_collection = server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "My dummy collection",
                    "department": "preservation",
                }
            ),
            content_type='application/json'
        ).get_json()

        sample_project = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        ).get_json()

        sample_object = server.post(
            flask.url_for("project_add_object", project_id=sample_project['id']),
            data=json.dumps(
                {
                    "name": "My dummy object",
                    "collectionId": sample_collection['id']
                }
            ),
            content_type='application/json'
        ).get_json()['object']

        sample_item = server.post(
            flask.url_for(
                "object_item",
                project_id=sample_project['id'],
                object_id=sample_object['object_id']
            ),
            data=json.dumps(
                {
                    "name": "My dummy item",
                    "format_id": 1
                }
            ),
            content_type='application/json'
        ).get_json()



        pbcore_xml = server.get(
            flask.url_for("object_pbcore", id=sample_object['object_id'])
        ).get_data()
        doc = etree.fromstring(pbcore_xml)
        print(str(etree.tostring(doc, pretty_print=True), encoding="utf-8"))
        assert PBCORE_SCHEMA.validate(doc) is True, PBCORE_SCHEMA.error_log.filter_from_errors().last_error.message
