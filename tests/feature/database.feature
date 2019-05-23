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
    And a staff contact
    And a new object for the collection created by the staff
    When a object is added to the collection
    Then the database has 1 Project records
    And the database has 2 Contact records
    And the database has 1 Collection records
    And the database has 1 CollectionObject records

  Scenario: Create a new item
    Given a database with a collection
    And a staff contact
    And a new object for the collection created by the staff
    And a new item is created by the staff
    When a item is added to the object
    Then the database has 1 Project records
    And the database has 1 Collection records
    And the database has 1 CollectionObject records
    And the database has 1 CollectionItem records
    And the new item record contains the correct barcode

    Scenario: Create a new note
      Given a database with a collection
      And a staff contact
      And a new object for the collection created by the staff
      And a new item is created by the staff
      And a new inspection note is created
      When a item is added to the object
      And the new inspection note is added to the item
      Then the database has 1 Note records
      And the item record has the new note
