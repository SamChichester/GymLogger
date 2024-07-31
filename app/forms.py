from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, IntegerField, RadioField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, InputRequired, Length
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')


def weight_check(form, field):
    if field.data < 0:
        raise ValidationError('Weight must be 0 or greater.')


def reps_check(form, field):
    if field.data < 1:
        raise ValidationError('Reps must be 1 or greater.')


class ExerciseForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[DataRequired()])
    weight = FloatField('Weight', validators=[InputRequired(), weight_check])
    reps = IntegerField('Reps', validators=[InputRequired(), reps_check])
    submit = SubmitField('Add Exercise')


class EditExerciseForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[DataRequired()])
    submit = SubmitField('Edit Exercise')


class AddProgressionForm(FlaskForm):
    weight = FloatField('Weight', validators=[DataRequired()])
    reps = IntegerField('Reps', validators=[DataRequired()])
    submit = SubmitField('Add Progression')


class EditProgressionForm(FlaskForm):
    progression_element = SelectField('Progression Element', choices=[], coerce=int, validators=[DataRequired()])
    update_weight = FloatField('Weight', validators=[DataRequired()])
    update_reps = IntegerField('Reps', validators=[DataRequired()])
    edit_submit = SubmitField('Update Progression')
    delete_submit = SubmitField('Delete Progression')


class PreferencesForm(FlaskForm):
    weight_unit = RadioField('Weight Unit', choices=[('lbs', 'Pounds (lbs)'), ('kgs', 'Kilograms (kgs)')], validators=[DataRequired()])
    display_date = RadioField('Display Format', choices=[('%m/%d/%Y', 'mm/dd/yyyy'), ('%d/%m/%Y', 'dd/mm/yyyy'), ('%Y/%m/%d', 'yyyy/mm/dd')], validators=[DataRequired()])
    privacy = RadioField('Privacy', choices=[('false', 'Private'), ('true', 'Public')], validators=[DataRequired()])
    submit = SubmitField('Save Preferences')


class SendFriendRequestForm(FlaskForm):
    friend_code = StringField('Friend Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Add Friend')


class ManageFriendRequestsForm(FlaskForm):
    accept = SubmitField('Accept')
    reject = SubmitField('Reject')
