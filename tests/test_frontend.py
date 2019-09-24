from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import tyko
import tyko.database


def test_view_web_object_empty():
    app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(app)
    tyko.create_app(app)
    tyko.database.init_database(db.engine)
    app.config["TESTING"] = True

    with app.test_client() as server:
        resulting_webpage = server.get("/object/1")
        assert resulting_webpage.status_code != 200


def test_view_web_object():
    app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(app)
    tyko.create_app(app)
    tyko.database.init_database(db.engine)
    app.config["TESTING"] = True

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
