from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class RoomForm(FlaskForm):
    roomName = StringField('会议室名', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    createrID = StringField('创建者ID', validators=[DataRequired(message='不能为空')])
    location = StringField('会议室地点', validators=[DataRequired(message='不能为空')])
    submit = SubmitField('提交')
