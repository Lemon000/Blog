# 导入相关拓展类库
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_moment import Moment
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class

# 创建相关扩展对象
bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manger = LoginManager()
photos = UploadSet('photos', IMAGES)


# 配置函数
def config_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manger.init_app(app)
    # 会话信息保护级别
    # None 不使用
    # basic 基本级别
    # strong 用户信息更改立即退出
    login_manger.session_protection = 'strong'
    # 设置登录页面端点 当用户访问需要登录才能访问的页面
    # 若你没有登录 会自动跳转
    login_manger.login_view = 'user.login'
    # 设置提示信息 默认是英文
    login_manger.login_message = '需要登录才可访问'
    # 上传文件初始化
    configure_uploads(app,photos)
    patch_request_class(app, size=None)
