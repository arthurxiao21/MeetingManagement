import logging
import os
from functools import partial
from logging.config import fileConfig

from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.shared_data import SharedDataMiddleware

from conf.config import config

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
fileConfig('D://codes/PycharmWorkSpace/MeetingManagement/conf/log-app.conf')


def get_logger(name):
    return logging.getLogger(name)


def get_basedir():
    return os.path.abspath(os.path.dirname(__file__))


def get_config():
    return config[os.getenv('FLASK_CONFIG') or 'default']


UPLOAD_FOLDER = "D://codes/PycharmWorkSpace/temp"
HERE = os.path.abspath(os.path.dirname(__file__))
get_file_path = partial(os.path.join, HERE, UPLOAD_FOLDER)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    # 上传文件设置
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/i/': get_file_path()
    })

    login_manager.init_app(app)

    from app.modules.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.modules.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # from app.modules.documentation import documentation as documentation_blueprint
    # app.register_blueprint(documentation_blueprint)
    #
    from app.modules.file import file as file_blueprint
    app.register_blueprint(file_blueprint)

    from app.modules.task import task as task_blueprint
    app.register_blueprint(task_blueprint)

    from app.modules.notice import notice as notice_blueprint
    app.register_blueprint(notice_blueprint)

    from app.modules.room import room as room_blueprint
    app.register_blueprint(room_blueprint)

    from app.modules.schedule import schedule as schedule_blueprint
    app.register_blueprint(schedule_blueprint)

    return app
