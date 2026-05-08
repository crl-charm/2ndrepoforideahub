from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask_socketio import SocketIO

# Create database object
db = SQLAlchemy()
_sqlalchemy_db = db
socketio = SocketIO(cors_allowed_origins="*")


def create_app():

    app = Flask(__name__)

    # Fix 1: config.py is outside the app folder, so import it properly
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config import Config
    app.config.from_object(Config)

    # connect database to app
    db.init_app(app)
    socketio.init_app(app)

    # import routes
    from app.routes.session_routes import session_bp
    from app.routes.order_routes import order_bp
    from app.routes.sales_routes import sales_bp
    from app.routes.sales_balance import sales_bp as sales_balance_bp
    from app.routes.user_routes import user_bp
    from app.routes.auth_routes import bp as auth_bp
    from app.routes.dashboard_routes import bp as dashboard_bp
    from app.routes.boardroom_routes import boardroom_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.lounge_routes import lounge_bp
    from app.routes.inventory import inventory_bp
    from app.routes.receivables import receivables_bp
    from app.routes.expenses import expenses_bp
    from app.routes.staff_performance import staff_performance_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reservations import reservations_bp
    from app.routes.receipts import receipts_bp
    from app.routes.menu import menu_bp
    from app.routes.qr_order import qr_bp, order_bp as qr_order_bp

    # register routes
    app.register_blueprint(session_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(sales_balance_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(boardroom_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(lounge_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(receivables_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(staff_performance_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(qr_order_bp)

    @app.route("/")
    def home():
        return render_template("landing.html")

    return app