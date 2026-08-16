from datetime import date, datetime, timezone

from app import db


class PCRExperiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    pcr_type = db.Column(db.String(80), nullable=False, default="Custom PCR")
    target = db.Column(db.String(160))
    reaction_volume_ul = db.Column(db.Float, nullable=False, default=25.0)
    instrument = db.Column(db.String(160))
    experiment_date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="Draft")
    notes = db.Column(db.Text)
    replicate_type = db.Column(db.String(40), nullable=False, default="None")
    technical_replicates = db.Column(db.Integer, nullable=False, default=1)
    biological_replicates = db.Column(db.Integer, nullable=False, default=1)
    sample_count = db.Column(db.Integer, nullable=False, default=0)
    positive_controls = db.Column(db.Integer, nullable=False, default=0)
    negative_controls = db.Column(db.Integer, nullable=False, default=0)
    ntcs = db.Column(db.Integer, nullable=False, default=0)
    master_mix_excess_percent = db.Column(db.Float, nullable=False, default=0.0)
    extra_reactions = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
    assay_id = db.Column(db.Integer, db.ForeignKey("assay.id"))
    template_id = db.Column(db.Integer, db.ForeignKey("pcr_template.id"))

    assay = db.relationship("Assay", back_populates="experiments")
    template = db.relationship("PCRTemplate", back_populates="experiments")
    samples = db.relationship("Sample", back_populates="experiment")
    controls = db.relationship("Control", back_populates="experiment")
    reagents = db.relationship("Reagent", back_populates="experiment", cascade="all, delete-orphan")
    programs = db.relationship("PCRProgram", back_populates="experiment", cascade="all, delete-orphan")
    plates = db.relationship("Plate", back_populates="experiment", cascade="all, delete-orphan")
