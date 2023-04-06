from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, TextAreaField, DateField, DateTimeField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    name = StringField(u'用户名', validators=[DataRequired()])
    passwd = PasswordField(u'密码', validators=[DataRequired()])
    role = StringField(u'角色', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired()])

class LoginForm(FlaskForm):
    name = StringField(u'用户名', validators=[DataRequired()])
    passwd = PasswordField(u'密码', validators=[DataRequired()])

class PasswdForm(FlaskForm):
    old_pass = PasswordField(u'旧密码', validators=[DataRequired()])
    new_pass = PasswordField(u'新密码', validators=[DataRequired()])
    rep_pass = PasswordField(u'重复密码', validators=[DataRequired()])

class ForgetPasswdForm(FlaskForm):
    email = StringField(u'邮箱', validators=[DataRequired()])
    verify_code = StringField(u'验证码', validators=[DataRequired()])
    new_pass = PasswordField(u'新密码', validators=[DataRequired()])
class LoginForm(FlaskForm):
    name = StringField(u'用户名', validators=[DataRequired()])
    passwd = PasswordField(u'密码', validators=[DataRequired()])
