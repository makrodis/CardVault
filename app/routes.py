from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from app.models import User, BaseballCard
from app.forms import LoginForm, RegistrationForm, AddCardForm
from flask_login import login_user, logout_user, login_required, current_user
from app import db
import io


main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def home():
    return render_template('index.html')


@main_routes.route('/image')
def image():
    card_id = request.args.get('card_id')
    if not card_id:
        flash('Card id not given.')
        return render_template('index.html')
    card = db.session.query(BaseballCard).get(card_id)
    if not card or not card.picture:
        flash('Cards not found.')
        return render_template('index.html')
    return send_file(
        io.BytesIO(card.picture), 
        mimetype='image/png',
        as_attachment=False,
    )

@main_routes.route('/collections')
@login_required
def collections():
    return render_template('collections.html', users=User.query.all())

@main_routes.route('/user', defaults={'user_id': None})
@main_routes.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    if user_id is None:
        user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User not found.')
        return render_template('index.html')
    return render_template('profile.html', user=user)


@main_routes.route('/add-card', methods=['GET', 'POST'])
@login_required
def add_card():
    form = AddCardForm()
    if form.validate_on_submit():
        card = BaseballCard(name=form.name.data, position=form.position.data, team=form.team.data,
                            year=form.year.data, user_id=current_user.id)
        if form.picture.data:
            card.picture = form.picture.data.read()
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('main.add_card'))
    return render_template('add-card.html', form=form)


auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid email or password.')
    return render_template('login.html', form=form)


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.create_password(form.password.data)
        if User.query.filter_by(username=user.username).first():
            flash('Username already in use.')
            return redirect(url_for('auth.register'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

