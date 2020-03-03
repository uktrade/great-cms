@django_db
Feature: Demo test scenarios


  Scenario: Home page should work
    Given "Joel" decided to visit the home page
    Then "Joel" should be on the home page
    And "Joel" should not see errors


  Scenario: Visiting a not existent page should yield a 404 page
    Given "Joel" is on the home page
    When "Joel" decided to go to "non-existent" page
    Then "Joel" should be on the 404 page