"""
Research Grant Management System - Flask Application Factory
"""
import os
from flask import Flask, render_template
from .config import config
from .extensions import db, login_manager, migrate, csrf


def create_app(config_name=None):
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.proposals import proposals_bp
    from .routes.reviews import reviews_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(proposals_bp, url_prefix='/proposals')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Shell context for flask shell
    @app.shell_context_processor
    def make_shell_context():
        from .models.user import User
        from .models.proposal import Proposal, ProposalDocument
        from .models.review import Review
        return {
            'db': db,
            'User': User,
            'Proposal': Proposal,
            'ProposalDocument': ProposalDocument,
            'Review': Review
        }
    
    return app
