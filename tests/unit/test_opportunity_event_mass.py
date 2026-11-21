"""Opportunity mass is event-count mass, not unique-pair presence."""

from __future__ import annotations

import pytest

from raven_mcs.sag.certificates import (
    pair_presence_distribution,
    window_opportunity_masses,
)


def test_event_mass_not_unique_pair_uniform() -> None:
    pairs = [("A", "s")] * 20 + [("B", "s")]
    masses = window_opportunity_masses(pairs)
    assert masses[("A", "s")] == pytest.approx(20.0 / 21.0)
    assert masses[("B", "s")] == pytest.approx(1.0 / 21.0)
    presence = pair_presence_distribution(pairs)
    assert presence[("A", "s")] == pytest.approx(0.5)
    assert presence[("B", "s")] == pytest.approx(0.5)
    assert masses[("A", "s")] != presence[("A", "s")]
