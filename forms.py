from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FloatField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class FundForm(FlaskForm):
    name = StringField('Member Name', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    method = SelectField('Payment Method', 
                        choices=[('bKash', 'bKash'), ('Nagad', 'Nagad'), ('Cash', 'Cash'), ('Other', 'Other')],
                        validators=[DataRequired()])
    submit = SubmitField('Add Fund')

class ExpenseForm(FlaskForm):
    title = StringField('Expense Title', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Add Expense')

class FundSubmissionForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=50)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=11, max=15)])
    amount = FloatField('Amount', validators=[DataRequired()])
    transaction_id = StringField('Transaction ID', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', 
                        choices=[('bKash', 'bKash'), ('Nagad', 'Nagad'), ('Cellfin', 'Cellfin')],
                        validators=[DataRequired()])
    screenshot = FileField('Screenshot (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Submit Fund')
