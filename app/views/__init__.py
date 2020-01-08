from .main import main
from .user import user
from .posts import posts
from .admin import admin
# 蓝本配置元祖
DEFAULT_BLUEPRINT = (
    # 蓝本前缀
    (main, ''),
    (user, '/user'),
    (posts, '/posts'),
    (admin, '/admin')
)


# 注册蓝本
def config_blueprint(app):
    for blue_print, url_prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blue_print, url_prefix=url_prefix)
