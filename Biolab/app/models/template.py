from datetime import datetime, timezone

from app import db


class PCRTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    pcr_type = db.Column(db.String(80), nullable=False, default="Custom PCR")
    target = db.Column(db.String(160))
    instrument = db.Column(db.String(160))
    protocol_json = db.Column(db.Text)
    reaction_volume_ul = db.Column(db.Float, nullable=False, default=25.0)
    replicate_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    assay_id = db.Column(db.Integer, db.ForeignKey("assay.id"))

    assay = db.relationship("Assay", back_populates="templates")
    experiments = db.relationship("PCRExperiment", back_populates="template")
