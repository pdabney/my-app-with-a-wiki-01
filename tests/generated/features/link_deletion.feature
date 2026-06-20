# Generated from colocated metadata — do not edit STRUCTURE by hand.
# Regenerate: python3 dist-brain-metadata-tooling/engine/generate_gherkin.py --root .
# @intent prose becomes scenario descriptions; @raises become Then steps.

Feature: link-deletion
  Deletion is hard (the link is gone, not soft-hidden) and gated behind a flag because it's destructive and irreversible. Deleting a code that doesn't exist is an error, not a silent no-op, so a caller 

  @flag:enable_link_deletion
  Scenario: delete_link
    # src/linkshort/delete.py#delete_link
    # @intent Deletion is hard (the link is gone, not soft-hidden) and gated behind a flag because it's destructive and irreversible. Deleting a code that doesn't exist is an error, not a silent no-op, so a caller can't believe it removed something it didn't.
    Given a link store
    When delete_link is called with "code"
    Then LinkNotFound is raised by delete_link

  # Flag-gated scenarios (matrix: on and off)

  @flag:enable_link_deletion
  Scenario: delete_link_flag_off
    # src/linkshort/delete.py#delete_link — flag enable_link_deletion is off
    Given flag enable_link_deletion is off
    And a link store
    When delete_link is invoked per contract
    Then behavior matches @intent with flag off

  @flag:enable_link_deletion
  Scenario: delete_link_flag_on
    # src/linkshort/delete.py#delete_link — flag enable_link_deletion is on
    Given flag enable_link_deletion is on
    And a link store
    When delete_link is invoked per contract
    Then behavior matches @intent with flag on
