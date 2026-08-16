from app import db


class PCRProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    experiment_id = db.Column(db.Integer, db.ForeignKey("pcr_experiment.id"))
    steps = db.relationship("PCRStep", back_populates="program", cascade="all, delete-orphan", order_by="PCRStep.order")
    cycle_groups = db.relationship("PCRCycleGroup", back_populates="program", cascade="all, delete-orphan")
    experiment = db.relationship("PCRExperiment", back_populates="programs")


class PCRStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False, default="Step")
    order = db.Column(db.Integer, nullable=False)
    temperature_c = db.Column(db.Float, nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=False)
    cycles = db.Column(db.Integer, nullable=False, default=1)
    step_type = db.Column(db.String(40), nullable=False, default="step")
    goto_step = db.Column(db.Integer)
    repeat_count = db.Column(db.Integer, nullable=False, default=0)
    program_id = db.Column(db.Integer, db.ForeignKey("pcr_program.id"), nullable=False)
    cycle_group_id = db.Column(db.Integer, db.ForeignKey("pcr_cycle_group.id"))

    program = db.relationship("PCRProgram", back_populates="steps")
    cycle_group = db.relationship("PCRCycleGroup", back_populates="steps")


class PCRCycleGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    cycles = db.Column(db.Integer, nullable=False, default=1)
    program_id = db.Column(db.Integer, db.ForeignKey("pcr_program.id"), nullable=False)

    program = db.relationship("PCRProgram", back_populates="cycle_groups")
    steps = db.relationship("PCRStep", back_populates="cycle_group")
