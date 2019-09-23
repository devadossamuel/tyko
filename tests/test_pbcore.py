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
from tyko import pbcore, data_provider, scheme

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
    tyko.create_app(app)
    tyko.database.init_database(db.engine)
    app.config["TESTING"] = True
    with app.test_client() as server:
        my_db = data_provider.DataProvider(db.engine)
        my_mw = data_provider.ObjectDataConnector(my_db.db_session_maker)
        new_object_id = my_mw.create(name="my object")
        assert new_object_id == 1

        pbcore_data = pbcore.create_pbcore_from_object(object_id=new_object_id, data_provider=my_db)

        doc = etree.fromstring(bytes(pbcore_data, encoding="utf-8"))
        assert PBCORE_SCHEMA.validate(doc) is True, "Invalid Pbcore data. \n {}".format(pbcore_data)
