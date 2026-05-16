from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import InputRequired, NumberRange


class EventTimeForm(FlaskForm):
    year = IntegerField('Év', validators=[InputRequired(), NumberRange(min=1900, max=3000)])
    month = IntegerField('Hónap', validators=[InputRequired(), NumberRange(min=1, max=12)])
    day = IntegerField('Nap', validators=[InputRequired(), NumberRange(min=1, max=31)])
    hour = IntegerField('Óra', validators=[InputRequired(), NumberRange(min=0, max=23)])
    minute = IntegerField('Perc', validators=[InputRequired(), NumberRange(min=0, max=59)])
    submit = SubmitField('Mentés')
