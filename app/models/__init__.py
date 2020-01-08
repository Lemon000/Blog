from .user import User
from .article import Article,Comment
from app.extensions import db

# # 用户帖子中间表
# # 一个用户可以收藏多篇文章  一片文章可以被多个用户收藏
# collections = db.Table('collections',
#                        db.Column('user.id', db.Integer, db.ForeignKey('users.id')),
#                        db.Column('post.id', db.Integer, db.ForeignKey('posts.id')),
#                        )
