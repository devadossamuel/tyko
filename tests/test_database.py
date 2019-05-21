from avforms import database

import pytest


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


@pytest.fixture
def empty_database_session():
    engine = create_engine("sqlite:///:memory:")

    dummy_session = sessionmaker(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    session = dummy_session()
    yield session
    session.close()


def test_create_contact(empty_database_session):
    session = empty_database_session

    new_first_name = "John"
    new_last_name = "Smith"
    new_email = "jsmith@illinois.edu"

    assert len(session.query(database.Contact).all()) == 0

    new_contact = database.Contact()
    new_contact.first_name = new_first_name
    new_contact.last_name = new_last_name
    new_contact.email_address = new_email

    session.add(new_contact)

    session.commit()

    staff_in_database = session.query(database.Contact).all()
    assert len(staff_in_database) == 1

    assert staff_in_database[0].first_name == new_first_name
    assert staff_in_database[0].last_name == new_last_name
    assert staff_in_database[0].email_address == new_email


def test_create_collection(empty_database_session):
    session = empty_database_session

    collection_contact_first_name = "John"
    collection_contact_last_name = "Smith"
    collection_contact_email = "jsmith@illinois.edu"

    new_contact = database.Contact(
        first_name=collection_contact_first_name,
        last_name=collection_contact_last_name,
        email_address=collection_contact_email
    )

    record_series = "my_record series"
    collection_name = "my collection"
    collection_department = "my department"

    new_collection = database.Collection(
        record_series=record_series,
        collection_name=collection_name,
        department=collection_department,
        contact=new_contact
    )
    session.add(new_contact)
    session.add(new_collection)
    session.commit()

    # Check newly added record in collection
    collections = session.query(database.Collection).all()
    assert len(collections) == 1

    collection_in_db = collections[0]
    assert collection_in_db.collection_name == collection_name
    assert collection_in_db.department == collection_department
    assert collection_in_db.record_series == record_series

    assert collection_in_db.contact.first_name == collection_contact_first_name
    assert collection_in_db.contact.last_name == collection_contact_last_name
    assert collection_in_db.contact.email_address == collection_contact_email


