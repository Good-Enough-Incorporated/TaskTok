"""
forms.py defines requirements and validation logic
for all web forms
"""
import re
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, PasswordField, ValidationError)
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
        raise ValidationError('Password must be at least '
                              f'{min_length} characters')
    if len(field.data) > max_length:
        raise ValidationError('Password cannot be more than '
                              f'{max_length} characters')
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
        raise ValidationError('Username must be at least '
                              f'{min_length} characters')
    if len(field.data) > max_length:
        raise ValidationError('Username cannot be more than '
                              f'{max_length} characters')
    if re.match(r'^\d*$', field.data):
        raise ValidationError('Username must contain letters')
    if re.match(r'^[A-Za-z\d]*$', field.data):
        return  # String contains valid characters only
    raise ValidationError('Username may only contain letters and numbers')

def validate_first_name(form, field):
    min_length = 2
    max_length = 50

    if len(field.data) < min_length:
        raise ValidationError('First Name must be at least 2 characters.')
    if len(field.data) > max_length:
        raise ValidationError('First name must not be more than 50 characters.')
    # Allowing a broader range of characters, including certain special characters like hyphens and apostrophes
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ-.\' ]*$', field.data):
        raise ValidationError('First name may only contain letters, hyphens, periods, apostrophes, and spaces')
    
def validate_last_name(form, field):
    min_length = 2
    max_length = 50

    if len(field.data) < min_length:
        raise ValidationError('Last Name must be at least 2 characters.')
    if len(field.data) > max_length:
        raise ValidationError('Last name must not be more than 50 characters.')
    # Allowing a broader range of characters, including certain special characters like hyphens and apostrophes
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ-.\' ]*$', field.data):
        raise ValidationError('Last name may only contain letters, hyphens, periods, apostrophes, and spaces')

def validate_timezone(form, field):
    import pytz
    
    if field.data.lower() not in list(map(str.lower,pytz.all_timezones)):
        raise ValidationError("Unknown timezone, please try again.")

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

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[
                             InputRequired(), validate_password])
    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError("Passwords do not match, please try again.")

class UpdatePersonalInfoForm(FlaskForm):

    username = StringField('Username',validators=[InputRequired(), validate_username])
    email = StringField('E-Mail',validators=[InputRequired(), validate_email])
    first_name = StringField('First Name',validators=[InputRequired(), validate_first_name])
    last_name =  StringField('Last Name',validators=[InputRequired(), validate_last_name])

class UpdateCredentialsForm(FlaskForm):
    current_password = PasswordField('Password', validators=[InputRequired(), validate_password])
    new_password = PasswordField('Confirm Password', validators=[InputRequired(), validate_password])
    new_password_confirm = PasswordField('Confirm Password', validators=[InputRequired(), validate_password])

    def validate_new_password_confirm(self, field):
        if field.data != self.new_password.data:
            raise ValidationError("Passwords do not match, please try again.")


class AddTaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[InputRequired(), validate_username])

class ForgotPasswordForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), validate_email])
    
class TimeZoneForm(FlaskForm):
    timezone_name = StringField('Time Zone', validators=[InputRequired(), validate_timezone])
    daylight_savings = BooleanField('Daylight Savings (Do you participate in this useless routine?)')
                    
