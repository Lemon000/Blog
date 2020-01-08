from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class PostsForm(FlaskForm):
    # 如果想要设置字段的其他属性，通过render_kw设置
    content = TextAreaField('', render_kw={'placeholder': '这一刻的想法...'},
                            validators=[DataRequired(), Length(1, 128, message='哪这么多话')])
    submit = SubmitField('发表')
