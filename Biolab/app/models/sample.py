from app import db


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    replicate_count = db.Column(db.Integer, nullable=False, default=1)
    specimen_id = db.Column(db.String(160))
    sample_type = db.Column(db.String(80))
    result = db.Column(db.String(160))
    notes = db.Column(db.Text)
    experiment_id = db.Column(db.Integer, db.ForeignKey("pcr_experiment.id"), nullable=False)

    experiment = db.relationship("PCRExperiment", back_populates="samples")
