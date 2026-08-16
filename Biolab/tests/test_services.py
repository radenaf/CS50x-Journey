import pytest

from app.services.master_mix_service import MasterMixComponent, calculate_master_mix
from app.services.pcr_program_service import total_program_time_seconds


def test_master_mix_scales_by_reactions_and_excess():
    components = [MasterMixComponent("Buffer", 2.0)]
    result = calculate_master_mix(components, reaction_count=10, excess_fraction=0.1)
    assert result[0].volume_per_reaction_ul == pytest.approx(22.0)


def test_master_mix_rejects_invalid_count():
    with pytest.raises(ValueError):
        calculate_master_mix([], 0)


def test_program_time_uses_step_cycles():
    steps = [type("Step", (), {"duration_seconds": 30, "cycles": 3})()]
    assert total_program_time_seconds(steps) == 90
