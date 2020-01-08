from flask import Blueprint, render_template, current_app, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.forms import PostsForm
from app.models import Article, Comment, User
from flask_login import current_user, login_required
from app.extensions import db
import markdown
from app.tools import generate_id
from datetime import datetime

main = Blueprint("main", __name__)
from time import strftime
import re


@main.route('/', methods=['GET', 'POST'])
def index():
    articles = Article().query.all()
    print(articles)
    page = request.args.get('page', 1, type=int)
    pagination = Article().query.paginate(page, per_page=3,
                                          error_out=False)
    posts = pagination.items
    print(posts)
    return render_template('main/index.html', articles=articles, posts=posts, pagination=pagination)


@main.route('/jiami/')
def jiami():
    return generate_password_hash('123456')


@main.route('/check/<password>')
def check(password):
    # 密码校验函数，加密后的值 密码
    # 正确：True  错误：False
    if check_password_hash(
            'pbkdf2:sha256:50000$kalYYPVa$d5ec029ca44b0ddc7a26373cee9a46a3cef3c5da442995564b550108105d51a3',
            password):
        return "密码正确"
    else:
        return "密码错误"


@main.route('/generate_token/')
def generate_token():
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=3600)
    # 加密指定的数据，以字典的形式传入
    return s.dumps({'id': 250})


@main.route('/activate/<token>')
def activate(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return 'token有误'
    return str(data.get('id'))


@main.route('/wrarticle/', methods=['GET', 'POST'])
@login_required
def wrarticle():
    if request.method == 'POST':
        article_title = request.form.get('article_title')
        artitle_type = request.form.get('f_type')
        article_text = request.form.get('article_content')
        article_url = request.form.get('article_url')
        article_text = markdown.markdown(article_text, ['extra', 'codehilite'])

        article_id = generate_id('article')
        # article_date = strftime('%Y-%m-%d %H:%M:%S')
        article_date = datetime.utcnow()
        if artitle_type == '1':
            article_type = 'python'
        elif artitle_type == '2':
            article_type = 'java'
        else:
            article_type = '其他'
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
        return render_template(
            'article/article.html', article=article, articles=articles)
    else:
        return render_template('article/wrarticle.html')


@main.route('/edit_article/<article_id>', methods=['post', 'get'])
@login_required
def edit_article(article_id):
    article = Article().query.filter_by(article_id=article_id).first()
    if request.method == 'POST':
        article_title = request.form.get('article_title')
        artitle_type = request.form.get('f_type')
        article_text = request.form.get('article_content')
        article_url = request.form.get('article_url')
        article_text = markdown.markdown(article_text, ['extra', 'codehilite'])
        # article_date = strftime('%Y-%m-%d %H:%M:%S')
        article_date = datetime.utcnow()
        if artitle_type == '1':
            article_type = 'python'
        elif artitle_type == '2':
            article_type = 'java'
        else:
            article_type = '其他'
        content = re.compile('.*?>(.*?)<').findall(article_text)
        article_summary = ''
        for x in content:
            if x:
                article_summary = article_summary + x
                if len(article_summary) > 250:
                    break
        article_summary = "".join(article_summary.split())
        article.article_title = article_title
        article.article_type = article_type
        article.article_text = article_text
        article.article_summary = article_summary[:180]
        article.article_url = article_url
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.get_article', article_id=article_id))
    return render_template('article/wrarticle.html', article=article)


@main.route('/get_article/<article_id>/')
def get_article(article_id):
    article = Article().query.filter_by(article_id=article_id).first()
    article.article_read_cnt = article.article_read_cnt + 1
    db.session.add(article)
    db.session.commit()
    articles = Article().query.limit(3)
    comments = Comment().query.filter_by(article_id=article_id).all()
    return render_template(
        'article/article.html', article=article, articles=articles, comments=comments)


@main.route('/wrcomment/<article_id>', methods=["POST"])
@login_required
def wrcomment(article_id):
    print('article_id:', article_id)
    comment_name = current_user.username
    commentary = request.form.get("commentary")
    commentary = markdown.markdown(commentary, ['extra', 'codehilite'])
    comment_id = generate_id('comment')
    comment_date = datetime.utcnow()
    print('comment:', commentary)
    comment = Comment(
        comment_id=comment_id,
        comment_text=commentary,
        comment_date=comment_date,
        comment_name=comment_name,
        article_id=article_id)
    db.session.add(comment)
    db.session.commit()
    article = Article().query.filter_by(article_id=article_id).first()
    article.article_pl += 1
    db.session.add(article)
    db.session.commit()
    return redirect(url_for("main.get_article", article_id=article_id))


@main.route('/comment_oppose/<comment_id>')
def comment_oppose(comment_id):
    comment = Comment().query.filter_by(comment_id=comment_id).first()
    comment.comment_oppose += 1
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("main.get_article", article_id=comment.article_id))


@main.route('/comment_support/<comment_id>')
def comment_support(comment_id):
    print('comment_id:', comment_id)
    comment = Comment().query.filter_by(comment_id=comment_id).first()
    comment.comment_support += 1
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("main.get_article", article_id=comment.article_id))


@main.route('/article_love/<article_id>')
def article_love(article_id):
    article = Article().query.filter_by(article_id=article_id).first()
    article.article_sc += 1
    db.session.add(article)
    db.session.commit()
    return redirect(url_for("main.get_article", article_id=article.article_id))


@main.route('/del_article/<article_id>')
@login_required
def del_article(article_id):
    article = Article().query.filter_by(article_id=article_id).first()
    db.session.delete(article)
    comments = Comment().query.filter_by(article_id=article_id).delete(
        synchronize_session=False)
    db.session.commit()
    return redirect(url_for('main.manage_article'))


@main.route('/manage_article/')
@login_required
def manage_article():
    articles = Article().query.filter_by(user_id=current_user.id).all()
    comment_count = Comment.query.filter_by
    return render_template('article/manage_article.html', articles=articles)


@main.route('/python/')
def get_python():
    articles = Article().query.filter_by(article_type='python').all()
    page = request.args.get('page', 1, type=int)

    pagination = Article().query.filter_by(article_type='python').paginate(page, per_page=3,
                                                                           error_out=False)
    posts = pagination.items
    return render_template('main/index.html', articles=articles, posts=posts, pagination=pagination)


@main.route('/java/')
def get_java():
    articles = Article().query.filter_by(article_type='java').all()
    page = request.args.get('page', 1, type=int)

    pagination = Article().query.filter_by(article_type='java').paginate(page, per_page=3,
                                                                         error_out=False)
    posts = pagination.items
    return render_template('main/index.html', articles=articles, posts=posts, pagination=pagination)


@main.route('/others/')
def get_others():
    articles = Article().query.filter_by(article_type='其他').all()
    page = request.args.get('page', 1, type=int)

    pagination = Article().query.filter_by(article_type='java').paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('main/index.html', articles=articles, posts=posts, pagination=pagination)
