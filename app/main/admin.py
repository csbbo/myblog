from flask import render_template,url_for,redirect,request,session,current_app
from . import main
from .. import db
from ..models import Article,Tag,Friend,User,Tool
from flask_login import login_user, logout_user, login_required,current_user
import re
from datetime import datetime

# 管理主页
@main.route('/admin/',methods=['GET'])
@login_required
def admin():
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        context={
            'tags':Tag.query.all(),
            'articles':Article.query.all(),
            'users':User.query.all()
        }
        return render_template('admin.html',**context)

# 添加文章
@main.route('/articleadd/',methods=['GET','POST'])
@login_required
def article_add():
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        if request.method == 'GET':
            return render_template('article_add.html')
        else:
            md = request.form.get('content')
            # 分组提取title,tag,preview,content
            article = re.search(r'title:(.*)\ntag:(.*)\n\n([\s\S]*)\n<!--.*preview.*-->\n([\s\S]*)',md)
            if article:
                title = article.group(1)
                tags = article.group(2).split(' ')
                content_preview = article.group(3)
                content = article.group(3)+article.group(4)
                article_db=Article(title=title,content_preview=content_preview,\
                        content=content,content_all=md,creat_time=datetime.now())#model的datetime.now依旧毛病
                db.session.add(article_db)
                db.session.commit()
                for tag in tags:
                    if tag.isspace() or len(tag)==0: #空格串或串长度为0
                        continue
                    t = Tag.query.filter(Tag.name==tag).first()
                    a = Article.query.filter(Article.title==title).first()
                    if t:                         #如果数据库中存在该标签
                        a.tags.append(t)
                        db.session.add(a)
                        db.session.commit()
                    else:                         #数据库中没有该标签
                        tag_db = Tag(name=tag)
                        db.session.add(tag_db)
                        db.session.commit()

                        t = Tag.query.filter(Tag.name==tag).first()
                        a.tags.append(t)           #添加关系
                        db.session.add(a)
                        db.session.commit()
                return "ok"
            else:                                   #正则匹配失败,文章格式错误
                return "fail"

# 修改文章
@main.route('/articlemod/<id>/',methods=['GET','POST'])
@login_required
def article_mod(id):
    admin_user = User.query.filter(User.id==session.get('user_id')).first()
    if admin_user and admin_user.admin != True:
        return render_template('404.html'), 404
    else:
        modify = Article.query.filter(Article.id==id).first()
        if request.method == 'GET':
            return render_template('article_mod.html',article=modify)
        else:
            md = request.form.get('content')
            # 分组提取title,tag,preview,content
            article = re.search(r'title:(.*)\ntag:(.*)\n\n([\s\S]*)\n<!--.*preview.*-->\n([\s\S]*)',md)
            if article:
                title = article.group(1)
                tags = article.group(2).split(' ')
                content_preview = article.group(3)
                content = article.group(3)+article.group(4)

                article_db=Article.query.filter(Article.id==id).first()
                article_db.title=title
                article_db.content_preview=content_preview
                article_db.content=content
                article_db.content_all=md
                db.session.add(article_db)
                db.session.commit()

                article_tags = tuple(article_db.tags)
                for rtag in article_tags:          # 删除文章所有tag关系
                    article_db.tags.remove(rtag)
                    db.session.add(article_db)
                    db.session.commit()

                for tag in tags:
                    if tag.isspace() or len(tag)==0:
                        continue
                    t = Tag.query.filter(Tag.name==tag).first()
                    if t:                         #如果数据库中存在该标签
                        article_db.tags.append(t)
                        db.session.add(article_db)
                        db.session.commit()
                    else:                         #数据库中没有该标签
                        tag_db = Tag(name=tag)
                        db.session.add(tag_db)
                        db.session.commit()

                        t = Tag.query.filter(Tag.name==tag).first()
                        article_db.tags.append(t)           #添加关系
                        db.session.add(article_db)
                        db.session.commit()
                return "ok"
            else:                                   #正则匹配失败,文章格式错误
                return "fail"

    return "success"


# 添加好友链接
@main.route('/friendlink/',methods=['POST'])
@login_required
def friendlink():
    name = request.form.get('friend')
    url = request.form.get('url')
    friend = Friend(name=name,url=url)
    db.session.add(friend)
    db.session.commit()
    return redirect(url_for('main.admin'))

# 删除标签
@main.route('/tag/',methods=['POST'])
@login_required
def tag():
    name = request.form.get('addtag')
    tag = Tag.query.filter(Tag.name==name).first()
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return "ok"
    else:
        return "fail"

# 添加工具
@main.route('/tool/',methods=['POST'])
@login_required
def tool():
    name = request.form.get('tool_name')
    url = request.form.get('tool_url')
    tool = Tool(name=name,url=url)
    db.session.add(tool)
    db.session.commit()
    return redirect(url_for('main.admin'))
