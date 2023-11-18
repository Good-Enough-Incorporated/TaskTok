"""
forms.py defines requirements and validation logic
for all web forms
"""
import re
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, ValidationError)
from wtforms.validators import DataRequired, Email, InputRequired, Length
from wtforms.widgets import (SubmitInput)
def validate_username(form, field):
    #if len(field.data) == 0:
    #    raise ValidationError('Username is required')
    
    # This could all be handled by regex but this way is easier to build on later
    min_length = 4
    max_length = 20
    if len(field.data) < min_length:
        raise ValidationError(f'Username must be at least {min_length} characters')
    if len(field.data) > max_length:
        raise ValidationError(f'Username cannot be more than {max_length} characters')
    if re.match('^[0-9]*$', field.data):
        raise ValidationError('Username must contain letters')
    if re.match('^[A-Za-z0-9]*$', field.data):
        return # String contains valid characters only
    raise ValidationError('Username may only contain letters and numbers')
    
class NewUserForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired(), validate_username])
    password = PasswordField('Password', validators=[DataRequired()])