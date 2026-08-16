def total_program_time_seconds(steps):
    """Return the duration implied by a structured, user-defined program."""
    return sum(step.duration_seconds * step.cycles for step in steps)
