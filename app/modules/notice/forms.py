import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length


class NoticeForm(FlaskForm):
    createrID = IntegerField('创建者ID')
    pubTime = DateTimeField('发布时间', default=datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"))
    startTime = DateTimeField('开始时间')
    endTime = DateTimeField('结束时间')
    urgency = SelectField('重要程度', choices=[('特别紧急', '特别紧急'), ('一般紧急', '一般紧急'), ('全员知晓', '全员知晓')],
                          validators=[DataRequired(message='不能为空')])
    comment = StringField('通知内容', validators=[DataRequired(message='不能为空'), Length(0, 256, message='长度不正确')])
    status = BooleanField('生效标识', default=True)
    submit = SubmitField('提交')
