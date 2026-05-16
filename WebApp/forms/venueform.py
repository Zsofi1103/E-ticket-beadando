from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class VenueForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(max=255)])
    address = StringField('Cím', validators=[Optional(), Length(max=500)])
    capacity = IntegerField('Kapacitás', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Mentés')
