from dataclasses import dataclass


@dataclass(frozen=True)
class MasterMixComponent:
    name: str
    volume_per_reaction_ul: float


def calculate_master_mix(components, reaction_count, excess_fraction=0.1):
    """Scale user-supplied component volumes for reactions and optional excess."""
    if reaction_count < 1:
        raise ValueError("reaction_count must be positive")
    if excess_fraction < 0:
        raise ValueError("excess_fraction cannot be negative")

    scale = reaction_count * (1 + excess_fraction)
    return [
        MasterMixComponent(component.name, component.volume_per_reaction_ul * scale)
        for component in components
    ]
