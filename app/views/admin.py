from datetime import datetime
import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
import markdown
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Article, User, Comment
from app.tools import generate_id

admin = Blueprint('admin', __name__)


@admin.route('/index')
def index():
    user_count = User.query.count()
    article_count = Article.query.count()
    comment_count = Comment.query.count()
    return render_template("admin/index.html", user_count=user_count, article_count=article_count,
                           comment_count=comment_count)


@admin.route('/all_user')
@login_required
def all_user():
    page = request.args.get('page', 1, type=int)
    pagination = User().query.paginate(page, per_page=10, error_out=False)
    users = pagination.items
    return render_template('admin/all_user.html', users=users, pagination=pagination)


@admin.route('/all_article')
@login_required
def all_article():
    page = request.args.get('page', 1, type=int)
    pagination = Article().query.paginate(page, per_page=10, error_out=False)
    articles = pagination.items
    return render_template('admin/all_article.html', articles=articles, pagination=pagination)


@admin.route('/all_comment')
@login_required
def all_comment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment().query.paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/all_comment.html', comments=comments, pagination=pagination)


@admin.route('/del_user/<id>', methods=['get', 'post'])
@login_required
def del_user(id):
    print("step1")
    user = User().query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.all_user'))


@admin.route('/del_comment/<comment_id>', methods=['get', 'post'])
@login_required
def del_comment(comment_id):
    print("step1")
    comment = Comment().query.filter_by(comment_id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin.all_comment'))


@admin.route('/del_article/<article_id>')
@login_required
def del_article(article_id):
    article = Article().query.filter_by(article_id=article_id).first()
    db.session.delete(article)
    comments = Comment().query.filter_by(article_id=article_id).delete(
        synchronize_session=False)
    db.session.commit()
    print('删除文章成功!!!!')
    return redirect(url_for('admin.all_article'))


@admin.route('/add_user', methods=['POST', 'GET'])
@login_required
def add_user():
    print('step0')
    if request.method == 'POST':
        print('step1')
        username = request.form.get("username")
        pwd = request.form.get('pwd')
        check_pwd = request.form.get('check_pwd')
        email = request.form.get('email')
        user = User(username=username, password=pwd, email=email)
        db.session.add(user)
        db.session.commit()
        print('step2')
        return redirect(url_for('admin.all_user'))
    return render_template('admin/add_user.html')


@admin.route('/add_article', methods=['POST', 'GET'])
@login_required
def add_article():
    if request.method == 'POST':
        article_title = request.form.get('article_title')
        artitle_type = request.form.get('f_type')
        article_text = request.form.get('article_content')
        article_url = request.form.get('article_url')
        article_text = markdown.markdown(article_text, ['extra', 'codehilite'])

        article_id = generate_id('article')
        # article_date = strftime('%Y-%m-%d %H:%M:%S')
        article_date = datetime.utcnow()
        article_type = '技术杂谈' if artitle_type == '1' else '人生感悟'
        content = re.compile('.*?>(.*?)<').findall(article_text)
        article_summary = ''
        for x in content:
            if x:
                article_summary = article_summary + x
                if len(article_summary) > 250:
                    break
        print('article_title=', article_title)
        print('article_type=', article_type)
        print('article_date=', article_date)
        article_summary = "".join(article_summary.split())
        print('article_summary=', article_summary)
        article = Article(
            article_id=article_id,
            article_title=article_title,
            article_type=article_type,
            article_text=article_text,
            article_summary=article_summary[:180],
            article_url=article_url,
            article_date=article_date,
            user_id=current_user.id,
            article_author=current_user.username)
        db.session.add(article)
        db.session.commit()
        print('add article finished')
        articles = Article().query.limit(8)
        return redirect(url_for('admin.all_article'))
    else:
        return render_template('admin/add_article.html')
