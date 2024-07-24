from flask import Blueprint, render_template
# , request, redirect, url_for
from app.models import User

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def home():
    return render_template('index.html')


@main_routes.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)
