"""
forms.py defines requirements and validation logic
for all web forms
"""
import re
from flask_wtf import FlaskForm
from wtforms import (StringField, BooleanField, PasswordField, ValidationError)
from wtforms.validators import InputRequired
from wtforms import widgets
import pytz

#  ---------- Unused imports: Needs review ------------------
#  from wtforms.widgets import (SubmitInput)
#  from wtforms import SubmitField, EmailField
#  from wtforms.validators import DataRequired, Length

class CustomPasswordField(StringField):
    """
    Original source: https://github.com/wtforms/wtforms/blob/2.0.2/wtforms/fields/simple.py#L35-L42

    A StringField, except renders an ``<input type="password">``.
    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """
    widget = widgets.PasswordInput(hide_value=False)

def validate_email(form, field):
    """
    Validates that the input in the 'email' field matches the standard email format (user@domain.tld). Raises a ValidationError if the format is not matched.

    :param form: The form where the email field resides.
    :param field: The email field to be validated.
    """
    # Found this regex here:
    # https://emailregex.com/
    if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", field.data):
        return
    raise ValidationError(
        'Email must match the standard format: user@domain.tld')


def validate_password(form, field):
    """
    Validates the password field according to NIST guidelines. Ensures that the password is between 12 and 64 characters and contains only valid characters. Raises a ValidationError if these conditions are not met.

    :param form: The form where the password field resides.
    :param field: The password field to be validated.
    """
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
    """
    Validates the username field to ensure it is between 4 and 20 characters and contains only letters and numbers. Raises a ValidationError if these conditions are not met.

    :param form: The form where the username field resides.
    :param field: The username field to be validated.
    """
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
    """
    Validates the first name field to ensure it is between 2 and 50 characters and contains only allowed characters (letters, hyphens, periods, apostrophes, and spaces). Raises a ValidationError if these conditions are not met.

    :param form: The form where the first name field resides.
    :param field: The first name field to be validated.
    """
    min_length = 2
    max_length = 50

    # Verify name isn't only spaces
    if not field.data.strip():
        raise ValidationError('First name must not be only spaces.')

    if len(field.data) < min_length:
        raise ValidationError('First Name must be at least 2 characters.')
    if len(field.data) > max_length:
        raise ValidationError('First name must not be more than 50 characters.')
    # Allowing a broader range of characters, including certain special characters like hyphens and apostrophes
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ-.\' ]*$', field.data):
        raise ValidationError('First name may only contain letters, hyphens, periods, apostrophes, and spaces')
        
def validate_last_name(form, field):
    """
    Validates the last name field to ensure it is between 2 and 50 characters and contains only allowed characters (letters, hyphens, periods, apostrophes, and spaces). Raises a ValidationError if these conditions are not met.

    :param form: The form where the last name field resides.
    :param field: The last name field to be validated.
    """
    min_length = 2
    max_length = 50

    # Verify name isn't only spaces
    if not field.data.strip():
        raise ValidationError('Last name must not be only spaces.')

    if len(field.data) < min_length:
        raise ValidationError('Last Name must be at least 2 characters.')
    if len(field.data) > max_length:
        raise ValidationError('Last name must not be more than 50 characters.')
    # Allowing a broader range of characters, including certain special characters like hyphens and apostrophes
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ-.\' ]*$', field.data):
        raise ValidationError('Last name may only contain letters, hyphens, periods, apostrophes, and spaces')

def validate_timezone(form, field):
    """
    Validates the timezone field to ensure it matches one of the known timezones in the pytz library. Raises a ValidationError if the timezone is unknown.

    :param form: The form where the timezone field resides.
    :param field: The timezone field to be validated.
    """

    
    if field.data.lower() not in list(map(str.lower,pytz.all_timezones)):
        raise ValidationError("Unknown timezone, please try again.")

class NewUserForm(FlaskForm):
    """
    Form for creating a new user. Includes fields for email, username, and password with appropriate validators for each field.
    """
    email = StringField('Email', validators=[InputRequired(), validate_email])
    username = StringField('Username', validators=[
                           InputRequired(), validate_username])
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])


class LoginForm(FlaskForm):
    """
    Form for user login. Includes fields for username and password with appropriate validators.
    """
    username = StringField('Username', validators=[
                           InputRequired(), validate_username])
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])

class ResetPasswordForm(FlaskForm):
    """
    Form for resetting a user's password. Includes fields for new password and confirm password, with validators to ensure they match and meet password requirements.
    """
    password = PasswordField('Password', validators=[
                             InputRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[
                             InputRequired(), validate_password])
    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError("Passwords do not match, please try again.")

class UpdatePersonalInfoForm(FlaskForm):
    """
    Form for updating a user's personal information. Includes fields for username, email, first name, and last name with appropriate validators for each field.
    """

    username = StringField('Username',validators=[InputRequired(), validate_username])
    email = StringField('E-Mail',validators=[InputRequired(), validate_email])
    first_name = StringField('First Name',validators=[InputRequired(), validate_first_name])
    last_name =  StringField('Last Name',validators=[InputRequired(), validate_last_name])

class UpdateCredentialsForm(FlaskForm):
    """
    Form for updating a user's credentials. Includes fields for current password, new password, and new password confirmation with appropriate validators.
    """
    current_password = CustomPasswordField('Password', validators=[InputRequired(), validate_password])
    new_password = CustomPasswordField('Confirm Password', validators=[InputRequired(), validate_password])
    new_password_confirm = CustomPasswordField('Confirm Password', validators=[InputRequired(), validate_password])

    def validate_new_password_confirm(self, field):
        """
        function to verify that the password and confirm_password match, if not a ValidationError is raised.
        """
        if field.data != self.new_password.data:
            raise ValidationError("Passwords do not match, please try again.")


class AddTaskForm(FlaskForm):
    """
    Dummy class to pass in a WTF Form for CSRF protection since we enabled protection on all routes
    """
    task_name = StringField('Task Name', validators=[InputRequired(), validate_username])

class ForgotPasswordForm(FlaskForm):
    """
    Form for initiating the password recovery process. Includes a field for the user's email with the appropriate validator.
    """
    email = StringField('email', validators=[InputRequired(), validate_email])
    
class UpdateTimeZoneForm(FlaskForm):
    """
    Form for updating a user's timezone settings. Includes fields for timezone name and a boolean field for daylight savings participation.
    """
    timezone_name = StringField('Time Zone', validators=[InputRequired(), validate_timezone])
    daylight_savings = BooleanField('Daylight Savings (Do you participate in this useless routine?)')
                    
