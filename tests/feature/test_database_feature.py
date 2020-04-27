import tyko.database
from tyko import schema
from datetime import date, datetime

from pytest_bdd import scenario, given, then, when, parsers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SAMPLE_TREATMENT_GIVEN = "This item got only y treatment"

SAMPLE_TREATMENT_NEEDED = "This item needs x, y, and z treatment"

SAMPLE_INSPECTION_NOTE = "This is a sample long form notes about the inspection"

SAMPLE_OBJ_SEQUENCE = 12

SAMPLE_DATE = date(1970, 1, 1)

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
    tyko.database.init_database(engine)

    dummy_session = sessionmaker(bind=engine)
    session = dummy_session()
    yield session
    session.close()


@given("a contact for a collection")
def collection_contact():
    new_contact = schema.Contact(
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
    staff_in_database = dummy_database.query(schema.Contact).all()

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
    collections = dummy_database.query(schema.Collection).all()
    assert len(collections) == 1


@then("the contact to the collection is expected value")
def expected_collection_contact(dummy_database):
    collection = dummy_database.query(schema.Collection).first()
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

    contact = dummy_database.query(schema.Contact).first()
    new_collection = schema.Collection(
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


@given(parsers.parse("a new object for the collection with a barcode"))
def create_new_object(dummy_database, new_collection, new_project):

    new_object = schema.CollectionObject(
        name=SAMPLE_OBJECT_NAME,
        collection=new_collection,
        project=new_project,
        barcode=SAMPLE_BAR_CODE,
        originals_rec_date=SAMPLE_DATE,
        originals_return_date=SAMPLE_DATE,
    )
    return new_object


@given("a new Project")
def new_project(dummy_database):

    return schema.Project(
        project_code=SAMPLE_PROJECT_CODE,
        title=SAMPLE_PROJECT_TITLE,
        current_location=SAMPLE_LOCATION,
        status=schema.ProjectStatus(name=SAMPLE_PROJECT_STATUS),
        specs=SAMPLE_PROJECT_SPECS
    )


@when("the project is added to the collection")
def add_new_project(dummy_database, new_project):
    dummy_database.add(new_project)
    dummy_database.commit()
    return dummy_database


@then("the collection contains the new project")
def collection_has_project(dummy_database):

    new_added_project = dummy_database.query(
        schema.Project).first()

    assert new_added_project.project_code == SAMPLE_PROJECT_CODE
    assert new_added_project.title == SAMPLE_PROJECT_TITLE
    assert new_added_project.current_location == SAMPLE_LOCATION
    assert new_added_project.specs == SAMPLE_PROJECT_SPECS


@given(parsers.parse(
    "a staff contact named {staff_first_name} {staff_last_name}"))
def staff_contact(dummy_database, staff_first_name, staff_last_name):
    new_contact = schema.Contact(
        first_name=staff_first_name,
        last_name=staff_last_name,
        email_address=SAMPLE_STAFF_CONTACT_EMAIL
    )
    dummy_database.add(new_contact)
    return new_contact


@then(parsers.parse("the database has {count:d} {data_type} records"))
def count_database_items(dummy_database, count, data_type):
    my_data_type = getattr(schema, data_type)
    assert len(dummy_database.query(my_data_type).all()) == count


@scenario("database.feature", "Create a new item")
def test_newitem():
    pass


@given(parsers.parse("a new {media_format_name} item is created by the staff"))
def new_item(dummy_database, new_collection, new_project, staff_contact,
             create_new_object, media_format_name):

    all_media_formats = dummy_database.query(schema.FormatTypes)

    format_type = all_media_formats.filter(
        schema.FormatTypes.name == media_format_name
    ).one()

    collection_item = schema.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        parent_object=create_new_object,
        obj_sequence=SAMPLE_OBJ_SEQUENCE,
        format_type=format_type

    )
    collection_item.files.append(
        schema.InstantiationFile(file_name=SAMPLE_FILE)
    )

    return collection_item


@when("the item is added to the object")
def add_item(dummy_database, new_item):
    dummy_database.add(new_item)
    dummy_database.commit()
    return dummy_database


@then("the new object record contains the correct barcode")
def object_has_correct_barcode(dummy_database):
    new_added_object = dummy_database.query(
        schema.CollectionObject).first()
    assert new_added_object.barcode == SAMPLE_BAR_CODE


@scenario("database.feature", "Create a new inspection note for item")
def test_database_note():
    pass


@given(parsers.parse("a new {note_type} note is created"))
def new_note(dummy_database, note_type):
    inspection_note = \
        dummy_database.query(schema.NoteTypes).filter(
            schema.NoteTypes.name == note_type).one()

    assert inspection_note.name == note_type

    return schema.Note(
        text=SAMPLE_INSPECTION_NOTE,
        note_type=inspection_note

    )


@when(parsers.parse("the new note is added to the {data_type}"))
def add_inspection_note(dummy_database, new_note, data_type):
    my_data_type = getattr(schema, data_type)
    collection_item = dummy_database.query(my_data_type).first()
    collection_item.notes.append(new_note)
    dummy_database.commit()
    return dummy_database


@then(parsers.parse("the {data_type} record has the new note"))
def item_has_the_note(dummy_database, data_type):
    my_data_type = getattr(schema, data_type)
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
    return schema.Treatment(
        needed=needs,
        given=given,
        date=SAMPLE_DATE

    )


@then(parsers.parse('the treatment record of the item states that it '
                    'needs "{needs}" and got "{given}"'))
def treatment_record_reads(dummy_database, needs, given):
    collection_item = dummy_database.query(
        schema.CollectionItem).first()

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

    media_type_info = schema.formats.format_types.get(media_type)
    assert media_type_info is not None, "No table for {}".format(media_type)

    all_format_types = dummy_database.query(schema.FormatTypes)
    format_type = all_format_types.filter(
        schema.FormatTypes.name == media_type
    ).one()

    new_item = schema.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        obj_sequence=SAMPLE_OBJ_SEQUENCE,
        format_type=format_type

    )
    new_item.files.append(
        schema.InstantiationFile(file_name=file_name)
    )

    media_table_type = media_type_info[1](item=new_item)
    create_new_object.items.append(new_item)
    dummy_database.add(create_new_object)
    dummy_database.add(media_table_type)
    dummy_database.commit()


@then("the database has item record with the <file_name> and has a "
       "corresponding <media_type> record with the same item id")
def has_a_record_with_media_item(dummy_database, file_name, media_type):

    item_file = dummy_database.query(
        schema.InstantiationFile)\
        .join(schema.CollectionItem)\
        .filter(
        schema.InstantiationFile.file_name == file_name).one()
    assert item_file.file_name == file_name

    media_types = dummy_database.query(schema.FormatTypes)

    collection_item = dummy_database.query(schema.CollectionItem) \
        .join(schema.InstantiationFile) \
        .filter(
        schema.InstantiationFile.file_name == file_name).one()
    media_format = media_types.filter(schema.FormatTypes.id ==
                                      collection_item.format_type_id).one()

    assert media_format.name == media_type


@scenario("database.feature", "Create a open reel project")
def test_new_open_reel_project():
    pass


@when("a new open reel item recorded on <date_recorded> to <tape_size> tape "
      "on a <base> base with <file_name> added to the object")
def new_open_reel(dummy_database, create_new_object, date_recorded,
                  tape_size, base, file_name):

    new_item = schema.CollectionItem(
        name=SAMPLE_ITEM_NAME,
    )
    new_item.files.append(
        schema.InstantiationFile(file_name=file_name)
    )

    open_reel = schema.OpenReel(
        item=new_item,
        date_recorded=SAMPLE_DATE,
        tape_size=tape_size,
        base=base

    )
    new_file_instance = schema.InstantiationFile(file_name=file_name)
    new_item.files.append(new_file_instance)
    create_new_object.items.append(new_item)
    dummy_database.add(open_reel)
    dummy_database.add(new_item)
    dummy_database.commit()


@then("the database has item record with the <file_name>")
def database_has_item_record_w_filename(dummy_database, file_name):
    collection_items = dummy_database.query(schema.CollectionItem)
    for collection_item in collection_items:
        for file_instance in collection_item.files:
            if file_instance.file_name == file_name:
                assert True
                return
    assert False, "No file matched {}".format(file_name)


@then("the database has open reel record with a <tape_size> sized tape")
def check_open_reel_tape_size(dummy_database, tape_size):
    open_reel_items = dummy_database.query(schema.OpenReel)
    open_reel_item = open_reel_items.filter(
        schema.OpenReel.tape_size == tape_size).one()

    assert open_reel_item.tape_size == tape_size


@then("the database has open reel record with a <base> base")
def check_open_reel_base(dummy_database, base):
    open_reel_items = dummy_database.query(schema.OpenReel)
    open_reel_item = open_reel_items.filter(
        schema.OpenReel.base == base).one()

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
    new_vendor = schema.Vendor(
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
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.name == vendor_name).one()
    assert vendor.name == vendor_name


@then("the newly created vendor has the address <address>")
def vendor_has_address(dummy_database, address):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.address == address).one()
    assert vendor.address == address


@then("the newly created vendor is located in <city> city")
def vendor_is_in_city(dummy_database, city):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.city == city).one()
    assert vendor.city == city


@then("the newly created vendor is located in <state> state")
def vendor_is_in_city(dummy_database, state):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.state == state).one()
    assert vendor.state == state


@then("the newly created vendor is has a <zipcode> zipcode")
def vendor_is_in_city(dummy_database, zipcode):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.zipcode == zipcode).one()
    assert vendor.zipcode == zipcode


@scenario("database.feature", "Create a vendor contacts")
def test_vendor_contact():
    pass


@when("<contact_first_name> <contact_last_name> is added as a contact to the "
      "vendor named <vendor_name>")
def contact_to_vendor(dummy_database, contact_first_name, contact_last_name,
                      vendor_name):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.name == vendor_name).one()

    contact = schema.Contact(
        first_name=contact_first_name,
        last_name=contact_last_name,
        )
    vendor.contacts.append(contact)
    dummy_database.commit()


@then("the vendor named <vendor_name> has a contact named "
      "<contact_first_name> <contact_last_name>")
def vendor_has_contact(dummy_database, vendor_name, contact_first_name,
                       contact_last_name):

    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.name == vendor_name).one()

    for contact in vendor.contacts:
        print(contact)
        if contact.first_name == contact_first_name \
                and contact.last_name == contact_last_name:
            break

    else:
        assert False, \
            f"No contact named {contact_first_name}, {contact_last_name}"


@scenario("database.feature", "Send an object to a vendor")
def test_vendor_gets_object():
    pass


@when("the object is sent to the vendor <vendor_name>")
def vendor_gets_object(dummy_database, create_new_object, vendor_name):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.name == vendor_name).one()

    vendor_transfer = schema.VendorTransfer(
        vendor=vendor,
        vendor_deliverables_rec_date=SAMPLE_DATE,
        returned_originals_rec_date=SAMPLE_DATE,
    )
    vendor_transfer.transfer_objects.append(create_new_object)
    dummy_database.add(vendor_transfer)
    dummy_database.commit()


@then("there is a new transfer for the new object sent to <vendor_name>")
def new_transfer_for_vendor(dummy_database, vendor_name, create_new_object):
    vendors = dummy_database.query(schema.Vendor)
    vendor = vendors.filter(schema.Vendor.name == vendor_name).one()

    transfers = dummy_database.query(schema.VendorTransfer)
    transfer = transfers.filter(
        schema.VendorTransfer.vendor == vendor).one()

    for transfer_object in transfer.transfer_objects:

        if transfer_object.name != create_new_object.name:
            continue

        if transfer_object.collection != create_new_object.collection:
            continue

        if transfer_object.project != create_new_object.project:
            continue

        if transfer_object.contact != create_new_object.contact:
            continue

        break
    else:
        assert False, "No valid objects found in the VendorTransfer"


@scenario("database.feature", "Create a new project with a note")
def test_project_note():
    pass


@when("a new Project with a project note")
def new_project_with_a_project_note(dummy_database, new_project, new_note):
    new_project_note = new_note
    new_project_note.text = "This is a new project note"
    new_project.notes.append(new_project_note)
    dummy_database.add(new_project)
    dummy_database.commit()
    return dummy_database


@then(parsers.parse("all the {data_type} records can be serialize"))
def can_serialize(dummy_database, data_type):
    my_data_type = getattr(schema, data_type)
    data_entry = dummy_database.query(my_data_type).all()
    for entry in data_entry:
        res = entry.serialize()
        assert res is not None


@scenario("database.feature", "Create a new Groove Disc object")
def test_database_groove_disc():
    pass


@then(parsers.parse("all the {media_type} items in the database can be serialized"))
def media_type_can_be_serialize(dummy_database, media_type):
    my_data_type = getattr(schema, media_type)
    data_entry = dummy_database.query(my_data_type).all()

    assert len(data_entry) > 0

    for entry in data_entry:
        res = entry.serialize()
        assert res is not None


@given("a new GroovedDisc item is created")
def new_grooved_disc(dummy_database):
    new_disc_item = schema.CollectionItem(name="side A")
    dummy_database.add(new_disc_item)
    dummy_database.commit()
    new_disc = schema.GroovedDisc(item_id=new_disc_item.id, side="A")
    dummy_database.add(new_disc)
    dummy_database.commit()


@scenario("database.feature", "Create a new Film object")
def test_database_film():
    pass


@given("a new Film item is created")
def new_film(dummy_database):
    new_film_item = schema.CollectionItem(name="reel 1")
    dummy_database.add(new_film_item)
    dummy_database.commit()
    new_film = schema.Film(item_id=new_film_item.id, sound="optical")
    dummy_database.add(new_film)
    dummy_database.commit()



@given("a new OpenReel item is created")
def new_open_reel(dummy_database):
    new_open_reel_item = schema.CollectionItem(name="reel 1")
    dummy_database.add(new_open_reel_item)
    dummy_database.commit()
    new_reel = schema.OpenReel(item_id=new_open_reel_item.id, track_count="2")
    dummy_database.add(new_reel)
    dummy_database.commit()


@scenario("database.feature", "Create a new OpenReel object")
def test_database_open_reel(dummy_database):
    pass


@scenario("database.feature", "Create a new media project where a file has a note and an annotation")
def test_file_note():
    pass


@when("a new <media_type> item with <file_name> with <note> and an annotation of <annotation_type> and <annotation_content> added to the object")
def new_media_with_file_note(dummy_database, create_new_object, media_type,
                             file_name, note,
                             annotation_type, annotation_content):
    media_type_info = schema.formats.format_types.get(media_type)
    assert media_type_info is not None, "No table for {}".format(media_type)

    all_format_types = dummy_database.query(schema.FormatTypes)
    format_type = all_format_types.filter(
        schema.FormatTypes.name == media_type
    ).one()

    new_item = schema.CollectionItem(
        name=SAMPLE_ITEM_NAME,
        obj_sequence=SAMPLE_OBJ_SEQUENCE,
        format_type=format_type

    )
    new_file = schema.InstantiationFile(file_name=file_name)
    new_file.notes.append(schema.FileNotes(message=note))
    annotation_type_enum = dummy_database.query(schema.FileAnnotationType)\
        .filter(schema.FileAnnotationType.name == annotation_type)\
        .one()

    new_file.annotations.append(
        schema.FileAnnotation(
            annotation_type=annotation_type_enum,
            annotation_content=annotation_content
        )
    )

    new_item.files.append(new_file)

    media_table_type = media_type_info[1](item=new_item)
    create_new_object.items.append(new_item)
    dummy_database.add(create_new_object)
    dummy_database.add(media_table_type)
    dummy_database.commit()


@then("the database has item record with the <file_name> that contains a note "
      "that reads <note>")
def file_with_note(dummy_database, file_name, note):
    files = \
        dummy_database.query(schema.InstantiationFile)\
            .filter(
            schema.InstantiationFile.file_name == file_name)
    for file in files:
        if file.file_name == file_name:
            assert file.notes[0].message == note
            return
    assert False


@then("the database has item record with the <file_name> that contains "
      "a <annotation_type> annotation containing <annotation_content>")
def file_with_note(dummy_database, file_name, annotation_type,
                   annotation_content):

    files = \
        dummy_database.query(schema.InstantiationFile).filter(
            schema.InstantiationFile.file_name == file_name)
    
    for file in files:
        if file.file_name == file_name:
            assert file.annotations[0].annotation_type.name == annotation_type
            assert file.annotations[0].annotation_content == annotation_content
            return
    assert False


@given("annotations for <annotation_type> configured in the database")
def add_file_annotation_type(dummy_database, annotation_type):
    dummy_database.add(
        schema.FileAnnotationType(name=annotation_type))
    return dummy_database


@scenario("database.feature", "Create a new media project with audio cassettes")
def test_audio_cassette_feature():
    pass


@given("a database with a project and a collection")
def project_and_collection(dummy_database):
    new_collection = schema.Collection(collection_name="simple collection")
    dummy_database.add(new_collection)

    new_project = schema.Project(title="Audio project")
    dummy_database.add(new_project)
    dummy_database.commit()
    return new_collection, new_project

#
@given("a new <object_title> audio recording is added")
def new_audio_object(dummy_database, project_and_collection, object_title):
    collection, project = project_and_collection
    new_object = schema.CollectionObject(name=object_title,
                                         project=project,
                                         collection=collection)
    dummy_database.add(new_object)
    dummy_database.commit()
    return {
        "collection": collection,
        "project": project,
        "object": new_object
    }

@when(
    "a tape named <item_title> recorded on <date_recorded> using a "
    "<audio_type> type <tape_type> and <tape_thickness> which was inspected "
    "on <inspection_date>")
def new_audio_item(dummy_database, new_audio_object, item_title, date_recorded,
                   audio_type, tape_type, tape_thickness, inspection_date):
    recording_date, recording_date_precision = \
        schema.AudioCassette.encode_date(date_recorded)

    new_audio_item = schema.AudioCassette(
        name=item_title,
        parent_object=new_audio_object["object"],
        recording_date=recording_date,
        recording_date_precision=recording_date_precision,
        format_type=schema.CassetteType(name=audio_type),
        tape_thickness=schema.CassetteTapeThickness(name=tape_thickness),
        inspection_date=datetime.strptime(inspection_date, "%m-%d-%Y")
    )

    if tape_type.strip() != "":
        new_audio_item.tape_type = schema.CassetteTapeType(name=tape_type)

    dummy_database.add(new_audio_item)
    dummy_database.commit()


@then(
    "the database has a an object entitled <object_title> with an "
    "AudioCassette")
def object_has_audio_cassette(dummy_database, object_title):
    found_object = dummy_database.query(schema.CollectionObject)\
        .filter(schema.CollectionObject.name == object_title).one()
    assert found_object.name == object_title
    assert len(found_object.audio_cassettes) == 1


@then(
    "AudioCassette in <object_title> is titled <item_title> was recorded on "
    "the date <date_recorded>")
def audio_cassette_has_a_title(dummy_database, object_title, item_title, date_recorded):
    cassette = dummy_database.query(schema.CollectionObject) \
        .filter(schema.CollectionObject.name == object_title) \
        .one().audio_cassettes[0]
    cassette_data = cassette.serialize()
    assert cassette_data['name'] == item_title
    assert cassette_data['date_recorded'] == date_recorded


@then(
    "AudioCassette in <object_title> with title <item_title> used type "
    "<tape_type> cassette and with <tape_thickness>")
def audio_cassette_has_a_tape_thickness(dummy_database, object_title, item_title, tape_type, tape_thickness):

    cassette = dummy_database.query(schema.CollectionObject) \
        .filter(schema.CollectionObject.name == object_title) \
        .one().audio_cassettes[0]
    cassette_date = cassette.serialize()
    assert cassette_date['name'] == item_title

    if "tape_type" in cassette_date:
        assert cassette_date['tape_type']['name'] == tape_type

    if "tape_thickness" in cassette_date:
        assert cassette_date['tape_thickness']['name'] == tape_thickness


@then(
    "AudioCassette in <object_title> with title <item_title> was inspected on "
    "<inspection_date>")
def audio_cassette_inspection_date(dummy_database, object_title, item_title, inspection_date):
    cassette = dummy_database.query(schema.CollectionObject) \
        .filter(schema.CollectionObject.name == object_title) \
        .one().audio_cassettes[0]
    cassette_date = cassette.serialize()
    assert cassette_date['inspection_date'] == inspection_date
