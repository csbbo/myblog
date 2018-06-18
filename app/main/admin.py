from flask import render_template,url_for,redirect,request,session,current_app
from . import main
from .. import db
from ..models import Article,Tag,Friend,User
from flask_login import login_user, logout_user, login_required,current_user


@main.route('/admin/',methods=['GET','POST'])
@login_required
def admin():
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        if request.method == 'GET':
            context={
                'tags':Tag.query.all(),
                'articles':Article.query.all(),
                'users':User.query.all()
            }
            return render_template('admin.html',**context)
        else:
            name = request.form.get('addtag')
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            return redirect(url_for('main.admin'))

@main.route('/addarticle/',methods=['GET','POST'])
@login_required
def add_article():
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        if request.method == 'GET':
            return render_template('add_article.html')
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            article=Article(title=title,content=content)
            db.session.add(article)
            db.session.commit()
            return redirect(url_for('main.first'))

# mod_article
@main.route('/modarticle/<id>/',methods=['GET','POST'])
@login_required
def mod_article(id):
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        tags = Tag.query.all()
        modify = Article.query.filter(Article.id==id).first()
        if request.method == 'GET':
            return render_template('mod_article.html',article=modify,tags=tags)
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            modify.content=content
            modify.title=title
            db.session.add(modify)
            db.session.commit()
            return redirect(url_for("main.mod_article",id=id))

# add article`s tags
@main.route('/addarticletag/',methods=['POST'])
@login_required
def article_add_tag():
    tagid = request.form.get('tagid')
    articleid = request.form.get('articleid')
    print(articleid+tagid)
    article=Article.query.filter(Article.id==articleid).first()
    tag=Tag.query.filter(Tag.id==tagid).first()

    article.tags.append(tag)
    db.session.add(article)
    db.session.commit()

    return "success"


# add friend link
@main.route('/friendlink/',methods=['POST'])
@login_required
def friendlink():
    name = request.form.get('friend')
    url = request.form.get('url')
    friend = Friend(name=name,url=url)
    db.session.add(friend)
    db.session.commit()
    return redirect(url_for('main.admin'))

# add tag
@main.route('/tag/',methods=['POST'])
@login_required
def tag():
    name = request.form.get('addtag')
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return redirect(url_for('main.admin'))
