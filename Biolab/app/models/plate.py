from app import db


class Plate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    rows = db.Column(db.Integer, nullable=False, default=8)
    columns = db.Column(db.Integer, nullable=False, default=12)
    experiment_id = db.Column(db.Integer, db.ForeignKey("pcr_experiment.id"), nullable=False)
    wells = db.relationship("PlateWell", back_populates="plate", cascade="all, delete-orphan")
    experiment = db.relationship("PCRExperiment", back_populates="plates")


class PlateWell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(8), nullable=False)
    contents = db.Column(db.String(160))
    replicate_number = db.Column(db.Integer)
    plate_id = db.Column(db.Integer, db.ForeignKey("plate.id"), nullable=False)
    target = db.Column(db.String(160))
    sample_id = db.Column(db.Integer, db.ForeignKey("sample.id"))
    control_id = db.Column(db.Integer, db.ForeignKey("control.id"))

    plate = db.relationship("Plate", back_populates="wells")
    sample = db.relationship("Sample", back_populates="wells")
    control = db.relationship("Control", back_populates="wells")
