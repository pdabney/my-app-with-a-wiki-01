# Generated from colocated metadata — do not edit STRUCTURE by hand.
# Regenerate: python3 dist-brain-metadata-tooling/engine/generate_gherkin.py --root .
# @intent prose becomes scenario descriptions; @raises become Then steps.

Feature: click-analytics
  Click recording is separated from resolution so it can be turned off wholesale via a feature flag (e.g. for privacy modes) without affecting redirects. An unknown code is an error rather than a silent

  @flag:enable_click_analytics
  Scenario: record_click
    # src/linkshort/analytics.py#record_click
    # @intent Click recording is separated from resolution so it can be turned off wholesale via a feature flag (e.g. for privacy modes) without affecting redirects. An unknown code is an error rather than a silent no-op.
    Given a link store
    When record_click is called with "code"
    Then LinkNotFound is raised by record_click

  # Flag-gated scenarios (matrix: on and off)

  @flag:enable_click_analytics
  Scenario: record_click_flag_off
    # src/linkshort/analytics.py#record_click — flag enable_click_analytics is off
    Given flag enable_click_analytics is off
    And a link store
    When record_click is invoked per contract
    Then behavior matches @intent with flag off

  @flag:enable_click_analytics
  Scenario: record_click_flag_on
    # src/linkshort/analytics.py#record_click — flag enable_click_analytics is on
    Given flag enable_click_analytics is on
    And a link store
    When record_click is invoked per contract
    Then behavior matches @intent with flag on
