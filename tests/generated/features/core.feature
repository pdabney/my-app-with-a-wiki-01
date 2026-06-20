# Generated from colocated metadata — do not edit STRUCTURE by hand.
# Regenerate: python3 dist-brain-metadata-tooling/engine/generate_gherkin.py --root .
# @intent prose becomes scenario descriptions; @raises become Then steps.

Feature: core
  A read-only view of the click total; never mutates state.

  Scenario: click_count
    # src/linkshort/analytics.py#click_count
    # @intent A read-only view of the click total; never mutates state.
    Given a link store
    When click_count is called with "code"
    Then LinkNotFound is raised by click_count

  Scenario: resolve
    # src/linkshort/resolve.py#resolve
    # @intent Resolving is a pure, side-effect-free lookup; it does not record a click (that is the analytics module's job) so that read-only previews and health checks don't inflate counts. An unknown code is an error, not an empty result, so callers can't redirect to nowhere.
    Given a link store
    When resolve is called with "code"
    Then LinkNotFound is raised by resolve
