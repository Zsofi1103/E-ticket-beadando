from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CategoryForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Mentés')
