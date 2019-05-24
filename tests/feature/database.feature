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
    And a new audiovisual object for the collection created by Henry Borchers
    When a object is added to the collection
    Then the database has 1 Project records
    And the database has 2 Contact records
    And the database has 1 Collection records
    And the database has 1 CollectionObject records
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new item
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new audiovisual object for the collection created by Henry Borchers
    And a new item is created by the staff
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
    And a new audiovisual object for the collection created by Henry Borchers
    And a new item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the CollectionItem
    Then the database has 1 Note records
    And the CollectionItem record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new inspection note for project
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new audiovisual object for the collection created by Henry Borchers
    And a new item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the Project
    Then the database has 1 Note records
    And the Project record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Create a new inspection note for CollectionObject
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new audiovisual object for the collection created by Henry Borchers
    And a new item is created by the staff
    And a new Inspection note is created
    When the item is added to the object
    And the new note is added to the CollectionObject
    Then the database has 1 Note records
    And the CollectionObject record has the new note
    And the CollectionObject record was last updated by Henry Borchers

  Scenario: Item is sent for treatment
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new audiovisual object for the collection created by Henry Borchers
    And a new item is created by the staff
    And a new treatment record is created that needs "X, Y, Z treatment" and got "Y treatment only"
    When the new treatment record is added to the item
    And the item is added to the object
    Then the database has 1 CollectionObject records
    And the database has 1 Treatment records
    And the treatment record of the item states that it needs "X, Y, Z treatment" and got "Y treatment only"
    And the CollectionObject record was last updated by Henry Borchers


  Scenario: Create a new open reel project
    Given a database with a collection
    And a staff contact named Henry Borchers
    And a new open reel object for the collection created by Henry Borchers
    And a new item added to the object
    Then the database has 1 CollectionItem records
    And the database has 1 CollectionObject records
#    And the database has 1 Contact records
#    And the database has 1 Collection records
#    And the contact to the collection is expected value