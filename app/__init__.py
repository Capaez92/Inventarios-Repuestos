import os
from flask import Flask
from flask_login import LoginManager
from app.models.models import db, User, CompanySetting, Product
from config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Inicie sesión para acceder al sistema.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads and instance directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.movements import movements_bp
    from app.routes.purchases import purchases_bp
    from app.routes.suppliers import suppliers_bp
    from app.routes.categories import categories_bp
    from app.routes.reports import reports_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(movements_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Context processor for global template variables
    @app.context_processor
    def inject_global_data():
        company = CompanySetting.query.first()
        low_count = 0
        try:
            low_count = Product.query.filter(Product.current_stock <= Product.min_stock).count()
        except Exception:
            pass
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_supabase = 'postgresql' in db_uri
        return {
            'company': company,
            'low_stock_badge_count': low_count,
            'is_supabase': is_supabase,
            'db_name_display': 'Supabase PostgreSQL' if is_supabase else 'SQLite Local'
        }

    # Template filters
    @app.template_filter('currency')
    def format_currency(value):
        try:
            return f"${float(value):,.2f}"
        except:
            return "$0.00"

    with app.app_context():
        db.create_all()
        try:
            if not User.query.filter_by(username='admin').first():
                from seed import run_seed
                run_seed(app)
        except Exception:
            pass

    return app
