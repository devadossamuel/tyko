import json

import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import tyko.database


@pytest.fixture()
def app():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app, verify_db=False)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    return testing_app


@pytest.fixture()
def server_with_project():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app, verify_db=False)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    with testing_app.test_client() as server:
        assert server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                },
            ),
            content_type='application/json'
        ).status_code == 200
        yield server


@pytest.fixture()
def server_with_object():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app, verify_db=False)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    with testing_app.test_client() as server:
        new_collection_response = server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "My dummy collection",
                    "department": "preservation",
                }
            ),
            content_type='application/json'
        )

        assert new_collection_response.status_code == 200
        new_collection_data = json.loads(new_collection_response.data)
        new_collection_id = new_collection_data['id']

        new_project_response = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        )
        assert new_project_response.status_code == 200
        new_project_data = json.loads(new_project_response.data)
        new_project_id = new_project_data['id']
        new_object_url = url_for("project_add_object",
                                 project_id=new_project_id)

        post_new_object_project_resp = server.post(
            new_object_url,
            data=json.dumps({
                "name": "My dummy object",
                "barcode": "12345",
                "collectionId": new_collection_id
            }),
            content_type='application/json'
        )
        assert post_new_object_project_resp.status_code == 200
        formats_response = server.get(url_for('formats'))
        assert formats_response.status_code == 200, formats_response.status

        format_types = {
            format_type["name"]: format_type
            for format_type in json.loads(formats_response.data)
        }

        data = {
            "collection": new_collection_data,
            "project": new_project_data,
            "object": json.loads(post_new_object_project_resp.data)['object'],
            "format_types": format_types,
        }
        yield server, data


@pytest.fixture()
def server_with_object_and_item():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app, verify_db=False)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    with testing_app.test_client() as server:
        new_collection_response = server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "My dummy collection",
                    "department": "preservation",
                }
            ),
            content_type='application/json'
        )

        assert new_collection_response.status_code == 200
        new_collection_id = json.loads(new_collection_response.data)['id']

        new_project_response = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        )
        assert new_project_response.status_code == 200
        new_project_id = json.loads(new_project_response.data)['id']
        new_object_url = url_for("project_add_object",
                                 project_id=new_project_id)

        post_new_object_project_resp = server.post(
            new_object_url,
            data=json.dumps({
                "name": "My dummy object",
                "barcode": "12345",
                "collectionId": new_collection_id
            }),
            content_type='application/json'
        )
        new_object_id = json.loads(post_new_object_project_resp.data)['object'][
            "object_id"]

        assert post_new_object_project_resp.status_code == 200
        new_item_url = url_for("object_item",
                               project_id=new_project_id,
                               object_id=new_object_id
                               )
        post_new_item = server.post(
            new_item_url,
            data=json.dumps({
                "name": "dummy object",
                "format_id": 2
            }),
            content_type='application/json'
        )
        assert post_new_item.status_code == 200
        yield server


@pytest.fixture()
def server_with_object_item_file(server_with_object_and_item):
    server = server_with_object_and_item

    projects = json.loads(
        server.get(url_for("projects")).data
    )["projects"]
    project_id = projects[0]['project_id']

    project = json.loads(
        server.get(url_for("project", project_id=project_id)).data)['project']

    object_id = project['objects'][0]["object_id"]
    item_id = project['objects'][0]["items"][0]["item_id"]

    new_file_url = url_for("project_object_item_add_file",
                           project_id=project_id,
                           object_id=object_id,
                           item_id=item_id)
    file_res = json.loads(server.post(
        new_file_url,
        data=json.dumps({
            "file_name": "my_dumb_audio.wav",
        }),
        content_type='application/json'
    ).data)
    file_id = file_res['id']
    data = {
        "project_id": project_id,
        "item_id": item_id,
        "object_id": object_id,
        "file_id": file_id
    }
    yield server, data


@pytest.fixture()
def server_with_file_note(server_with_object_item_file):
    server, data = server_with_object_item_file
    file_id = data['file_id']

    file_notes_url = url_for("file_notes", file_id=file_id)
    new_note = json.loads(
        server.post(
            file_notes_url,
            data=json.dumps(
                {
                    "message": "This file is silly"
                }
            ),
            content_type='application/json'
        ).data
    )
    data['note_id'] = new_note['note']['id']
    yield server, data


@pytest.fixture()
def server_with_cassette(server_with_enums):
    server, data = server_with_enums

    object_add_url = url_for(
        "object_item",
        project_id=data['project']['id'],
        object_id=data['object']['object_id']
    )

    new_item_resp = server.post(
        object_add_url,
        data=json.dumps({
            "name": "dummy",
            "format_id":
                data['format_types']['audio cassette']["format_types_id"],
            "format_details": {
                "format_type_id":
                    data['cassette_tape_formats']['compact cassette']['id'],
                "date_recorded": "11-26-1993",
                "inspection_date": "12-10-2019",
                "tape_thickness_id": data['tape_thicknesses'][0]['id'],
                'tape_type_id': data["cassette_tape_tape_types"][0]['id']

            }
        }),
        content_type='application/json'
    )
    assert new_item_resp.status_code == 200, new_item_resp.status
    new_item_data = json.loads(new_item_resp.data)
    new_item_data['item']['routes'] = new_item_data['routes']
    data['item'] = new_item_data['item']
    yield server, data


@pytest.fixture()
def server_with_enums(server_with_object):
    server, data = server_with_object

    # ===================== cassette_tape_tape_thickness ======================
    tape_thickness_values = [
        ({"unit": "mm", "value": "0.5"}),
        ({"unit": "mm", "value": "1.0"}),
        ({"unit": "mm", "value": "1.5"}),
        ({"unit": None, "value": "unknown"})
    ]
    tape_thickness_api_url = url_for("cassette_tape_tape_thickness")

    for tape_thickness in tape_thickness_values:
        resp = server.post(tape_thickness_api_url,
                           data=json.dumps(tape_thickness),
                           content_type='application/json'
                           )
        assert resp.status_code == 200, resp.status
    data["tape_thicknesses"] = json.loads(
        server.get(tape_thickness_api_url).data)

    # ====================== cassette_tape_format_types =======================
    formats = [
        "compact cassette",
        "DAT",
        "ADAT",
        "Other"

    ]
    cassette_tape_format_types_url = url_for("cassette_tape_format_types")
    for f in formats:
        new_cassette_type_resp = server.post(
            cassette_tape_format_types_url,
            data=json.dumps({
                "name": f
            }),
            content_type='application/json'
        )
        assert new_cassette_type_resp.status_code == 200, \
            new_cassette_type_resp.status
    cassette_tape_formats = {
        i['name']: i for i in json.loads(
            server.get(cassette_tape_format_types_url).data
        )
    }
    data["cassette_tape_formats"] = cassette_tape_formats

    # ========================== cassette_tape_tape_types ======================

    tape_tape_type_api_url = url_for("cassette_tape_tape_types")
    for value in ["I", "II", "IV"]:
        resp = server.post(tape_tape_type_api_url,
                           data=json.dumps({"name": value}),
                           content_type='application/json'
                           )
        assert resp.status_code == 200, resp.status

    data["cassette_tape_tape_types"] = json.loads(
        server.get(tape_tape_type_api_url).data)
    yield server, data
