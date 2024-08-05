from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from app.models import User, BaseballCard
from app.forms import LoginForm, RegistrationForm, AddCardForm, SortCardsForm
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from sqlalchemy import func
from PIL import Image
import io
import os
import magic
import pillow_heif
import fitz

main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def home():
    return render_template('landing.html')


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

    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(card.picture)

    img_io = io.BytesIO(card.picture)

    if mime_type == 'application/pdf':
        pdf_document = fitz.open(stream=img_io, filetype="pdf")
        first_page = pdf_document.load_page(0)  # Load the first page
        pix = first_page.get_pixmap()
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
    elif mime_type == 'image/heic':
        heif_file = pillow_heif.read_heif(img_io)
        img = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
    else:
        img = Image.open(img_io)


    output_io = io.BytesIO()
    img.save(output_io, 'JPEG')
    output_io.seek(0)
    
    return send_file(
        output_io,
        mimetype='image/jpeg',
        as_attachment=False,
    )

    # mime = magic.Magic(mime=True)
    # mime_type = mime.from_buffer(card.picture)
    # return send_file(
    #     io.BytesIO(card.picture),
    #     mimetype=mime_type,
    #     as_attachment=False,
    # )
     
@main_routes.route('/collections')
def collections():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.username.asc()).paginate(
        page=page, per_page=5, error_out=False)
    users = pagination.items
    count = User.query.count()
    return render_template('collections.html', users=users, pagination=pagination, count=count)


@main_routes.route('/card/<int:card_id>')
@login_required
def view_card(card_id):
    card = BaseballCard.query.filter_by(id=card_id).first()
    return render_template('view-card.html', card=card)

@main_routes.route('/user', defaults={'user_id': None}, methods=['GET', 'POST'])
@main_routes.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_profile(user_id):
    form = SortCardsForm()
    if user_id is None:
        user_id = current_user.id
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash('User not found.')
        return render_template('index.html')
    if form.validate_on_submit():
        sort_by = form.sort_by.data
        return redirect(url_for('main.user_profile', user_id=user_id, sort=sort_by))
    sort_by = request.args.get('sort', 'name', type=str)
    page = request.args.get('page', 1, type=int)
    pagination = user.cards.order_by(func.lower(getattr(BaseballCard, sort_by))).paginate(
        page=page, per_page=5, error_out=False)
    cards = pagination.items
    return render_template('profile.html', user=user, cards=cards, form=form, pagination=pagination, sort=sort_by)


@main_routes.route('/add-card', methods=['GET', 'POST'])
@login_required
def add_card():
    form = AddCardForm()
    if form.validate_on_submit():
        card = BaseballCard(name=form.name.data, position=form.position.data, team=form.team.data,
                            year=form.year.data, user_id=current_user.id)
        if form.picture.data:
            card.picture = form.picture.data.read()
        else:
            default_image_path = os.path.join(os.path.dirname(__file__), 'static', 'default.png')
            card.picture = open(default_image_path, 'rb').read()
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('main.add_card'))
    return render_template('add-card.html', form=form)


auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.user_profile', user_id=user.id))
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

