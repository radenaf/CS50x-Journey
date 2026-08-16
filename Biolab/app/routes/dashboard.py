from datetime import date

from flask import Blueprint, render_template

from app import db
from app.models import Assay, PCRExperiment, PCRTemplate

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def dashboard():
    stats = {
        "experiments": db.session.query(PCRExperiment).count(),
        "templates": db.session.query(PCRTemplate).count(),
        "assays": db.session.query(Assay).count(),
    }
    recent_experiments = PCRExperiment.query.order_by(PCRExperiment.updated_at.desc()).limit(5).all()
    return render_template("dashboard.html", stats=stats, recent_experiments=recent_experiments, today=date.today())
