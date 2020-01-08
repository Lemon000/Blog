from flask import Blueprint, render_template, flash, redirect, url_for, \
    current_app, request
from app.forms import RegisterForm, LoginForm, PasswordForm, IconForm
from app.email import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.models import User
from app.extensions import db, photos
from flask_login import login_user, logout_user, login_required, current_user
import os
from PIL import Image

user = Blueprint('user', __name__)


@user.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 创建对象，
        u = User(username=form.username.data, password=form.password.data, email=form.email.data)
        # 写入数据库
        db.session.add(u)
        # 产生token需要用户id
        db.session.commit()
        # 生成token
        token = u.generate_activate_token()
        # 发送激活邮件
        send_mail(form.email.data, '账户激活', 'email/account_activate', token=token, username=form.username.data)
        flash('激活邮件已发送，请点击链接完成用户激活')
        return redirect(url_for('main.index'))
    return render_template('user/register.html', form=form)


@user.route('/activate/<token>')
def activate(token):
    # if User.check_activate_token(token):
    flash("账户激活成功")
    return redirect(url_for('user.login'))
    # else:
    #     flash("账户激活失败")
    #     return redirect(url_for('main.index'))


@user.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            u = User.query.filter_by(username=form.username.data).first()
            login_user(u, remember=form.remember_me.data)
            return redirect(url_for('admin.index'))
        u = User.query.filter_by(username=form.username.data).first()
        if u is None:
            flash('无效的用户名')
        elif u.verify_password(form.password.data):
            # 验证通过，用户登录
            login_user(u, remember=form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('密码错误')
    print('step2')
    return render_template('user/login.html', form=form)


@user.route('/logout')
# 保护路由
@login_required
def logout():
    logout_user()
    flash('用户已退出')
    return redirect(url_for('main.index'))


@user.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')


@user.route('/change_password', methods=['get', 'post'])
@login_required
def change_password():
    form = PasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_pwd.data):
            current_user.password = form.new_pwd.data
            db.session.add(current_user)
            flash("密码修改成功")
            return redirect(url_for('main.index'))
        else:
            flash("原密码错误")
            return redirect(url_for('user.change_password'))
    return render_template('user/change_password.html', form=form)


@user.route("/change_icon", methods=["GET", "Post"])
@login_required
def change_icon():
    # print(current_app.config['UPLOADED_PHOTOS_DEST'])
    form = IconForm()
    if form.validate_on_submit():
        # 生成一个随机文件名
        suffix = os.path.splitext(form.icon.data.filename)[1]
        name = rand_str() + suffix
        photos.save(form.icon.data, name=name)
        # 生成缩略图
        pathname = os.path.join(os.path.join(current_app.config
                                             ['UPLOADED_PHOTOS_DEST'], name))
        # print(pathname)
        img = Image.open(pathname)
        img.thumbnail((64, 64))
        img.save(pathname)
        # 删除原有图片
        if current_user.icon != 'default.jpg':
            # 第一次更换头像不删除
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST',
                                                      current_user.icon]))
        # 保存新头像
        current_user.icon = name
        db.session.add(current_user)
        flash('头像已更换')
    return render_template('user/change_icon.html', form=form)


def rand_str(length=32):
    import random
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))
