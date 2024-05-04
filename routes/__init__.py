# routes/__init__.py

from flask import Blueprint

# Define blueprints for each route module
auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)

# Import route modules
from . import auth, main, admin
