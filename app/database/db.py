from flask_sqlalchemy import SQLAlchemy
from app.utils.logger import LoggerManager

logger = LoggerManager().get_logger(__name__)

db = SQLAlchemy()

def init_db(app):
    logger.info("Initializing database connection...")
    try:
        db.init_app(app)
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("Database initialization completed!")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise