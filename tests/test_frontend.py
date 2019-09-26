from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytest
import tyko
import tyko.database

@pytest.fixture()
def app():
    app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(app)
    tyko.create_app(app)
    tyko.database.init_database(db.engine)
    app.config["TESTING"] = True
    return app


def test_view_web_object_empty(app):
    with app.test_client() as server:
        resulting_webpage = server.get("/object/1")
        assert resulting_webpage.status_code != 200


def test_view_web_object(app):
    with app.test_client() as server:
        server.post("/api/object/",
                    data={
                        "name": "my stupid object",
                        }
                    )
        resulting_webpage = server.get("/object/1")
        assert resulting_webpage.status_code == 200
        data = str(resulting_webpage.data, encoding="utf-8")
        assert "<td>my stupid object</td>" in data


def test_view_web_item(app):
    with app.test_client() as server:
        server.post("/api/item/",
                    data={
                        "name": "My dummy item",
                        "file_name": "dummy.txt",
                        "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4"
                    }
                )
        resulting_webpage = server.get("/item/1")
        assert resulting_webpage.status_code == 200
        data = str(resulting_webpage.data, encoding="utf-8")
        assert "<td>My dummy item</td>" in data
