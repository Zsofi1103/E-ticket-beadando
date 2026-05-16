from flask_wtf import FlaskForm
from wtforms import SubmitField


class ReservationForm(FlaskForm):
    submit = SubmitField('Foglalás')
