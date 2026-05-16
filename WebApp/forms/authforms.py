from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


class RegistrationForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(max=255)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Jelszó', validators=[DataRequired(), Length(min=6), Regexp(r'^\S+$', message='A jelszó nem tartalmazhat szóközt')])
    password2 = PasswordField('Jelszó ismét', validators=[DataRequired(), EqualTo('password', message='A jelszavak nem egyeznek')])
    submit = SubmitField('Regisztráció')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Jelszó', validators=[DataRequired(), Regexp(r'^\S+$', message='A jelszó nem tartalmazhat szóközt')])
    submit = SubmitField('Bejelentkezés')


class ProfileForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(max=255)])
    current_password = PasswordField('Jelenlegi jelszó (ha jelszót változtatsz)')
    new_password = PasswordField('Új jelszó', validators=[Length(min=6), Regexp(r'^\S+$', message='A jelszó nem tartalmazhat szóközt')])
    new_password2 = PasswordField('Új jelszó ismét', validators=[EqualTo('new_password', message='A jelszavak nem egyeznek')])
    submit = SubmitField('Mentés')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField('Jelszó visszaállítása')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField('Új jelszó', validators=[DataRequired(), Length(min=6), Regexp(r'^\S+$', message='A jelszó nem tartalmazhat szóközt')])
    new_password2 = PasswordField('Új jelszó ismét', validators=[DataRequired(), EqualTo('new_password', message='A jelszavak nem egyeznek')])
    submit = SubmitField('Jelszó mentése')
