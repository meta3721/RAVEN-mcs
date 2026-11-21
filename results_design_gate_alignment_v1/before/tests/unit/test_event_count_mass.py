"""Opportunity mass is event-count normalized, not unique-pair uniform."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import (
    pair_presence_distribution,
    window_opportunity_event_counts,
    window_opportunity_masses,
)


def test_event_count_mass() -> None:
    pairs = [("A", "s")] * 20 + [("B", "s")]
    counts = window_opportunity_event_counts(pairs)
    masses = window_opportunity_masses(pairs)
    assert counts[("A", "s")] == 20.0
    assert counts[("B", "s")] == 1.0
    assert masses[("A", "s")] == pytest.approx(20.0 / 21.0)
    assert masses[("B", "s")] == pytest.approx(1.0 / 21.0)
    presence = pair_presence_distribution(pairs)
    assert presence[("A", "s")] == pytest.approx(0.5)
    assert masses[("A", "s")] != pytest.approx(presence[("A", "s")])
