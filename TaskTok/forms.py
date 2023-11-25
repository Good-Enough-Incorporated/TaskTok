"""
forms.py defines requirements and validation logic
for all web forms
"""
import re
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, ValidationError)
from wtforms.validators import InputRequired


#  ---------- Unused imports: Needs review ------------------
#  from wtforms.widgets import (SubmitInput)
#  from wtforms import SubmitField, EmailField
#  from wtforms.validators import DataRequired, Length

def validate_email(form, field):
    # Found this regex here:
    # https://emailregex.com/
    if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", field.data):
        return
    raise ValidationError(
        'Email must match the standard format: user@domain.tld')


def validate_password(form, field):
    # NIST password recommendations:
    # https://www.auditboard.com/blog/nist-password-guidelines/
    # https://github.com/usnistgov/800-63-3
    min_length = 12
    max_length = 64
    if len(field.data) < min_length:
        raise ValidationError(f'Password must be at least {
                              min_length} characters')
    if len(field.data) > max_length:
        raise ValidationError(f'Password cannot be more than {
                              max_length} characters')
    if re.match(r'^[A-Za-z\d._@$!%*#?&^-]*$', field.data):
        return  # String contains valid characters only
    raise ValidationError('Password may only contain letters, numbers,'
                          + ' and the following characters: . _ @ $ ! % * # ? & ^ -')


def validate_username(form, field):
    # if len(field.data) == 0:
    #    raise ValidationError('Username is required')

    # This could all be handled by regex but this way is easier to build on later
    min_length = 4
    max_length = 20
    if len(field.data) < min_length:
        raise ValidationError(f'Username must be at least {
                              min_length} characters')
    if len(field.data) > max_length:
        raise ValidationError(f'Username cannot be more than {
                              max_length} characters')
    if re.match(r'^\d*$', field.data):
        raise ValidationError('Username must contain letters')
    if re.match(r'^[A-Za-z\d]*$', field.data):
        return  # String contains valid characters only
    raise ValidationError('Username may only contain letters and numbers')


class NewUserForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), validate_email])
    username = StringField('Username', validators=[
                           InputRequired(), validate_username])
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), validate_username])
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])
