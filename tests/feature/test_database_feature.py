from avforms import database
from datetime import date

from pytest_bdd import scenario, given, then, when, parsers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SAMPLE_INSPECTION_NOTE = "This is a sample long form notes about the inspection"

SAMPLE_OBJ_SEQUENCE = 12

SAMPLE_DATE = date(1970, 1, 1)

SAMPLE_MEDUSA_ID = "ASDFASDF"

SAMPLE_FILE = "SampleFile.txt"

SAMPLE_BAR_CODE = "S4MP1384RC0D"

SAMPLE_ITEM_NAME = "Sample Item Name"

CONTACT_COLLECTION_EMAIL = "jsmith@illinois.edu"
CONTACT_COLLECTION_LAST_NAME = "Smith"
CONTACT_COLLECTION_FIRST_NAME = "John"

SAMPLE_RECORD_SERIES = "my_record series"
SAMPLE_COLLECTION_NAME = "my collection"
SAMPLE_DEPARTMENT = "my department"
SAMPLE_OBJECT_NAME = "sample object name"

SAMPLE_PROJECT_TITLE = "my sample project title"
SAMPLE_PROJECT_CODE = "my project code"
SAMPLE_PROJECT_SPECS = "project specs"
SAMPLE_PROJECT_STATUS = "ACTIVE"
SAMPLE_LOCATION = "my location"

SAMPLE_STAFF_CONTACT_EMAIL = "jsmith@illinois.edu"
SAMPLE_STAFF_CONTACT_LAST_NAME = "Smith"
SAMPLE_STAFF_CONTACT_FIRST_NAME = "John"


@scenario("database.feature", "Create a new user")
def test_database_feature():
    pass


@given("a blank database")
def dummy_database():
    engine = create_engine("sqlite:///:memory:")
    database.init_database(engine)

    dummy_session = sessionmaker(bind=engine)
    session = dummy_session()
    yield session
    session.close()


@given("a contact for a collection")
def collection_contact():
    new_contact = database.Contact(
        first_name=CONTACT_COLLECTION_FIRST_NAME,
        last_name=CONTACT_COLLECTION_LAST_NAME,
        email_address=CONTACT_COLLECTION_EMAIL
    )
    return new_contact


@when("the contact is added to the database")
def add_contact(dummy_database, collection_contact):
    dummy_database.add(collection_contact)
    dummy_database.commit()


@then("the collection contact can be found in the database")
def find_collection_contact(dummy_database):
    staff_in_database = dummy_database.query(database.Contact).all()

    assert staff_in_database[0].first_name == CONTACT_COLLECTION_FIRST_NAME
    assert staff_in_database[0].last_name == CONTACT_COLLECTION_LAST_NAME
    assert staff_in_database[0].email_address == CONTACT_COLLECTION_EMAIL


@scenario("database.feature", "Create a new collection")
def test_collection_feature():
    pass


@when("a new collection is created with a contact")
def new_collection(dummy_database, new_collection):
    dummy_database.add(new_collection)
    dummy_database.commit()
    return database_with_collection


@then("the new collection can be found in the database")
def find_collection(dummy_database):
    # Check newly added record in collection
    collections = dummy_database.query(database.Collection).all()
    assert len(collections) == 1


@then("the contact to the collection is expected value")
def expected_collection_contact(dummy_database):
    collection = dummy_database.query(database.Collection).first()
    contact = collection.contact
    assert contact.first_name == CONTACT_COLLECTION_FIRST_NAME
    assert contact.last_name == CONTACT_COLLECTION_LAST_NAME
    assert contact.email_address == CONTACT_COLLECTION_EMAIL


@scenario("database.feature", "Create a new project")
def test_database_project():
    pass


@scenario("database.feature", "Create a new object")
def test_database_object():
    pass


@given("a new collection")
def new_collection(dummy_database, collection_contact):
    dummy_database.add(collection_contact)
    dummy_database.commit()

    contact = dummy_database.query(database.Contact).first()
    new_collection = database.Collection(
        record_series=SAMPLE_RECORD_SERIES,
        collection_name=SAMPLE_COLLECTION_NAME,
        department=SAMPLE_DEPARTMENT,
        contact=contact

    )
    return new_collection


@given("a database with a collection")
def database_with_collection(dummy_database, new_collection):
    dummy_database.add(new_collection)
    dummy_database.commit()
    return dummy_database


@when("a object is added to the collection")
def add_new_object(dummy_database, create_new_object):
    dummy_database.add(create_new_object)
    dummy_database.commit()
    return dummy_database


@given("a new object for the collection created by the staff")
def create_new_object(dummy_database, new_collection, new_project, staff_contact):
    new_object = database.CollectionObject(
        name=SAMPLE_OBJECT_NAME,
        collection=new_collection,
        project=new_project,
        last_updated=staff_contact
    )
    return new_object


@given("a new Project")
def new_project(dummy_database):

    return database.Project(
        code=SAMPLE_PROJECT_CODE,
        title=SAMPLE_PROJECT_TITLE,
        current_location=SAMPLE_LOCATION,
        status=SAMPLE_PROJECT_STATUS,
        specs=SAMPLE_PROJECT_SPECS
    )


@when("the project is added to the collection")
def add_new_project(dummy_database, new_project):
    dummy_database.add(new_project)
    dummy_database.commit()
    return dummy_database


@then("the collection contains the new project")
def collection_has_project(dummy_database):

    new_added_project = dummy_database.query(database.Project).first()

    assert new_added_project.code == SAMPLE_PROJECT_CODE
    assert new_added_project.title == SAMPLE_PROJECT_TITLE
    assert new_added_project.current_location == SAMPLE_LOCATION
    assert new_added_project.specs == SAMPLE_PROJECT_SPECS


@given("a staff contact")
def staff_contact():
    return database.Contact(
        first_name=SAMPLE_STAFF_CONTACT_FIRST_NAME,
        last_name=SAMPLE_STAFF_CONTACT_LAST_NAME,
        email_address=SAMPLE_STAFF_CONTACT_EMAIL
    )


@then(parsers.parse("the database has {count:d} {data_type} records"))
def count_database_items(dummy_database, count, data_type):
    my_data_type = getattr(database, data_type)
    assert len(dummy_database.query(my_data_type).all()) == count


@scenario("database.feature", "Create a new item")
def test_newitem():
    pass


@given("a new item is created by the staff")
def new_item(dummy_database, new_collection, new_project, staff_contact,
             create_new_object):
    return database.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        barcode=SAMPLE_BAR_CODE,
        file_name=SAMPLE_FILE,
        medusa_uuid=SAMPLE_MEDUSA_ID,
        original_rec_date=SAMPLE_DATE,
        original_return_date=SAMPLE_DATE,
        collection_object=create_new_object,
        obj_sequence=SAMPLE_OBJ_SEQUENCE

    )


@when("a item is added to the object")
def add_item(dummy_database, new_item):
    dummy_database.add(new_item)
    dummy_database.commit()
    return dummy_database


@then("the new item record contains the correct barcode")
def item_has_correct_barcode(dummy_database):
    new_added_item = dummy_database.query(database.CollectionItem).first()
    assert new_added_item.barcode == SAMPLE_BAR_CODE


@scenario("database.feature", "Create a new note")
def test_database_note():
    pass


@given("a new inspection note is created")
def inspection_note(dummy_database):
    inspection_note = \
        dummy_database.query(database.NoteTypes).filter(
            database.NoteTypes.type_name == "Inspection").one()

    assert inspection_note.type_name == "Inspection"

    database.Note(
        text=SAMPLE_INSPECTION_NOTE,
        note_type=inspection_note

    )
