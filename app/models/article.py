from app.extensions import db
from datetime import datetime


class Article(db.Model):
    __tablename__ = 'article'
    article_id = db.Column(db.String(20), primary_key=True)
    article_title = db.Column(db.String(100), nullable=False)
    article_text = db.Column(db.Text)
    article_summary = db.Column(db.String(255))
    article_read_cnt = db.Column(db.Integer, default=0)
    article_sc = db.Column(db.Integer, default=0)
    article_pl = db.Column(db.Integer, default=0)
    article_date = db.Column(db.DateTime, default=datetime.utcnow())
    article_url = db.Column(db.Text)
    article_type = db.Column(db.String(10))
    article_author = db.Column(db.String(20))
    user_id = db.Column(db.String(20))


class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.String(20), primary_key=True)
    comment_text = db.Column(db.Text)
    comment_date = db.Column(db.DateTime)
    comment_name = db.Column(db.String(30))
    comment_support = db.Column(db.Integer, default=0)
    comment_oppose = db.Column(db.Integer, default=0)
    article_id = db.Column(db.String(20), nullable=False)
