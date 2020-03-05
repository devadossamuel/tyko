import json
import sys

from pyexpat import ExpatError

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import pytest
import tyko
import tyko.database
from tyko import frontend
from xml.dom.minidom import parseString


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
        project_id = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        ).get_json()['id']
        object_id = server.post(
            url_for("project_add_object", project_id=project_id),
            data=json.dumps(
                {
                    "name": "my stupid object",
                }
            ),
            content_type='application/json'
        ).get_json()['object']['object_id']
        # page_project_object_details
        resulting_webpage = server.get(
            url_for(
                "page_project_object_details",
                project_id=project_id,
                object_id=object_id
            )
        )
        assert resulting_webpage.status_code == 200
        data = str(
            resulting_webpage.data, encoding="utf-8")
        assert "my stupid object" in data


def test_view_web_item(app):
    with app.test_client() as server:
        project_id = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        ).get_json()['id']

        object_id = server.post(
            url_for("project_add_object", project_id=project_id),
            data=json.dumps(
                {
                    "name": "my stupid object",
                }
            ),
            content_type='application/json'
        ).get_json()['object']['object_id']
        new_item_rep = server.post(
            url_for(
                'project_object_add_item',
                project_id=project_id,
                object_id=object_id
            ),
            data=json.dumps(
                {
                    "name": "My dummy item",
                    "file_name": "dummy.txt",
                    "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4",
                    "format_id": 1
                }
            ),
            content_type='application/json'

        )
        assert new_item_rep.status_code == 200
        new_item_data = new_item_rep.get_json()['item']
        resulting_webpage = server.get(
            url_for(
                "page_project_object_item_details",
                project_id=project_id,
                object_id=object_id,
                item_id=new_item_data['item_id'])
        )
        assert resulting_webpage.status_code == 200
        data = str(resulting_webpage.data, encoding="utf-8")
        assert "My dummy item" in data


@pytest.fixture()
def breadcrumb_builder_with_project():
    builder = frontend.BreadcrumbBuilder()
    builder["Project"] = "http://127.0.0.1:5000/project/1"
    return builder


def test_breadcrumb_builder_len(breadcrumb_builder_with_project):
    assert len(breadcrumb_builder_with_project) == 1


def test_breadcrumb_builder_get_key(breadcrumb_builder_with_project):
    assert breadcrumb_builder_with_project["Project"] == "http://127.0.0.1:5000/project/1"


def test_breadcrumb_builder_iter(breadcrumb_builder_with_project):
    for v in breadcrumb_builder_with_project:
        assert v == ("Project", "http://127.0.0.1:5000/project/1")


def test_breadcrumb_builder_builds(breadcrumb_builder_with_project):
    breadcrumbs = breadcrumb_builder_with_project.build(active_level="Project")
    assert isinstance(breadcrumbs, list)
    assert len(breadcrumbs) == 1


def test_breadcrumb_builder_del(breadcrumb_builder_with_project):
    assert len(breadcrumb_builder_with_project) == 1
    del breadcrumb_builder_with_project["Project"]
    assert len(breadcrumb_builder_with_project) == 0
