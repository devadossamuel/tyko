Feature: database
  Connection to the database

  Scenario: Create a new user
    Given a blank database
    And a contact for a collection
    When the contact is added to the database
    Then the database has 1 Contact records
    And the collection contact can be found in the database

  Scenario: Create a new collection
    Given a blank database
    When a new collection is created with a contact
    Then the new collection can be found in the database
    And the database has 1 Contact records
    And the database has 1 Collection records
    And the contact to the collection is expected value

  Scenario: Create a new project
    Given a database with a collection
    And a new Project
    When the project is added to the collection
    Then the database has 1 Project records
    And the collection contains the new project

  Scenario: Create a new object
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    When a object is added to the collection
    Then the database has 1 Project records
    And the database has 2 Contact records
    And the database has 1 Collection records
    And the database has 1 CollectionObject records
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new item
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    And a new audio video item is created by the staff
    When the item is added to the object
    Then the database has 1 Project records
    And the database has 1 Collection records
    And the database has 1 CollectionObject records
    And the database has 1 CollectionItem records
    And the new item record contains the correct barcode
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new inspection note for item
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    And a new audio video item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the CollectionItem
    Then the database has 1 Note records
    And the CollectionItem record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new inspection note for project
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    And a new audio video item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the Project
    Then the database has 1 Note records
    And the Project record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new inspection note for CollectionObject
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    And a new audio video item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the CollectionObject
    Then the database has 1 Note records
    And the CollectionObject record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Item is sent for treatment
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new object for the collection created by Henry Borchers
    And a new audio video item is created by the staff
    And a new treatment record is created that needs "X, Y, Z treatment" and got "Y treatment only"
    When the new treatment record is added to the item
    And the item is added to the object
    Then the database has 1 CollectionObject records
    And the database has 1 Treatment records
    And the treatment record of the item states that it needs "X, Y, Z treatment" and got "Y treatment only"
    And the CollectionObject record was last updated by Henry Borchers


  Scenario Outline: Create a new media project
    Given a database with a collection
    And a staff contact named <first_name> <last_name>
    And a new object for the collection created by <first_name> <last_name>
    And a new <media_type> item with <file_name> added to the object
    Then the database has 1 CollectionItem records
    And the database has 1 CollectionObject records
    And the database has item record with the <file_name> and has a corresponding <media_type> record with the same item id

    Examples:
    | first_name | last_name | media_type         |  file_name    |
    | Henry      | Borchers  | open reel          |  myfile.wav   |
    | John       | Smith     | open reel          |  my2file.wav  |
    | John       | Smith     | film               |  myfilm.mov   |
    | John       | Smith     | grooved disc       |  mydisc.wav   |
    | John       | Smith     | audio video        |  myvideo.mov  |


  Scenario Outline: Create a open reel project
    Given a database with a collection
    And a staff contact named <first_name> <last_name>
    And a new object for the collection created by <first_name> <last_name>
    When a new open reel item recorded on <date_recorded> to <tape_size> tape on a <base> base with <file_name> added to the object
    Then the database has 1 CollectionItem records
    And the database has 1 CollectionObject records
    And the database has item record with the <file_name>
    And the database has open reel record with a <tape_size> sized tape
    And the database has open reel record with a <base> base

    Examples:
    | first_name | last_name | file_name    | date_recorded | tape_size | base      |
    | Henry      | Borchers  | myfile.wav   | 1970/1/1      | 1/4 inch  | acetate   |
    | John       | Smith     | my2file2.wav | 1998/2/10     | 1/4 inch  | polyester |


  Scenario Outline: Create a vendor
    Given an empty database
    When a new vendor named <name> from <address> in <city>, <state> <zipcode> is added
    Then the database has 1 Vendor records
    And the newly created vendor has the name <name>
    And the newly created vendor is located in <city> city
    And the newly created vendor is located in <state> state
    And the newly created vendor is has a <zipcode> zipcode

    Examples:
    | name             | address          | city    | state | zipcode |
    | Alias AV Vendor  | 123 Fake Street  | Gothum  | NY    | 12345   |