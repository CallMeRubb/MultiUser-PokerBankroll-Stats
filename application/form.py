from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, BooleanField, DateField, FloatField
from wtforms.validators import DataRequired, NumberRange

class UserInputForm(FlaskForm):
    game_type = SelectField('Game Type', validators=[DataRequired()],
                            choices=[('sit_and_go', 'Sit and Go'), ('tournament', 'Tournament')])
    buy_in = IntegerField("Buy-In", validators=[NumberRange(min=0)])
    total_pot = IntegerField("Total Pot", validators=[NumberRange(min=0)])
    hours_played = FloatField("Hours Played")  # Add field for hours played
    custom_date = BooleanField("Custom Date")
    custom_date_input = DateField("Custom Date Input")
    submit = SubmitField("Generate Report")
