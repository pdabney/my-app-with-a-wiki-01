# Generated from colocated metadata — do not edit STRUCTURE by hand.
# Regenerate: python3 dist-brain-metadata-tooling/engine/generate_gherkin.py --root .
# @intent prose becomes scenario descriptions; @raises become Then steps.

Feature: custom-aliases
  A URL gets a deterministic short code derived from its content, so the same URL always yields the same code. A caller may instead request a custom alias; that path is guarded by a feature flag because

  @flag:enable_custom_aliases
  Scenario: create_short_link
    # src/linkshort/shorten.py#create_short_link
    # @intent A URL gets a deterministic short code derived from its content, so the same URL always yields the same code. A caller may instead request a custom alias; that path is guarded by a feature flag because it is a paid feature. A taken alias is rejected rather than silently overwriting an existing link.
    Given a link store
    When create_short_link is called with "alias", "url"
    Then InvalidURL is raised by create_short_link
    Then AliasTaken is raised by create_short_link

  # Flag-gated scenarios (matrix: on and off)

  @flag:enable_custom_aliases
  Scenario: create_short_link_flag_off
    # src/linkshort/shorten.py#create_short_link — flag enable_custom_aliases is off
    Given flag enable_custom_aliases is off
    And a link store
    When create_short_link is invoked per contract
    Then behavior matches @intent with flag off

  @flag:enable_custom_aliases
  Scenario: create_short_link_flag_on
    # src/linkshort/shorten.py#create_short_link — flag enable_custom_aliases is on
    Given flag enable_custom_aliases is on
    And a link store
    When create_short_link is invoked per contract
    Then behavior matches @intent with flag on
