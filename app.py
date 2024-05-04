import os
from flask import Flask, render_template
from extensions import db, migrate, csrf, login_manager

def create_app(config=None):
    app = Flask(__name__, template_folder='templates')
    if config is None:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '40a8627889499172e11d1c6603e7f61b077b546cecb70c3504f618ce7748e1e3')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        app.config.from_mapping(config)

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import and register blueprints inside the create_app function
    from routes.auth import auth
    from routes.main import main
    from routes.admin import admin

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)