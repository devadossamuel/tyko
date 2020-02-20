import json
import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import tyko
import tyko.database


@pytest.fixture()
def app():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    return testing_app


def test_project_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/project/",
            data={
                "title": "my dumb project",
            }
        )
        assert post_resp.status_code == 200

        new_project_record = json.loads(post_resp.data)["url"]

        put_resp = server.put(
            new_project_record,
            data=json.dumps(
                {
                    "title": "my dumb project has changed"
                }
            ),
            content_type='application/json'
        )
        assert put_resp.status_code == 200


def test_item_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/item/",
            data={
                "name": "My dummy item",
                "file_name": "dummy.txt",
                "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4"
                }
            )
        assert post_resp.status_code == 200

        new_item_record_url = json.loads(post_resp.data)["url"]
        put_resp = server.put(
            new_item_record_url,
            data=json.dumps({
                "file_name": "changed_dummy.txt"
            }),
            content_type='application/json'
        )
        assert put_resp.status_code == 200
        put_resp_data = json.loads(put_resp.data)
        put_item = put_resp_data["item"]
        assert put_item["file_name"] == "changed_dummy.txt"

        get_resp = server.get(new_item_record_url)
        assert get_resp.status_code == 200

        edited_data = json.loads(get_resp.data)
        item = edited_data["item"]
        assert item["file_name"] == "changed_dummy.txt"
        assert item["medusa_uuid"] == "03de08f0-dada-0136-5326-0050569601ca-4"
        assert item["name"] == "My dummy item"


def test_item_delete(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/item/",
            data={
                "name": "My dummy item",
                "file_name": "dummy.txt",
                "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4"
                }
            )
        assert post_resp.status_code == 200

        new_item_record_url = json.loads(post_resp.data)["url"]

        get_resp = server.get(new_item_record_url)
        assert get_resp.status_code == 200

        delete_resp = server.delete(new_item_record_url)
        assert delete_resp.status_code == 204


def test_object_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/object/",
            data={
                "name": "My dummy object",
                "barcode": "12345",
                }
            )
        assert post_resp.status_code == 200

        new_object_record_url = json.loads(post_resp.data)["url"]

        put_resp = server.put(
            new_object_record_url,
            data=json.dumps({
                "name": "changed_dummy object"
            }),
            content_type='application/json'

        )

        assert put_resp.status_code == 200
        put_resp_data = json.loads(put_resp.data)
        put_item = put_resp_data["object"]
        assert put_item["name"] == "changed_dummy object"
        assert put_item["barcode"] == "12345"

        get_resp = server.get(new_object_record_url)
        assert get_resp.status_code == 200

        edited_data = json.loads(get_resp.data)
        get_object = edited_data["object"]
        assert get_object["name"] == "changed_dummy object"
        assert get_object["barcode"] == "12345"


def test_object_delete(app):
    with app.test_client() as server:
        post_resp = server.post(
            "/api/object/",
            data={
                "name": "My dummy object",
                "barcode": "12345",
                }
            )
        assert post_resp.status_code == 200

        new_record_url = json.loads(post_resp.data)["url"]

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200

        delete_resp = server.delete(new_record_url)
        assert delete_resp.status_code == 204


def test_note_create(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/notes/",
            data={
                "note_type_id": "3",
                "text": "MY dumb note",
                },
            )
        assert post_resp.status_code == 200
        new_record_id = json.loads(post_resp.data)["id"]

        get_all_notes = server.get(f"/api/notes")
        note_data = json.loads(get_all_notes.data)
        assert note_data['total'] == 1

        get_resp = server.get(f"/api/notes/{new_record_id}")
        note_data = json.loads(get_resp.data)
        assert note_data['note']["text"] == "MY dumb note"


def test_note_create_and_delete(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/notes/",
            data={
                "note_type_id": "3",
                "text": "MY dumb note",
                },
            )
        assert post_resp.status_code == 200
        new_record_url = json.loads(post_resp.data)["url"]

        get_all_notes = server.get(f"/api/notes")
        note_data = json.loads(get_all_notes.data)
        assert note_data['total'] == 1

        delete_resp=server.delete(new_record_url)
        assert delete_resp.status_code == 204

        get_all_notes_again = server.get(f"/api/notes")
        new_note_data = json.loads(get_all_notes_again.data)
        assert new_note_data['total'] == 0


def test_note_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/notes/",
            data={
                "note_type_id": "3",
                "text": "MY dumb note",
                }
            )
        assert post_resp.status_code == 200
        new_record_url = json.loads(post_resp.data)["url"]

        put_resp = server.put(
            new_record_url,
            data=json.dumps(
                {
                    "text": "My Note has changed"
                }
            ),
            content_type='application/json'

        )

        assert put_resp.status_code == 200
        newly_created_data = json.loads(put_resp.data)
        created_collection = newly_created_data["note"]
        assert created_collection["text"] == "My Note has changed"
        assert created_collection["note_type_id"] == 3


def test_create_new_project_note(app):
    with app.test_client() as server:

        project_post_resp = server.post(
            "/api/project/",
            data={
                "title": "my dumb project",
            }
        )

        assert project_post_resp.status_code == 200
        new_project_url = json.loads(project_post_resp.data)["url"]
        new_note_url = f"{new_project_url}/notes"
        note_post_resp = server.post(
            new_note_url,
            data=json.dumps({
                "note_type_id": "3",
                "text": "MY dumb note",
            }
            ),
            content_type='application/json'
        )

        assert note_post_resp.status_code == 200
        project_get_resp = server.get(new_project_url)
        assert project_get_resp.status_code == 200
        updated_project = \
            json.loads(project_get_resp.data)['project']
        project_notes = updated_project['notes']
        assert len(project_notes) == 1
        assert project_notes[0]['text'] == "MY dumb note"


def test_collection_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/collection/",
            data={
                "collection_name": "My dummy collection",
                "department": "preservation",
                }
            )
        assert post_resp.status_code == 200

        new_record_url = json.loads(post_resp.data)["url"]

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200
        newly_created_data = json.loads(get_resp.data)
        created_collection = newly_created_data["collection"]
        assert created_collection['collection_name'] == "My dummy collection"
        assert created_collection["department"] == "preservation"

        put_resp = server.put(
            new_record_url,
            data={
                "collection_name": "My changed dummy collection"
            }
        )

        assert put_resp.status_code == 200
        put_resp_data = json.loads(put_resp.data)
        put_item = put_resp_data["collection"]
        assert put_item["collection_name"] == "My changed dummy collection"
        assert put_item["department"] == "preservation"

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200

        edited_data = json.loads(get_resp.data)
        get_object = edited_data["collection"]
        assert get_object["collection_name"] == "My changed dummy collection"
        assert get_object["department"] == "preservation"


def test_collection_delete(app):
    with app.test_client() as server:
        post_resp = server.post(
            "/api/collection/",
            data={
                "collection_name": "My dummy collection",
                "department": "preservation",
                }
            )
        assert post_resp.status_code == 200

        new_record_url = json.loads(post_resp.data)["url"]

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200

        delete_resp = server.delete(new_record_url)
        assert delete_resp.status_code == 204


@pytest.fixture()
def server_with_project():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    with testing_app.test_client() as server:
        assert server.post(
            "/api/project/",
            data={
                "title": "my dumb project",
            },
            # FIXME: fix project api creation needs json
            # content_type='application/json'
        ).status_code == 200
        yield server


def test_add_object_to_project(server_with_project):
    project_api_url = "/api/project/1"
    new_object_api_url = f"{project_api_url}/object"

    post_new_object_project_resp = server_with_project.post(
        new_object_api_url,
        data=json.dumps({
            "name": "My dummy object",
            "barcode": "12345",
        }),
        content_type='application/json'
    )

    assert post_new_object_project_resp.status_code == 200
    new_object_data = json.loads(post_new_object_project_resp.data)['object']
    assert new_object_data["name"] == "My dummy object"

    project_resp = server_with_project.get(project_api_url)
    assert project_resp.status_code == 200
    data = json.loads(project_resp.data)['project']
    assert len(data['objects']) == 1
    assert data['objects'][0]['barcode'] == "12345"
