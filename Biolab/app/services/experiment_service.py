from app import db
from app.models import PCRCycleGroup, PCRProgram, PCRStep


def total_reactions(experiment):
    sample_count = experiment.sample_count or len(experiment.samples)
    configured_control_count = experiment.positive_controls + experiment.negative_controls + experiment.ntcs
    control_count = configured_control_count or len(experiment.controls)
    if experiment.replicate_type == "Technical":
        multiplier = max(experiment.technical_replicates, 1)
    elif experiment.replicate_type == "Biological":
        multiplier = max(experiment.biological_replicates, 1)
    elif experiment.replicate_type == "Both":
        multiplier = max(experiment.technical_replicates, 1) * max(experiment.biological_replicates, 1)
    else:
        multiplier = 1
    return (sample_count + control_count) * multiplier


def master_mix_reactions(experiment):
    """Return total reaction equivalents including explicitly added extras."""
    return total_reactions(experiment) + max(experiment.extra_reactions, 0)


def master_mix_totals(experiment):
    preparation_reactions = master_mix_reactions(experiment)
    return [
        (reagent, reagent.volume_per_reaction_ul * preparation_reactions)
        for reagent in experiment.reagents
        if reagent.include_in_master_mix
    ]


def add_program_step(experiment, data):
    program = experiment.programs[0] if experiment.programs else PCRProgram(name=f"{experiment.name} program", experiment=experiment)
    step = PCRStep(
        name=data.get("name", "New step"),
        step_type=data.get("step_type", "step"),
        order=len(program.steps) + 1,
        temperature_c=float(data.get("temperature_c", 0)),
        duration_seconds=round(float(data.get("duration_minutes", float(data.get("duration_seconds", 0)) / 60)) * 60),
        cycles=int(data.get("cycles", 1)),
        goto_step=int(data.get("goto_step", 0) or 0) or None,
        repeat_count=max(int(data.get("repeat_count", 0) or 0), 0),
    )
    program.steps.append(step)
    db.session.add(program)
    return step


def delete_program_step(experiment, step_id):
    program = experiment.programs[0] if experiment.programs else None
    step = next((item for item in program.steps if item.id == step_id), None) if program else None
    if step:
        db.session.delete(step)
        db.session.flush()
        for index, remaining in enumerate(program.steps, 1):
            remaining.order = index
    return step


def move_program_step(experiment, step_id, direction):
    program = experiment.programs[0] if experiment.programs else None
    if not program:
        return None
    steps = sorted(program.steps, key=lambda item: item.order)
    index = next((position for position, item in enumerate(steps) if item.id == step_id), None)
    target = index + direction if index is not None else None
    if target is None or target < 0 or target >= len(steps):
        return None
    steps[index], steps[target] = steps[target], steps[index]
    for position, step in enumerate(steps, 1):
        step.order = position
    return steps[target]


def update_program_step(experiment, step_id, data):
    program = experiment.programs[0] if experiment.programs else None
    step = next((item for item in program.steps if item.id == step_id), None) if program else None
    if not step:
        return None
    step.name = data.get("name", step.name).strip() or step.name
    step.step_type = data.get("step_type", step.step_type)
    step.temperature_c = float(data.get("temperature_c", step.temperature_c))
    step.duration_seconds = round(float(data.get("duration_minutes", step.duration_seconds / 60)) * 60)
    step.cycles = max(int(data.get("cycles", step.cycles)), 1)
    step.goto_step = int(data.get("goto_step", step.goto_step or 0) or 0) or None
    step.repeat_count = max(int(data.get("repeat_count", step.repeat_count) or 0), 0)
    return step


def add_cycle_group(experiment, data):
    program = experiment.programs[0] if experiment.programs else PCRProgram(name=f"{experiment.name} program", experiment=experiment)
    group = PCRCycleGroup(name=data.get("name", "Cycling group").strip() or "Cycling group", cycles=max(int(data.get("cycles", 1)), 1), program=program)
    db.session.add(program)
    db.session.add(group)
    return group
