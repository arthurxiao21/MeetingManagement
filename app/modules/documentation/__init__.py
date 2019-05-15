from flask import Blueprint

documentation = Blueprint('documentation', __name__)

from . import views, forms, errors
