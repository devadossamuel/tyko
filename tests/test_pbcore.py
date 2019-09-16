import pytest
import flask
import urllib.request
import os

from lxml import etree

import tyko
import tyko.exceptions
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
    empty_data_provider = data_provider.DataProvider("sqlite:///:memory:")

    with pytest.raises(tyko.exceptions.DataError):
        pbcore.create_pbcore_from_object(object_id=1, data_provider=empty_data_provider)


def test_pbcore_valid_id(tmpdir):
    temp_db_dir = str(tmpdir.mkdir("db"))
    TEMP_DATABASE = "sqlite:///{}/testdata.sqlite".format(temp_db_dir)

    app = flask.Flask(__name__, template_folder="../tyko/templates")
    tyko.create_app(TEMP_DATABASE, app, init_db=True)
    app.config["TESTING"] = True
    with app.test_client() as server:
        my_db = data_provider.DataProvider(TEMP_DATABASE)
        my_mw = data_provider.ObjectDataConnector(my_db.session)
        new_object_id = my_mw.create(name="my object")
        assert new_object_id == 1

        pbcore_data = pbcore.create_pbcore_from_object(object_id=new_object_id, data_provider=my_db)

        doc = etree.fromstring(pbcore_data)
        assert PBCORE_SCHEMA.validate(doc) is True, "Invalid Pbcore data. \n {}".format(pbcore_data)