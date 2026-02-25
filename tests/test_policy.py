from byteops_agent.config import FilteringConfig
from byteops_agent.policy import Event, match_policy


def test_policy_respects_include_exclude_and_severity():
    event = Event(
        source_type="rss",
        source_name="CISA",
        title="Critical RCE advisory",
        summary="high severity and urgent",
        url="https://example.com",
        severity="critical",
    )

    filtering = FilteringConfig(
        min_severity="medium",
        include_keywords=["rce"],
        exclude_keywords=["ignoreme"],
    )
    result = match_policy(event, filtering)
    assert result.matched is True

    blocked = FilteringConfig(min_severity="high", include_keywords=[], exclude_keywords=["advisory"])
    blocked_result = match_policy(event, blocked)
    assert blocked_result.matched is False
    assert blocked_result.reason.startswith("excluded")
