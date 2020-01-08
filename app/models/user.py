from flask import current_app
from app.extensions import db, login_manger
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.article import Article
import os


class User(UserMixin, db.Model):
    # 指定表名
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(64), default='default.jpg')
    # # 添加关联模型，相当于在关联的模型中动态的添加了一个字段
    # # 参数说明：
    # # 第一个参数：唯一一个必须的参数，关联的模型类名
    # # backref：反向引用的字段名
    # # lazy：指定加载关联数据的方式，dynamic:不加载记录，但是提供关联查询
    # posts = db.relationship('Posts', backref='user', lazy='dynamic')
    # favorites = db.relationship('Posts', secondary='collections', backref=db.backref('users', lazy='dynamic'),
    #                             lazy='dynamic')

    # 保护字段
    @property
    def password(self):
        raise AttributeError('密码是不可读属性')

    # # 判断用户是否收藏
    # def is_favorite(self, pid):
    #     # 获取所有收藏的帖子
    #     favorites = self.favorites.all()
    #     # 通过判断传过来的帖子是否在 收藏的列表中
    #     # 最后转成列表 判断长度 如果大于0 表示收藏
    #     posts = list(filter(lambda p: p.id == pid, favorites))
    #     if len(posts) > 0:
    #         return True
    #     else:
    #         return False
    #
    # # 收藏帖子
    # def add_favorite(self, pid):
    #     p = Posts.query.get(pid)
    #     self.favorites.append(p)
    #
    # # 取消收藏
    # def del_favorite(self, pid):
    #     p = Posts.query.get(pid)
    #     self.favorites.remove(p)

    # 设置密码，加密存储
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 密码校验
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成用户激活的token
    def generate_activate_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in)
        return s.dumps({'id': self.id})

    # 激活账户时的token校验,校验时不知道用户信息，需要静态方法
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return False
        user = User.query.get(data.get('id'))
        if user is None:
            # 不存在此用户
            return False
        if not user.confirmed:
            # 账户没有激活是才激活
            user.confirmed = True
            db.session.add(user)
        return True

class Commparam(db.Model):
    __tablename__ = 'commparam'
    # 参数名称
    param_name = db.Column(db.String(10), primary_key=True)
    # 参数值1
    param_value = db.Column(db.Integer, default=1)
    # 参数值2
    param_text = db.Column(db.String(100))
    # 参数状态 0-正常 1-停用
    param_stat = db.Column(db.String(2), default='0')


@login_manger.user_loader
def loader_user(user_id):
    return User.query.get(int(user_id))


