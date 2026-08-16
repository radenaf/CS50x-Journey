from app import db


class Control(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    control_type = db.Column(db.String(80), nullable=False)
    replicate_count = db.Column(db.Integer, nullable=False, default=1)
    result = db.Column(db.String(160))
    notes = db.Column(db.Text)
    experiment_id = db.Column(db.Integer, db.ForeignKey("pcr_experiment.id"), nullable=False)

    experiment = db.relationship("PCRExperiment", back_populates="controls")
    wells = db.relationship("PlateWell", back_populates="control")
