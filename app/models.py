# -*- coding: utf-8 -*-

import json
import os
import uuid
# import magic
from datetime import datetime

from flask_login import UserMixin
from peewee import MySQLDatabase, Model, CharField, BooleanField, IntegerField, DateTimeField
from werkzeug.security import check_password_hash

from app import login_manager
from conf.config import config

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from flask import abort, request

from app.utils import get_file_md5, get_file_path
from app.mimes import IMAGE_MIMES, AUDIO_MIMES, VIDEO_MIMES

cfg = config[os.getenv('FLASK_CONFIG') or 'default']

db = MySQLDatabase(host=cfg.DB_HOST, user=cfg.DB_USER, passwd=cfg.DB_PASSWD, database=cfg.DB_DATABASE)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        # return str(r)
        return json.dumps(r, ensure_ascii=False)


# 用户表
class User(UserMixin, BaseModel):
    username = CharField(unique=True)  # 用户名
    password = CharField()  # 密码
    fullname = CharField()  # 真实性名
    sex = CharField()  # 用户性别
    email = CharField()  # 邮箱
    phone = CharField()  # 电话
    role = IntegerField()  # 用户身份
    status = BooleanField(default=True)  # 生效失效标识

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


# 会议日程安排表
class Meeting(BaseModel):
    meetingTitle = CharField()  # 会议名称
    startTime = DateTimeField()  # 创建时间
    durationTime = CharField()  # 持续时间
    createrID = IntegerField()  # 创建者ID
    place = CharField()  # 会议地点
    desc = CharField()  # 会议描述


# 会议记录表
class documentation(BaseModel):
    meetingID = IntegerField()  # 会议ID
    thingsTODO = IntegerField()  # 待办事项


# 通知表
class notice(BaseModel):
    createrID = IntegerField()  # 创建者ID
    pubTime = DateTimeField()  # 发布时间
    startTime = DateTimeField()  # 起始时间
    endTime = DateTimeField()  # 终止时间
    urgency = CharField()  # 紧急程度    1:特别紧急  2：一般紧急  3：全员知晓
    comment = CharField()  # 通知内容
    status = BooleanField(default=True)  # 生效失效标识


# 任务表
class task(BaseModel):
    userID = IntegerField()  # 用户ID
    isFinish = IntegerField()  # 是否完成   1：已完成  0：未完成
    createTime = DateTimeField(default=datetime.now())  # 创建时间
    endTime = DateTimeField()  # 截至时间
    desc = CharField()  # 任务描述


# 文件表
class Pastefile(BaseModel):
    uploaderID = IntegerField()  # 上传者ID
    meetingID = IntegerField()  # 会议ID
    fileName = CharField()  # 文件名字
    fileHash = CharField()  # 文件路径
    fileMD5 = CharField()  # 文件MD5
    uploadTime = DateTimeField()  # 文件上传时间
    mimeType = CharField()  # 文件类型
    size = CharField()  # 文件大小

    # def __init__(self, filename='', mimetype='application/octet-stream',
    #              size=0, filehash=None, filemd5=None):
    #     self.uploadTime = datetime.now()
    #     self.mimeType = mimetype
    #     self.size = int(size)
    #     self.fileHash = filehash if filehash else self._hash_filename(filename)
    #     self.fileName = filename if filename else self.fileHash
    #     self.fileMD5 = filemd5

    @staticmethod
    def _hash_filename(filename):
        _, _, suffix = filename.rpartition('.')
        return '%s.%s' % (uuid.uuid4().hex, suffix)

    @classmethod
    def get_by_filehash(cls, filehash, code=404):
        return cls.get(cls.fileHash == filehash) or abort(code)

    @classmethod
    def get_by_md5(cls, filemd5):
        try:
            rst = cls.get(cls.fileMD5 == filemd5)
            return rst
        except Exception:
            return None

    @classmethod
    def create_by_upload_file(cls, uploaded_file):
        # rst = cls(uploaded_file.filename, uploaded_file.mimetype)
        uploadTime = datetime.now()
        mimeType = uploaded_file.mimetype
        size = 0
        fileHash = Pastefile._hash_filename(uploaded_file.filename)
        fileName = uploaded_file.filename if uploaded_file.filename else fileHash
        rst = cls.create(fileName=fileName, mimeType=mimeType, size=size, fileHash=fileHash, uploadTime=uploadTime)
        print(rst.path)
        uploaded_file.save(rst.path)
        with open(rst.path, 'rb') as f:
            filemd5 = get_file_md5(f)
            uploaded_file = cls.get_by_md5(filemd5)
            if uploaded_file:
                os.remove(rst.path)
                return uploaded_file
        filestat = os.stat(rst.path)
        rst.size = filestat.st_size
        rst.fileMD5 = filemd5
        return rst

    @property
    def path(self):
        return get_file_path(self.fileHash)

    def get_url(self, subtype, is_symlink=False):
        hash_or_link = self.symlink if is_symlink else self.filehash
        return 'http://{host}/{subtype}/{hash_or_link}'.format(
            subtype=subtype, host=request.host, hash_or_link=hash_or_link)

    @property
    def url_i(self):
        return self.get_url('i')

    @property
    def url_p(self):
        return self.get_url('p')

    @property
    def url_s(self):
        return self.get_url('s', is_symlink=True)

    @property
    def url_d(self):
        return self.get_url('d')

    @property
    def quoteurl(self):
        return quote(self.url_i)

    @property
    def is_image(self):
        return self.mimeType in IMAGE_MIMES

    @property
    def is_audio(self):
        return self.mimeType in AUDIO_MIMES

    @property
    def is_video(self):
        return self.mimeType in VIDEO_MIMES

    @property
    def is_pdf(self):
        return self.mimeType == 'application/pdf'

    @property
    def type(self):
        for t in ('image', 'pdf', 'video', 'audio'):
            if getattr(self, 'is_' + t):
                return t
        return 'binary'


# 会议室表
class room(BaseModel):
    roomName = CharField()  # 会议室编号
    createTime = DateTimeField(default=datetime.now())  # 创建时间
    createrID = IntegerField()  # 创建者ID
    location = CharField()  # 地点描述


# 会议室预约信息表
class order(BaseModel):
    ordererID = IntegerField()  # 预约人ID
    orderTime = DateTimeField()  # 预约时间
    startTime = DateTimeField()  # 起始时间
    endTime = DateTimeField()  # 结束时间
    roomID = IntegerField()  # 预约会议室编号


# 预约室设备信息表
class roomInfo(BaseModel):
    roomID = IntegerField()  # 会议室ID
    hasProjecter = IntegerField()  # 是否有投影 1:有 下同
    hasPC = IntegerField()  # 是否有电脑
    desc = CharField()  # 其他描述


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# 建表
def create_table():
    db.connect()
    db.create_tables([User, Meeting, documentation, notice, task, Pastefile, room, order, roomInfo])


if __name__ == '__main__':
    create_table()
