from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField, SelectField
from wtforms.validators import DataRequired, Regexp, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddCardForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired()])
    position = StringField('Position*', validators=[DataRequired()])
    team = StringField('Team*', validators=[DataRequired()])
    year = StringField('Year*', validators=[DataRequired()])
    picture = FileField('Image (png, jpeg, pdf, or jpg)') #, validators=[FileAllowed(['jpg', 'png', 'jpeg', 'pdf'])])
    submit = SubmitField('Submit')


class SortCardsForm(FlaskForm):
    sort_by = SelectField(
        'Sort by',
        choices=[
            ('name', 'Name'),
            ('year', 'Year'),
            ('position', 'Position'),
            ('team', 'Team')
        ],
        default='name'
    )
    submit = SubmitField('Sort')
