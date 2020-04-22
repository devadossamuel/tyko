import json
import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
import tyko
import tyko.database


@pytest.fixture()
def app():
    testing_app = Flask(__name__, template_folder="../tyko/templates")
    db = SQLAlchemy(testing_app)
    tyko.create_app(testing_app, verify_db=False)
    tyko.database.init_database(db.engine)
    testing_app.config["TESTING"] = True
    return testing_app


def test_project_create_and_delete(app):
    with app.test_client() as server:
        new_project_id = json.loads(server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                    "project_code": "my dumb project code",
                    "current_location": "old location",
                    "status": "No work done"
                }
            ),
            content_type='application/json'

        ).data)['id']
        delete_resp = server.delete(
            url_for("project", project_id=new_project_id)
        )
        assert delete_resp.status_code == 204


def test_project_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                    "project_code": "my dumb project code",
                    "current_location": "old location",
                    "status": "No work done"
                }
            ),
            content_type='application/json'

        )
        assert post_resp.status_code == 200

        new_project_record = json.loads(post_resp.data)["url"]

        put_resp = server.put(
            new_project_record,
            data=json.dumps(
                {
                    "title": "my dumb project has changed",
                    "project_code": "my dumb project code changed",
                    "current_location": "new location",
                    "status": "Complete"
                }
            ),
            content_type='application/json'
        )
        assert put_resp.status_code == 200
        updated_project = json.loads(put_resp.data)["project"]
        assert updated_project["title"] == "my dumb project has changed"
        assert updated_project["project_code"] == "my dumb project code changed"
        assert updated_project["current_location"] == "new location"
        assert updated_project["status"] == "Complete"


def test_item_update(app):

    with app.test_client() as server:

        post_resp = server.post(
            "/api/item/",
            data=json.dumps(
                {
                    "name": "My dummy item",
                    "files": [
                        {
                            "name": "dummy.txt",
                        }
                    ],
                    "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4",
                    "format_id": 2,
                }
            ),
            content_type='application/json'
        )
        assert post_resp.status_code == 200
        new_item_data = json.loads(post_resp.data)
        new_item_record_url = url_for("item", item_id=new_item_data['id'])
        put_resp = server.put(
            new_item_record_url,
            data=json.dumps({
                "name": "changed_dummy"
            }),
            content_type='application/json'
        )
        assert put_resp.status_code == 200
        get_resp = server.get(new_item_record_url)
        assert get_resp.status_code == 200
        #
        edited_data = json.loads(get_resp.data)
        item = edited_data["item"]
        assert item["medusa_uuid"] == "03de08f0-dada-0136-5326-0050569601ca-4"
        assert item["name"] == "changed_dummy"


def test_item_delete(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/item/",
            data=json.dumps(
                {
                    "name": "My dummy item",
                    "files": [
                        {
                            "name": "changed_dummy.txt",
                        }
                    ],
                    "medusa_uuid": "03de08f0-dada-0136-5326-0050569601ca-4",
                    "format_id": 1
                }
            ),
            content_type='application/json'
        )
        assert post_resp.status_code == 200
        data = json.loads(post_resp.data)

        new_item_record_url = url_for("item", item_id=data['id'])

        get_resp = server.get(new_item_record_url)
        assert get_resp.status_code == 200

        delete_resp = server.delete(new_item_record_url)
        assert delete_resp.status_code == 204


def test_object_add_note(app):
    with app.test_client() as server:
        project_id = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        ).get_json()["id"]

        new_object_id = server.post(
            url_for("project_add_object", project_id=project_id),
            data=json.dumps(
                {
                    "name": "My dummy object",
                    "barcode": "12345",
                }
            ),
            content_type='application/json'
        ).get_json()['object']["object_id"]

        new_object_note_resp = server.post(
            url_for("project_object_add_note",
                    project_id=project_id,
                    object_id=new_object_id),
            data=json.dumps(
                {
                    "note_type_id": "3",
                    "text": "MY dumb note",
                }
            ),
            content_type='application/json'
        )
        assert new_object_note_resp.status_code == 200
        new_note_data =new_object_note_resp.get_json()

        object_notes = server.get(
            url_for("object", object_id=new_object_id)
        ).get_json()['object']['notes']
        assert len(object_notes) == 1

        new_note_id = object_notes[0]['note_id']

        delete_resp =server.delete(
            url_for("object_notes",
                    project_id=project_id,
                    object_id=new_object_id,
                    note_id=new_note_id
                    )
        )
        assert delete_resp.status_code == 202

        notes_after_deleting = server.get(
            url_for("object", object_id=new_object_id)
        ).get_json()['object']['notes']

        assert len(notes_after_deleting) == 0


def test_object_update(app):

    with app.test_client() as server:

        collection_one_id = json.loads(server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "dumb collection",
                    "department": "dumb department",
                    "record_series": "dumb record series",
                }
            ),
            content_type='application/json'
        ).data)["id"]

        collection_two_id = json.loads(server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "dumb other collection",
                    "department": "dumb other department",
                    "record_series": "dumb other record series",
                }
            ),
            content_type='application/json'
        ).data)["id"]

        post_resp = server.post(
            "/api/object/",
            data=json.dumps(
                {
                    "name": "My dummy object",
                    "barcode": "12345",
                    "collection_id": collection_one_id,
                    "originals_rec_date": "2010-2-4",
                    "originals_return_date": "2012-2-4"
                }
            ),
            content_type='application/json'
            )
        assert post_resp.status_code == 200
        post_data = json.loads(post_resp.data)
        new_object_record_url = url_for("object", object_id=post_data['id'])

        put_resp = server.put(
            new_object_record_url,
            data=json.dumps({
                "name": "changed_dummy object",
                "barcode": "54321",
                "collection_id": collection_two_id,
                "originals_rec_date": "2010-01-04",
                "originals_return_date": "2012-05-04"
            }),
            content_type='application/json'

        )

        assert put_resp.status_code == 200
        put_resp_data = json.loads(put_resp.data)
        put_item = put_resp_data["object"]
        assert put_item["name"] == "changed_dummy object"
        assert put_item["barcode"] == "54321"

        get_resp = server.get(new_object_record_url)
        assert get_resp.status_code == 200

        edited_data = json.loads(get_resp.data)
        get_object = edited_data["object"]
        assert get_object["name"] == "changed_dummy object"
        assert get_object["name"] == "changed_dummy object"
        assert get_object["originals_rec_date"] == "2010-01-04"
        assert get_object["originals_return_date"] == "2012-05-04"
        assert get_object['collection']["collection_id"] == collection_two_id


def test_object_delete(app):
    with app.test_client() as server:
        post_resp = server.post(
            "/api/object/",
            data=json.dumps(
                {
                    "name": "My dummy object",
                    "barcode": "12345",
                }
            ),
            content_type='application/json'
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
            data=json.dumps(
                {
                    "note_type_id": "3",
                    "text": "MY dumb note",
                }
            ),
            content_type='application/json'
        )
        assert post_resp.status_code == 200
        new_record_id = json.loads(post_resp.data)["id"]

        get_all_notes = server.get(f"/api/notes")
        note_data = json.loads(get_all_notes.data)
        assert note_data['total'] == 1

        get_resp = server.get(url_for("note", note_id=new_record_id))
        note_data = json.loads(get_resp.data)
        assert note_data['note']["text"] == "MY dumb note"


def test_note_create_and_delete(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/notes/",
            data=json.dumps(
                {
                    "note_type_id": "3",
                    "text": "MY dumb note",
                }
            ),
            content_type='application/json'
            )
        assert post_resp.status_code == 200
        post_data = json.loads(post_resp.data)
        new_record_url = url_for("note", note_id=post_data['id'])

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
            data=json.dumps(
                {
                    "note_type_id": "3",
                    "text": "MY dumb note",
                }
            ),
            content_type='application/json'
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


def test_create_new_project_note_with_invalid_type(app):
    with app.test_client() as server:

        project_post_resp = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        )

        new_project_data = json.loads(project_post_resp.data)
        new_project_id = new_project_data["id"]

        note_post_resp = server.post(
            url_for("project_add_note", project_id=new_project_id),
            data=json.dumps({
                "note_type_id": "-3",
                "text": "MY dumb note",
            }
            ),
            content_type='application/json'
        )
        assert note_post_resp.status_code == 400


def test_create_new_project_note(app):
    with app.test_client() as server:

        project_post_resp = server.post(
            "/api/project/",
            data=json.dumps(
                {
                    "title": "my dumb project",
                }
            ),
            content_type='application/json'
        )

        assert project_post_resp.status_code == 200
        new_project_data = json.loads(project_post_resp.data)
        new_project_url = new_project_data["url"]
        new_note_url = f"{new_project_url}/notes"

        note_post_resp = server.post(
            new_note_url,
            data=json.dumps({
                "note_type_id": "3",
                "text": "MY dumb note",
            }),
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

        note_update_resp = server.put(
            url_for(
                "project_notes",
                project_id=new_project_data['id'],
                note_id=1
            ),
            data=json.dumps(
                {
                    "text": "MY dumb note changed",
                    "note_type_id": "1",
                }
            ),
            content_type='application/json'
        )
        assert note_update_resp.status_code == 200

        get_updated_note_resp = server.get(
            url_for("note", note_id=project_notes[0]['note_id'])
        )
        assert get_updated_note_resp.status_code == 200
        updated_note = get_updated_note_resp.get_json()['note']

        assert updated_note['text'] == "MY dumb note changed"
        assert updated_note["note_type_id"] == 1


def test_collection_update(app):

    with app.test_client() as server:
        post_resp = server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "My dummy collection",
                    "department": "preservation",
                    "record_series": "one"
                }
            ),
            content_type='application/json'
        )
        assert post_resp.status_code == 200
        post_resp_data = json.loads(post_resp.data)
        new_record_url = \
            url_for("collection", collection_id=post_resp_data['id'])

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200
        newly_created_data = json.loads(get_resp.data)
        created_collection = newly_created_data["collection"]
        assert created_collection['collection_name'] == "My dummy collection"
        assert created_collection["department"] == "preservation"

        put_resp = server.put(
            new_record_url,
            data=json.dumps(
                {
                    "collection_name": "My changed dummy collection",
                    "record_series": "two"
                }
            ),
            content_type='application/json'
        )

        assert put_resp.status_code == 200
        put_resp_data = json.loads(put_resp.data)
        put_item = put_resp_data["collection"]
        assert put_item["collection_name"] == "My changed dummy collection"
        assert put_item["department"] == "preservation"
        assert put_item["record_series"] == "two"

        get_resp = server.get(new_record_url)
        assert get_resp.status_code == 200

        edited_data = json.loads(get_resp.data)
        get_object = edited_data["collection"]
        assert get_object["collection_name"] == "My changed dummy collection"
        assert get_object["department"] == "preservation"

        update_2 = json.loads(
            server.put(
                new_record_url,
                data=json.dumps(
                    {
                        "department": "some other departments",
                    }
                ),
                content_type='application/json'
            ).data
        )['collection']
        assert update_2["department"] == "some other departments"


def test_collection_delete(app):
    with app.test_client() as server:
        post_resp = server.post(
            "/api/collection/",
            data=json.dumps(
                {
                    "collection_name": "My dummy collection",
                    "department": "preservation",
                }
            ),
            content_type='application/json'
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


def test_add_object_to_project(server_with_project):
    project_api_url = "/api/project/1"
    new_object_api_url = f"{project_api_url}/object"

    post_new_object_project_resp = server_with_project.post(
        new_object_api_url,
        data=json.dumps(
            {
                "name": "My dummy object",
                "barcode": "12345",
                "originals_rec_date": "2010-2-4"
            }
        ),
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


def test_add_and_delete_object_to_project(server_with_project):
    project_api_url = "/api/project/1"
    object_api_url = f"{project_api_url}/object"

    post_new_object_project_resp = server_with_project.post(
        object_api_url,
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

    new_object_id = new_object_data['object_id']
    new_object_api_url = f"{object_api_url}/{new_object_id}"

    delete_resp = server_with_project.delete(new_object_api_url)
    assert delete_resp.status_code == 202


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
        new_object_url = url_for("project_add_object", project_id=new_project_id)

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
        yield server


def test_add_and_delete_item_to_object(server_with_object):

    formats = dict()
    for format_type in server_with_object.get(url_for("formats")).get_json():
        formats[format_type['name']] = format_type['format_types_id']

    test_project_url = url_for("projects")
    test_project = \
        json.loads(server_with_object.get(test_project_url).data)['projects'][0]

    test_object = test_project['objects'][0]

    new_object_item_url = url_for("project_object_add_item",
                                  project_id=test_project['project_id'],
                                  object_id=test_object['object_id']
                                  )

    post_response = server_with_object.post(
        new_object_item_url,
        data=json.dumps(
            {
                "name": "My dummy item",
                "files": [
                    {
                        "name": "dummy.wav",
                    }
                ],
                "format_id": formats['audio']
            }
        ),
        content_type='application/json')

    assert post_response.status_code == 200, f"Failed reason {post_response.data}"

    new_item = json.loads(post_response.data)['item']
    assert new_item
    assert new_item['name'] == "My dummy item"
    assert new_item["files"][0]['name'] == "dummy.wav"
    assert new_item['format']['name'] == "audio"

    object_url = url_for(
        "object",
        object_id=test_object['object_id']
    )

    object_get_resp = server_with_object.get(object_url)
    object_data = json.loads(object_get_resp.data)['object']
    assert len(object_data['items']) == 1
    assert object_data['items'][0]['name'] == "My dummy item"

    item_api_url = url_for("object_item",
                           project_id=test_project['project_id'],
                           object_id=test_object['object_id'],
                           item_id=new_item['item_id']
                           )

    delete_response = server_with_object.delete(item_api_url)
    assert delete_response.status_code == 202

    items_after_deleted = \
        json.loads(server_with_object.get(object_url).data)['object']['items']
    assert len(items_after_deleted) == 0


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
        new_object_url = url_for("project_add_object", project_id=new_project_id)

        post_new_object_project_resp = server.post(
            new_object_url,
            data=json.dumps({
                "name": "My dummy object",
                "barcode": "12345",
                "collectionId": new_collection_id
            }),
            content_type='application/json'
        )
        new_object_id = json.loads(post_new_object_project_resp.data)['object']["object_id"]

        assert post_new_object_project_resp.status_code == 200
        new_item_url = url_for("project_object_add_item",
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


def test_create_and_get_file(server_with_object_and_item):
    projects = json.loads(
        server_with_object_and_item.get(url_for("projects")).data
    )["projects"]
    project_id = projects[0]['project_id']
    project = json.loads(
        server_with_object_and_item.get(
            url_for("project", project_id=project_id)
        ).data
    )['project']
    object_id = project['objects'][0]["object_id"]
    item_id = project['objects'][0]["items"][0]["item_id"]

    new_file_url = url_for("project_object_item_add_file",
                           project_id=project_id,
                           object_id=object_id,
                           item_id=item_id
                           )
    res = server_with_object_and_item.post(
        new_file_url,
        data=json.dumps({
            "file_name": "my_dumb_audio.wav",
        }),
        content_type='application/json'
    )
    assert res.status_code == 200
    new_file_res_data = json.loads(res.data)
    new_file_details_url = new_file_res_data['url']
    file_details_resp = server_with_object_and_item.get(new_file_details_url)
    assert file_details_resp.status_code == 200
    file_details_data = json.loads(file_details_resp.data)
    assert file_details_data['file_name'] == "my_dumb_audio.wav"


def test_update_file_name(server_with_object_and_item):
    projects = json.loads(
        server_with_object_and_item.get(url_for("projects")).data
    )["projects"]
    project = projects[0]
    project_id = project['project_id']
    object_id = project['objects'][0]["object_id"]
    item_id = project['objects'][0]["items"][0]["item_id"]
    new_file_url = url_for("project_object_item_add_file",
                           project_id=project_id,
                           object_id=object_id,
                           item_id=item_id
                           )

    file_id = json.loads(server_with_object_and_item.post(
        new_file_url,
        data=json.dumps({
            "file_name": "my_dumb_audio.wav",
        }),
        content_type='application/json'
    ).data)['id']

    new_file_route = url_for("item_file_details",
                             project_id=project_id,
                             object_id=object_id,
                             item_id=item_id,
                             file_id=file_id)

    put_res = server_with_object_and_item.put(
        new_file_route,
        data=json.dumps({
            "file_name": "my_dumb_changed_audio.wav"
        }),
        content_type='application/json'
    )
    assert put_res.status_code == 200

    # Get again and see if the data is changed
    get_res = server_with_object_and_item.get(
        new_file_route,
        content_type='application/json'
    )
    get_res_data = json.loads(get_res.data)
    assert get_res_data['file_name'] == "my_dumb_changed_audio.wav"


def test_create_and_delete_file(server_with_object_and_item):
    server = server_with_object_and_item
    projects = json.loads(
        server.get(url_for("projects")).data)["projects"]

    project_id = projects[0]['project_id']

    project = json.loads(
        server.get(url_for("project", project_id=project_id)).data)['project']

    object_id = project['objects'][0]["object_id"]
    item_id = project['objects'][0]["items"][0]["item_id"]

    new_file_url = url_for("project_object_item_add_file",
                           project_id=project_id,
                           object_id=object_id,
                           item_id=item_id
                           )
    res = server.post(
        new_file_url,
        data=json.dumps({
            "file_name": "my_dumb_audio.wav",
        }),
        content_type='application/json'
    )
    assert res.status_code == 200

#     check that item has file
    item = \
        json.loads(server.get(url_for("item", item_id=item_id)).data)['item']

    assert len(item['files']) == 1

    file_id = item['files'][0]['id']
    new_file_url = url_for("item_file_details", project_id=project_id, object_id=object_id, item_id=item_id, file_id=file_id)
    del_resp = server.delete(
        new_file_url
    )
    assert del_resp.status_code == 202


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


def test_create_and_delete_file_note(server_with_object_item_file):
    server, data = server_with_object_item_file

    file_id = data['file_id']

    file_notes_url = url_for("file_notes", file_id=file_id)
    new_note_resp = server.post(
        file_notes_url,
        data=json.dumps(
            {
                "message": "This file is silly"
            }
        ),
        content_type='application/json'
    )
    assert new_note_resp.status_code == 200
    new_note_api_url = json.loads(new_note_resp.data)['note']['url']['api']
    notes = json.loads(server.get(file_notes_url).data)['notes']
    assert len(notes) == 1
    del_resp = server.delete(new_note_api_url)
    assert del_resp.status_code == 202

    assert len(json.loads(server.get(file_notes_url).data)['notes']) == 0


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


def test_get_file_note(server_with_file_note):
    server, data = server_with_file_note
    file_notes_url = url_for("file_note",
                             project_id=data['project_id'],
                             object_id=data['object_id'],
                             file_id=data['file_id'],
                             note_id=data['note_id']
                             )
    get_resp = server.get(file_notes_url)
    assert get_resp.status_code == 200
    res_data = json.loads(get_resp.data)
    assert res_data['file_id'] == data['file_id']

def test_update_file_note(server_with_file_note):
    server, data = server_with_file_note

    file_notes_url = url_for("file_note",
                             project_id=data['project_id'],
                             object_id=data['object_id'],
                             file_id=data['file_id'],
                             note_id=data['note_id']
                             )

    update_resp = server.put(
        file_notes_url,
        data=json.dumps({
            "message": "New note message"
        }),
        content_type='application/json'
    )
    assert update_resp.status_code == 200
    assert json.loads(update_resp.data)["message"] == "New note message"


def test_create_and_delete_file_annotation_types(server_with_object_item_file):
    server, data = server_with_object_item_file
    file_annotation_types_url = url_for("file_annotation_types")

    new_annotation_type_get_resp = server.get(file_annotation_types_url)

    assert new_annotation_type_get_resp.status_code == 200

    new_annotation_type_data = json.loads(new_annotation_type_get_resp.data)
    assert len(new_annotation_type_data['annotation_types']) == 0
    assert new_annotation_type_data['total'] == 0

    new_annotation_type_resp = server.post(
        file_annotation_types_url,
        data=json.dumps({
            "text": "Audio Quality"

        }),
        content_type='application/json'
    )

    assert new_annotation_type_resp.status_code == 200

    new_annotation_type_resp_data = \
        json.loads(new_annotation_type_resp.data)

    new_annotation_type_after_adding_data = \
        json.loads(server.get(file_annotation_types_url).data)

    assert len(new_annotation_type_after_adding_data['annotation_types']) == 1
    assert new_annotation_type_after_adding_data['total'] == 1
    assert new_annotation_type_after_adding_data['annotation_types'][0]["name"] == "Audio Quality"

    file_annotation_type_url = \
        url_for("file_annotation_types", id=new_annotation_type_resp_data['fileAnnotationType']['id'])
    resp = server.delete(file_annotation_type_url)
    assert resp.status_code == 202

    assert json.loads(server.get(file_annotation_types_url).data)['total'] == 0


def test_create_and_delete_file_annotation(server_with_object_item_file):
    server, data = server_with_object_item_file

    file_id = data['file_id']
    file_annotation_types_url = url_for("file_annotation_types")
    new_annotation_type_resp = server.post(
        file_annotation_types_url,
        data=json.dumps({
            "text": "Audio Quality"

        }),
        content_type='application/json'
    )

    assert new_annotation_type_resp.status_code == 200

    new_annotation_type_data = json.loads(new_annotation_type_resp.data)['fileAnnotationType']

    assert isinstance(new_annotation_type_data["id"], int)

    file_annotations_url = url_for("file_annotations", file_id=file_id)
    new_annotation_resp = server.post(
        file_annotations_url,
        data=json.dumps(
            {
                "content": "This file is silly",
                "type_id": new_annotation_type_data["id"]
            }
        ),
        content_type='application/json'
    )
    assert new_annotation_resp.status_code == 200

    annotations = \
        json.loads(server.get(file_annotations_url).data)['annotations']

    assert len(annotations) == 1
    annotation_url = url_for("file_annotations", file_id=file_id, id=annotations[0]['id'])
    del_resp = server.delete(annotation_url)
    assert del_resp.status_code == 202
    assert len(json.loads(server.get(file_annotations_url).data)['annotations']) == 0
