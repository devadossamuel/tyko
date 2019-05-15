from avforms import database

import pytest


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

@pytest.fixture
def dummy_database_session():
    engine = create_engine("sqlite:///:memory:")

    dummy_session = sessionmaker(bind=engine)
    database.Base.metadata.create_all(bind=engine)
    session = dummy_session()
    yield session
    session.close()


def test_create_preservation_staff(dummy_database_session):
    session = dummy_database_session

    new_first_name = "John"
    new_last_name = "Smith"
    new_email = "jsmith@illinois.edu"

    assert len(session.query(database.PreservationStaff).all()) == 0

    new_preservation_staff = database.PreservationStaff()
    new_preservation_staff.first_name = new_first_name
    new_preservation_staff.last_name = new_last_name
    new_preservation_staff.email_address = new_email

    session.add(new_preservation_staff)


    session.commit()

    staff_in_database = session.query(database.PreservationStaff).all()
    assert len(staff_in_database) == 1

    assert staff_in_database[0].first_name == new_first_name
    assert staff_in_database[0].last_name == new_last_name
    assert staff_in_database[0].email_address == new_email
