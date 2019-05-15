from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length


class MeetingForm(FlaskForm):
    meetingTitle = StringField('会议标题', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    startTime = DateTimeField('开始时间')
    durationTime = SelectField('持续时间', choices=[('1小时', '1小时'), ('2小时', '2小时'), ('3小时', '3小时')],
                               validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    place = SelectField('地点', choices=[('416', '会议室1'), ('422', '会议室2'), ('530', '会议室3')],
                        validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    desc = StringField('描述', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    submit = SubmitField('提交')
