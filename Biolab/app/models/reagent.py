from app import db


class Reagent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(40), nullable=False, default="Other")
    include_in_master_mix = db.Column(db.Boolean, nullable=False, default=True)
    stock_concentration = db.Column(db.String(80))
    volume_per_reaction_ul = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text)
    experiment_id = db.Column(db.Integer, db.ForeignKey("pcr_experiment.id"), nullable=False)

    experiment = db.relationship("PCRExperiment", back_populates="reagents")
