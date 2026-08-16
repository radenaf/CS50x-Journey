from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    if isinstance(config_class, dict):
        app.config.from_object(Config)
        app.config.from_mapping(config_class)
    else:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import register_models
    register_models()

    from app.database import ensure_development_schema
    with app.app_context():
        ensure_development_schema()

    from app.routes.dashboard import dashboard_bp
    from app.routes.pcr_assistant import pcr_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pcr_bp, url_prefix="/pcr")

    with app.app_context():
        db.create_all()

    return app
