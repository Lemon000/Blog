# 导入表单基类
from flask_wtf import FlaskForm
# 导入相关字段
from wtforms import StringField, PasswordField, SubmitField, ValidationError, BooleanField
# 导入验证器
from wtforms.validators import DataRequired, Email, EqualTo, Length
from app.models import User
# 导入上传文件的字段级验证器
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.extensions import photos


# 注册表单
class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(),
                                              Length(6, 18, message='用户名必须在6-18个字符之间')])
    password = PasswordField('密码', validators=[DataRequired(),
                                               Length(6, 18, message='密码长度必须在6-18个字符之间')])
    confirm = PasswordField('确认密码', validators=[EqualTo('password',
                                                        message='两次密码不一致')])
    email = StringField('邮箱', validators=[Email(message='邮箱格式不正确')])
    submit = SubmitField('立即注册')

    # 自定义验证器，验证用户名
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    # 自定义验证器，验证邮箱
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')


# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('立即登录')


class PasswordForm(FlaskForm):
    old_pwd = PasswordField('原密码', validators=[DataRequired()])
    new_pwd = PasswordField("新密码", validators=[DataRequired(),
                                               Length(6, 18, message='密码长度必须在6-18个字符之间')])
    confirm = PasswordField('确认密码', validators=[EqualTo('new_pwd', message='两次密码不一致')])
    submit = SubmitField('确认修改')


# 修改头像表单
class IconForm(FlaskForm):
    icon = FileField('头像', validators=[FileRequired('请选择上传文件'), FileAllowed(photos, '只能上传图片')])
    submit = SubmitField('上传')
