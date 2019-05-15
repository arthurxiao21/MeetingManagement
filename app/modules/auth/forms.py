from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), ])
    password = PasswordField('密码', validators=[DataRequired()])
    rememberme = BooleanField('记住我')
    submit = SubmitField('提交')


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), ])
    fullname = StringField('全名', validators=[DataRequired(), Length(1, 64), ])
    sex = SelectField('性别', choices=[('男', '男'), ('女', '女')],
                      validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), ])
    phone = StringField('手机号', validators=[DataRequired(), Length(1, 64), ])
    role = StringField('权限')
    submit = SubmitField('提交')
