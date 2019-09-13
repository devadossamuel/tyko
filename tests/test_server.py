import tyko
from tyko import routes, data_provider
import tyko.database
import sqlalchemy
from tyko.database import init_database
import pytest
import json
from flask import Flask

static_page_routes = [
    "/",
    "/about",
]

dynamic_page_routes = [
    "/collection",
    "/project",
    "/format",
    "/item",
]

api_routes = [
    "/api",
    "/api/format",
    "/api/project",
    "/api/collection",
    "/api/item",
    "/api/object",


]

TEMP_DATABASE = "sqlite:///:memory:"


@pytest.mark.parametrize("route", static_page_routes)
def test_static_pages(route):
    app = tyko.create_app(TEMP_DATABASE)
    app.config["TESTING"] = True
    with app.test_client() as server:
        resp = server.get(route)
        assert resp.status == "200 OK"


@pytest.mark.parametrize("route", dynamic_page_routes)
def test_dynamic_pages(route):
    app = Flask(__name__, template_folder="../tyko/templates")
    tyko.create_app(TEMP_DATABASE, app, init_db=True)
    app.config["TESTING"] = True
    with app.test_client() as server:
        resp = server.get(route)
        assert resp.status == "200 OK"


@pytest.fixture(scope="module")
def test_app():
    app = Flask(__name__, template_folder="../tyko/templates")
    tyko.create_app(TEMP_DATABASE, app, init_db=True)
    app.config["TESTING"] = True
    return app.test_client()


def test_api_formats(test_app):
    resp = test_app.get("/api/format")
    assert resp.status == "200 OK"
    tmp_data = json.loads(resp.data)

    for k, v in tyko.scheme.format_types.items():
        for entry in tmp_data:
            if entry["name"] == k:
                assert entry["id"] == v[0]
                break
        else:
            assert False


@pytest.mark.parametrize("route", api_routes)
def test_api_routes(route):
    app = Flask(__name__, template_folder="../tyko/templates")
    tyko.create_app(TEMP_DATABASE, app, init_db=True)
    app.config["TESTING"] = True
    with app.test_client() as server:
        resp = server.get(route)
        assert resp.status == "200 OK"

def test_create(test_app):
    resp = test_app.post(
        "/api/project/",
        data={
            "title": "dummy title",
            "project_code": "sample project code",
            "status": "inactive",
            "specs": "asdfadsf"
        }
    )
    assert resp.status_code == 200
    tmp_data = json.loads(resp.data)

    assert tmp_data["id"] is not None
    assert tmp_data["url"] is not None


test_data_read = [
    (
        "project", {
            "title": "dummy title",
            "project_code": "sample project code",
            "status": "inactive"
        }
     ),
    (
        "collection", {
            "collection_name": "Silly collection name",
            "department": "my department"
        }

    ),
    (
        "item", {
            "name": "my stupid new item",
            "barcode": "8umb",
            "file_name": "stupid.mov"
        }
    ),
    (
        "object", {
            "name": "my stupid object"
        }
    )
]


@pytest.mark.parametrize("data_type,data_value", test_data_read)
def test_create_and_read2(data_type, data_value):

    app = Flask(__name__, template_folder="../tyko/templates")
    tyko.create_app(TEMP_DATABASE, app, init_db=True)
    app.config["TESTING"] = True
    with app.test_client() as server:
        route ="/api/{}/".format(data_type)
        create_resp = server.post(
            route,
            data=data_value)

        assert create_resp.status == "200 OK", "Failed to create a new entity with {}".format(route)

        new_id = json.loads(create_resp.data)["id"]
        assert new_id is not None

        read_res = server.get("/api/{}/{}".format(data_type, new_id))
        assert read_res.status_code == 200 , "{} failed with status {}".format(route, read_res.status_code)

        read_resp_data = json.loads(read_res.data)
        data_object = read_resp_data[data_type][0]

        for k, v in data_value.items():
            assert data_object[k] == v

def test_empty_database_error():
    # Creating a server without a validate database should raise a DataError
    # exception

    with pytest.raises(data_provider.DataError):
        empty_data_provider = data_provider.DataProvider(TEMP_DATABASE)
        empty_data_provider.get_formats()
