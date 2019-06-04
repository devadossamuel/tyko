from avforms import database
from datetime import date

from pytest_bdd import scenario, given, then, when, parsers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SAMPLE_TREATMENT_GIVEN = "This item got only y treatment"

SAMPLE_TREATMENT_NEEDED = "This item needs x, y, and z treatment"

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


@given(parsers.parse("a new object for the collection "
                     "created by {staff_first_name} {staff_last_name}"))
def create_new_object(dummy_database, new_collection, new_project,
                      staff_first_name, staff_last_name):

    all_contacts = dummy_database.query(database.Contact)

    staff_contact = \
        all_contacts.filter(
            database.Contact.last_name == staff_last_name,
            database.Contact.first_name == staff_first_name
        ).one()

    assert staff_contact.last_name == staff_last_name
    assert staff_contact.first_name == staff_first_name

    new_object = database.CollectionObject(
        name=SAMPLE_OBJECT_NAME,
        collection=new_collection,
        project=new_project,
        last_updated=staff_contact,
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


@given(parsers.parse(
    "a staff contact named {staff_first_name} {staff_last_name}"))
def staff_contact(dummy_database, staff_first_name, staff_last_name):
    new_contact = database.Contact(
        first_name=staff_first_name,
        last_name=staff_last_name,
        email_address=SAMPLE_STAFF_CONTACT_EMAIL
    )
    dummy_database.add(new_contact)
    return new_contact


@then(parsers.parse("the database has {count:d} {data_type} records"))
def count_database_items(dummy_database, count, data_type):
    my_data_type = getattr(database, data_type)
    assert len(dummy_database.query(my_data_type).all()) == count


@scenario("database.feature", "Create a new item")
def test_newitem():
    pass


@given(parsers.parse("a new {media_format_name} item is created by the staff"))
def new_item(dummy_database, new_collection, new_project, staff_contact,
             create_new_object, media_format_name):

    all_media_formats = dummy_database.query(database.FormatTypes)

    format_type = all_media_formats.filter(
        database.FormatTypes.name == media_format_name
    ).one()

    collection_item = database.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        barcode=SAMPLE_BAR_CODE,
        file_name=SAMPLE_FILE,
        medusa_uuid=SAMPLE_MEDUSA_ID,
        original_rec_date=SAMPLE_DATE,
        original_return_date=SAMPLE_DATE,
        collection_object=create_new_object,
        obj_sequence=SAMPLE_OBJ_SEQUENCE,
        format_type=format_type

    )

    return collection_item


@when("the item is added to the object")
def add_item(dummy_database, new_item):
    dummy_database.add(new_item)
    dummy_database.commit()
    return dummy_database


@then("the new item record contains the correct barcode")
def item_has_correct_barcode(dummy_database):
    new_added_item = dummy_database.query(database.CollectionItem).first()
    assert new_added_item.barcode == SAMPLE_BAR_CODE


@scenario("database.feature", "Create a new inspection note for item")
def test_database_note():
    pass


@given(parsers.parse("a new {note_type} note is created"))
def new_note(dummy_database, note_type):
    inspection_note = \
        dummy_database.query(database.NoteTypes).filter(
            database.NoteTypes.name == note_type).one()

    assert inspection_note.name == note_type

    return database.Note(
        text=SAMPLE_INSPECTION_NOTE,
        note_type=inspection_note

    )


@when(parsers.parse("the new note is added to the {data_type}"))
def add_inspection_note(dummy_database, new_note, data_type):
    my_data_type = getattr(database, data_type)
    collection_item = dummy_database.query(my_data_type).first()
    collection_item.notes.append(new_note)
    dummy_database.commit()
    return dummy_database


@then(parsers.parse("the {data_type} record has the new note"))
def item_has_the_note(dummy_database, data_type):
    my_data_type = getattr(database, data_type)
    collection_item = dummy_database.query(my_data_type).first()
    for note in collection_item.notes:
        assert note.text == SAMPLE_INSPECTION_NOTE


@scenario("database.feature", "Create a new inspection note for project")
def test_project_node():
    pass


@scenario("database.feature",
          "Create a new inspection note for CollectionObject")
def test_project_node():
    pass


@then(parsers.parse("the CollectionObject record was last updated "
                    "by {staff_first_name} {staff_last_name}"))
def object_updated_by_staff(dummy_database, staff_first_name, staff_last_name):
    all_contacts = dummy_database.query(database.Contact)

    staff_contact = \
        all_contacts.filter(
            database.Contact.last_name == staff_last_name,
            database.Contact.first_name == staff_first_name
        ).one()

    assert staff_contact.last_name == staff_last_name
    assert staff_contact.first_name == staff_first_name

    collection_object = dummy_database.query(database.CollectionObject).first()
    assert collection_object.last_updated.last_name == staff_last_name
    assert collection_object.last_updated.first_name == staff_first_name


@scenario("database.feature", "Item is sent for treatment")
def test_add_treatment():
    pass


@when("the new treatment record is added to the item")
def treatment_add_to_item(dummy_database, new_item, treatment_record):
    new_item.treatment.append(treatment_record)
    dummy_database.commit()
    return dummy_database


@given(parsers.parse('a new treatment record is created that '
                     'needs "{needs}" and got "{given}"'))
def treatment_record(needs, given):
    return database.Treatment(
        needed=needs,
        given=given,
        date=SAMPLE_DATE

    )


@then(parsers.parse('the treatment record of the item states that it '
                    'needs "{needs}" and got "{given}"'))
def treatment_record_reads(dummy_database, needs, given):
    collection_item = dummy_database.query(database.CollectionItem).first()

    assert len(collection_item.treatment) == 1, \
        "Can only test if there is a single treatement record"

    treatment_record = collection_item.treatment[0]

    assert treatment_record.needed == needs
    assert treatment_record.given == given


@scenario("database.feature", "Create a new media project")
def test_new_media_project():
    pass


@given("a new <media_type> item with <file_name> added to the object")
def add_new_item_to_object(dummy_database, create_new_object, media_type,
                           file_name):

    media_type_info = database.format_types.get(media_type)
    assert media_type_info is not None, "No table for {}".format(media_type)

    all_format_types = dummy_database.query(database.FormatTypes)
    format_type = all_format_types.filter(
        database.FormatTypes.name == media_type
    ).one()

    new_item = database.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        barcode=SAMPLE_BAR_CODE,
        file_name=file_name,
        medusa_uuid=SAMPLE_MEDUSA_ID,
        original_rec_date=SAMPLE_DATE,
        original_return_date=SAMPLE_DATE,
        obj_sequence=SAMPLE_OBJ_SEQUENCE,
        format_type=format_type

    )

    media_table_type = media_type_info[1](item=new_item)
    create_new_object.items.append(new_item)
    dummy_database.add(create_new_object)
    dummy_database.add(media_table_type)
    dummy_database.commit()


@then("the database has item record with the <file_name> and has a "
       "corresponding <media_type> record with the same item id")
def has_a_record_with_media_item(dummy_database, file_name, media_type):
    collection_items = dummy_database.query(database.CollectionItem)
    collection_item = collection_items.filter(
        database.CollectionItem.file_name == file_name).one()

    assert collection_item.file_name == file_name

    media_types = dummy_database.query(database.FormatTypes)

    media_format = media_types.filter(database.FormatTypes.id ==
                                      collection_item.format_type_id).one()

    assert media_format.name == media_type


@scenario("database.feature", "Create a open reel project")
def test_new_open_reel_project():
    pass


@when("a new open reel item recorded on <date_recorded> to <tape_size> tape "
      "on a <base> base with <file_name> added to the object")
def new_open_reel(dummy_database, create_new_object, date_recorded,
                  tape_size, base, file_name):

    new_item = database.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        file_name=file_name
    )

    open_reel = database.OpenReel(
        item=new_item,
        date_recorded=SAMPLE_DATE,
        tape_size=tape_size,
        base=base

    )

    create_new_object.items.append(new_item)
    dummy_database.add(open_reel)
    dummy_database.add(new_item)
    dummy_database.commit()


@then("the database has item record with the <file_name>")
def database_has_item_record_w_filename(dummy_database, file_name):
    collection_items = dummy_database.query(database.CollectionItem)
    collection_item = collection_items.filter(
        database.CollectionItem.file_name == file_name).one()
    assert collection_item.file_name == file_name


@then("the database has open reel record with a <tape_size> sized tape")
def check_open_reel_tape_size(dummy_database, tape_size):
    open_reel_items = dummy_database.query(database.OpenReel)
    open_reel_item = open_reel_items.filter(
        database.OpenReel.tape_size == tape_size).one()

    assert open_reel_item.tape_size == tape_size


@then("the database has open reel record with a <base> base")
def check_open_reel_base(dummy_database, base):
    open_reel_items = dummy_database.query(database.OpenReel)
    open_reel_item = open_reel_items.filter(
        database.OpenReel.base == base).one()

    assert open_reel_item.base == base


@scenario("database.feature", "Create a vendor")
def test_vendor():
    pass


@given("an empty database")
def empty_database(dummy_database):
    return dummy_database


@when("a new vendor named <vendor_name> from <address> in <city>, <state> "
      "<zipcode> is added")
def add_vendor(empty_database, vendor_name, address, city, state, zipcode):
    new_vendor = database.Vendor(
        name=vendor_name,
        address=address,
        city=city,
        state=state,
        zipcode=zipcode,
    )
    empty_database.add(new_vendor)
    empty_database.commit()


@then("the newly created vendor has the name <vendor_name>")
def vendor_has_name(dummy_database, vendor_name):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.name == vendor_name).one()
    assert vendor.name == vendor_name


@then("the newly created vendor has the address <address>")
def vendor_has_address(dummy_database, address):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.address == address).one()
    assert vendor.address == address


@then("the newly created vendor is located in <city> city")
def vendor_is_in_city(dummy_database, city):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.city == city).one()
    assert vendor.city == city


@then("the newly created vendor is located in <state> state")
def vendor_is_in_city(dummy_database, state):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.state == state).one()
    assert vendor.state == state


@then("the newly created vendor is has a <zipcode> zipcode")
def vendor_is_in_city(dummy_database, zipcode):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.zipcode == zipcode).one()
    assert vendor.zipcode == zipcode


@scenario("database.feature", "Create a vendor contacts")
def test_vendor_contact():
    pass


@when("<contact_first_name> <contact_last_name> is added as a contact to the "
      "vendor named <vendor_name>")
def contact_to_vendor(dummy_database, contact_first_name, contact_last_name,
                      vendor_name):
    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.name == vendor_name).one()

    contact = database.Contact(
        first_name=contact_first_name,
        last_name=contact_last_name,
        )
    vendor.contacts.append(contact)
    dummy_database.commit()


@then("the vendor named <vendor_name> has a contact named "
      "<contact_first_name> <contact_last_name>")
def vendor_has_contact(dummy_database, vendor_name, contact_first_name,
                       contact_last_name):

    vendors = dummy_database.query(database.Vendor)
    vendor = vendors.filter(database.Vendor.name == vendor_name).one()

    for contact in vendor.contacts:
        print(contact)
        if contact.first_name == contact_first_name \
                and contact.last_name == contact_last_name:
            break

    else:
        assert False, \
            f"No contact named {contact_first_name}, {contact_last_name}"
