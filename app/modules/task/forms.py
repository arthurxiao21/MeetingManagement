from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length


class TaskForm(FlaskForm):
    userID = StringField('用户ID', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    isFinish = SelectField('是否完成', choices=[('1', '已完成'), ('2', '未完成')], )
    endTime = DateTimeField('截止时间')
    desc = StringField('任务描述', validators=[DataRequired(message='不能为空')])
    submit = SubmitField('提交')
