import json
from datetime import date, datetime

from app.models import Control, PCRCycleGroup, PCRExperiment, PCRProgram, PCRStep, Reagent, Sample


def _date_value(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def experiment_to_dict(experiment):
    program = experiment.programs[0] if experiment.programs else None
    return {
        "format": "biolab-pcr",
        "version": 1,
        "experiment": {
            "name": experiment.name,
            "pcr_type": experiment.pcr_type,
            "target": experiment.target,
            "reaction_volume_ul": experiment.reaction_volume_ul,
            "instrument": experiment.instrument,
            "experiment_date": _date_value(experiment.experiment_date),
            "status": experiment.status,
            "notes": experiment.notes,
            "replicate_type": experiment.replicate_type,
            "technical_replicates": experiment.technical_replicates,
            "biological_replicates": experiment.biological_replicates,
            "sample_count": experiment.sample_count,
            "positive_controls": experiment.positive_controls,
            "negative_controls": experiment.negative_controls,
            "ntcs": experiment.ntcs,
            "master_mix_excess_percent": experiment.master_mix_excess_percent,
            "extra_reactions": experiment.extra_reactions,
        },
        "samples": [
            {"name": s.name, "specimen_id": s.specimen_id, "sample_type": s.sample_type, "result": s.result, "notes": s.notes}
            for s in experiment.samples
        ],
        "controls": [
            {"name": c.name, "control_type": c.control_type, "result": c.result, "notes": c.notes}
            for c in experiment.controls
        ],
        "reagents": [
            {"name": r.name, "category": r.category, "include_in_master_mix": r.include_in_master_mix, "stock_concentration": r.stock_concentration, "volume_per_reaction_ul": r.volume_per_reaction_ul, "notes": r.notes}
            for r in experiment.reagents
        ],
        "program": {
            "name": program.name,
            "description": program.description,
            "steps": [
                {"name": s.name, "step_type": s.step_type, "order": s.order, "temperature_c": s.temperature_c, "duration_seconds": s.duration_seconds, "cycles": s.cycles, "goto_step": s.goto_step, "repeat_count": s.repeat_count}
                for s in program.steps
            ],
            "cycle_groups": [
                {"name": group.name, "cycles": group.cycles, "step_ids": [step.id for step in group.steps]}
                for group in program.cycle_groups
            ],
        } if program else None,
    }


def experiment_json(experiment):
    return json.dumps(experiment_to_dict(experiment), indent=2)


def experiment_from_dict(payload):
    info = payload.get("experiment", payload)
    experiment = PCRExperiment(
        name=info.get("name", "Imported experiment"),
        pcr_type=info.get("pcr_type", "Custom PCR"),
        target=info.get("target"),
        reaction_volume_ul=float(info.get("reaction_volume_ul", 25)),
        instrument=info.get("instrument"),
        experiment_date=date.fromisoformat(info["experiment_date"]) if info.get("experiment_date") else date.today(),
        status=info.get("status", "Draft"),
        notes=info.get("notes"),
        replicate_type=info.get("replicate_type", "None"),
        technical_replicates=int(info.get("technical_replicates", 1)),
        biological_replicates=int(info.get("biological_replicates", 1)),
        sample_count=int(info.get("sample_count", 0)),
        positive_controls=int(info.get("positive_controls", 0)),
        negative_controls=int(info.get("negative_controls", 0)),
        ntcs=int(info.get("ntcs", 0)),
        master_mix_excess_percent=float(info.get("master_mix_excess_percent", 10)),
        extra_reactions=int(info.get("extra_reactions", 0)),
    )
    for item in payload.get("samples", []):
        experiment.samples.append(Sample(**{key: item.get(key) for key in ("name", "specimen_id", "sample_type", "notes")}, replicate_count=int(item.get("replicate_count", 1)), result=item.get("result")))
    for item in payload.get("controls", []):
        experiment.controls.append(Control(name=item.get("name", "Control"), control_type=item.get("control_type", "Other"), replicate_count=int(item.get("replicate_count", 1)), result=item.get("result"), notes=item.get("notes")))
    for item in payload.get("reagents", []):
        experiment.reagents.append(Reagent(name=item.get("name", "Reagent"), category=item.get("category", "Other"), include_in_master_mix=item.get("include_in_master_mix", True), stock_concentration=item.get("stock_concentration"), volume_per_reaction_ul=float(item.get("volume_per_reaction_ul", 0)), notes=item.get("notes")))
    program_data = payload.get("program")
    if program_data:
        program = PCRProgram(name=program_data.get("name", "PCR Program"), description=program_data.get("description"))
        program.steps = [PCRStep(name=item.get("name", "Step"), step_type=item.get("step_type", "step"), order=int(item.get("order", index + 1)), temperature_c=float(item.get("temperature_c", 0)), duration_seconds=int(item.get("duration_seconds", 0)), cycles=int(item.get("cycles", 1)), goto_step=item.get("goto_step"), repeat_count=int(item.get("repeat_count", 0))) for index, item in enumerate(program_data.get("steps", []))]
        program.cycle_groups = [PCRCycleGroup(name=item.get("name", "Cycling group"), cycles=int(item.get("cycles", 1))) for item in program_data.get("cycle_groups", [])]
        experiment.programs.append(program)
    return experiment
