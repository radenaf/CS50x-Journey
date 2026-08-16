from datetime import datetime, timezone

from app import db


class Assay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    target = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    templates = db.relationship("PCRTemplate", back_populates="assay")
    experiments = db.relationship("PCRExperiment", back_populates="assay")
