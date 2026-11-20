@backend
Feature: PDND administration access

  Scenario: Anonymous visitors must log in before managing PDND projects
    When an anonymous visitor opens the PDND project form
    Then they are redirected to the login page
