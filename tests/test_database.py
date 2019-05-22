from avforms import database

import pytest


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

SAMPLE_OBJECT_NAME = "sample object name"

SAMPLE_PROJECT_STATUS = "ACTIVE"
SAMPLE_LOCATION = "my location"
SAMPLE_PROJECT_TITLE = "my sample project title"
SAMPLE_PROJECT_CODE = "my project code"
SAMPLE_PROJECT_SPECS = "project specs"
SAMPLE_DEPARTMENT = "my department"
SAMPLE_COLLECTION_NAME = "my collection"
SAMPLE_RECORD_SERIES = "my_record series"

CONTACT_EMAIL = "jsmith@illinois.edu"
CONTACT_LAST_NAME = "Smith"
CONTACT_FIRST_NAME = "John"

SAMPLE_STAFF_CONTACT_EMAIL = "jsmith@illinois.edu"
SAMPLE_STAFF_CONTACT_LAST_NAME = "Smith"
SAMPLE_STAFF_CONTACT_FIRST_NAME = "John"

Base = declarative_base()


@pytest.fixture
def empty_database_session():
    engine = create_engine("sqlite:///:memory:")

    dummy_session = sessionmaker(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    session = dummy_session()
    yield session
    session.close()


@pytest.fixture
def sample_contact():
    new_contact = database.Contact(
        first_name=CONTACT_FIRST_NAME,
        last_name=CONTACT_LAST_NAME,
        email_address=CONTACT_EMAIL
    )
    return new_contact


@pytest.fixture
def sample_staff_contact():
    new_contact = database.Contact(
        first_name=SAMPLE_STAFF_CONTACT_FIRST_NAME,
        last_name=SAMPLE_STAFF_CONTACT_LAST_NAME,
        email_address=SAMPLE_STAFF_CONTACT_EMAIL
    )
    return new_contact


@pytest.fixture
def database_with_contact(empty_database_session, sample_contact):
    session = empty_database_session
    session.add(sample_contact)
    session.commit()

    return empty_database_session


@pytest.fixture
def database_with_project(database_with_contact, sample_staff_contact):
    session = database_with_contact

    sample_contact_person = session.query(database.Contact).filter(
        database.Contact.first_name == CONTACT_FIRST_NAME).one()

    session.add(sample_staff_contact)

    new_project = database.Project(
        code=SAMPLE_PROJECT_CODE,
        title=SAMPLE_PROJECT_TITLE,
        contact=sample_contact_person,
        current_location=SAMPLE_LOCATION,
        project_status=SAMPLE_PROJECT_STATUS,
        specs=SAMPLE_PROJECT_SPECS
    )
    session.add(new_project)
    session.commit()
    assert len(session.query(database.Contact).all()) == 2
    return database_with_contact


@pytest.fixture
def sample_collection(sample_contact):
    new_collection = database.Collection(
        record_series=SAMPLE_RECORD_SERIES,
        collection_name=SAMPLE_COLLECTION_NAME,
        department=SAMPLE_DEPARTMENT,
        contact=sample_contact
    )
    return new_collection


def test_create_contact(empty_database_session):
    session = empty_database_session

    assert len(session.query(database.Contact).all()) == 0

    new_contact = database.Contact()
    new_contact.first_name = CONTACT_FIRST_NAME
    new_contact.last_name = CONTACT_LAST_NAME
    new_contact.email_address = CONTACT_EMAIL
    session.add(new_contact)

    session.commit()

    staff_in_database = session.query(database.Contact).all()
    assert len(staff_in_database) == 1

    assert staff_in_database[0].first_name == CONTACT_FIRST_NAME
    assert staff_in_database[0].last_name == CONTACT_LAST_NAME
    assert staff_in_database[0].email_address == CONTACT_EMAIL


def test_create_collection(empty_database_session, sample_contact):

    session = empty_database_session

    new_collection = database.Collection(
        record_series=SAMPLE_RECORD_SERIES,
        collection_name=SAMPLE_COLLECTION_NAME,
        department=SAMPLE_DEPARTMENT,
        contact=sample_contact
    )
    session.add(new_collection)
    session.add(sample_contact)
    session.commit()

    # Check newly added record in collection
    collections = session.query(database.Collection).all()
    assert len(collections) == 1

    collection_in_db = collections[0]
    assert collection_in_db.collection_name == SAMPLE_COLLECTION_NAME
    assert collection_in_db.department == SAMPLE_DEPARTMENT
    assert collection_in_db.record_series == SAMPLE_RECORD_SERIES

    assert collection_in_db.contact.first_name == CONTACT_FIRST_NAME
    assert collection_in_db.contact.last_name == CONTACT_LAST_NAME
    assert collection_in_db.contact.email_address == CONTACT_EMAIL


def test_create_project(database_with_contact, sample_staff_contact):
    session = database_with_contact
    contacts = session.query(database.Contact).all()
    assert len(contacts) == 1

    test_contact = contacts[0]

    session.add(sample_staff_contact)

    new_project = database.Project(
        code=SAMPLE_PROJECT_CODE,
        title=SAMPLE_PROJECT_TITLE,
        contact=test_contact,
        current_location=SAMPLE_LOCATION,
        project_status=SAMPLE_PROJECT_STATUS,
        specs=SAMPLE_PROJECT_SPECS
    )
    session.add(new_project)
    session.commit()

    projects = session.query(database.Project).all()
    assert len(projects) == 1
    my_added_project = projects[0]

    assert my_added_project.code == SAMPLE_PROJECT_CODE
    assert my_added_project.title == SAMPLE_PROJECT_TITLE
    assert my_added_project.project_status == SAMPLE_PROJECT_STATUS


def test_new_object(database_with_project, sample_collection):
    database_with_project.add(sample_collection)

    contacts = database_with_project.query(database.Contact).all()
    assert len(contacts) == 2

    collections = database_with_project.query(database.Collection).all()
    assert len(collections) == 1

    projects = database_with_project.query(database.Project).all()
    assert len(projects) == 1

    test_collection = collections[0]
    test_project = projects[0]

    new_object = database.CollectionObject(
        name=SAMPLE_OBJECT_NAME,
        collection=test_collection,
        project=test_project,
        last_updated=contacts[0]

    )

    database_with_project.add(new_object)
    database_with_project.commit()

    objects = database_with_project.query(database.CollectionObject).all()

    assert len(objects) == 1

    my_object = objects[0]

    assert my_object.name == SAMPLE_OBJECT_NAME
