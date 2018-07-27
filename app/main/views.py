from flask import render_template,request,redirect,session,g,flash,url_for,current_app,send_from_directory
from . import main
from ..models import Article,User,Comment,Friend,Tag,Tool
from .. import db
import markdown
import base64
import sys
import os
from werkzeug import secure_filename
import json
from datetime import datetime
from .sms import requestSmsCode,verifySmsCode
import types

# 重定向到分页index 1
@main.route('/')
def first():
    return redirect(url_for('main.index',page=1))

# 分页
@main.route('/<page>')
def index(page):
    articles=Article.query.all()
    tags=Tag.query.all()
    tools=Tool.query.all()

    pages_articles=[]
    iterable=[]
    i=1

    count = Article.query.count()
    pages = count//6
    if count/6 > pages:
        pages=pages+1

    iterable_pages=pages
    while iterable_pages>0:
        iterable.append(i)
        i=i+1
        iterable_pages=iterable_pages-1

    # 预览阶段将markdown渲染成h5
    temp = int(page)
    for j,article in enumerate(articles):
        if j>=(temp-1)*6 and j<temp*6:
            article.content_preview = markdown.markdown(article.content_preview)
            pages_articles.append(article)

    context={
        'articles':pages_articles,
        'tags':tags,
        'tools':tools,
        'pages':iterable,
        'current_page':int(page),
        'last_page':pages
    }

    return render_template('index.html',**context)

# 文件上传
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in \
        current_app.config['ALLOWED_EXTENSIONS']
# 文件上传
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],filename)

# 个人简介
@main.route('/profile/',methods=['GET','POST'])
def profile():
    user = User.query.filter(User.id==g.user.id).first()

    if request.method == 'GET':
        return render_template('user_profile.html',fileurl=user.avatar_url)
    else:
        file = request.files.get('avatar')
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = g.user.username+'.'+file.filename.rsplit('.', 1)[1]
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))
            fileurl=url_for('main.uploaded_file',filename=filename)

            user.avatar_url=fileurl
            db.session.add(user)
            db.session.commit()
            return render_template('user_profile.html',fileurl=fileurl)

        else:
            return redirect(url_for('main.profile'))

# 文章
@main.route('/detail/<id>',methods=['GET'])
def article_detail(id):
    if request.method == 'GET':
        forward = int(id)-1
        next = int(id)+1
        context={
            'article':Article.query.get(id),
            'f_article':Article.query.get(forward),
            'n_article':Article.query.get(next),
            'comments':Comment.query.filter(Comment.article_id==id).all(),
            'tags':Tag.query.all(),
            'tools':Tool.query.all(),
            'content':Article.query.get(id).content
        }
        return render_template('article_detail.html',**context)

# iframe内嵌分离
@main.route('/subiframe/<id>/',methods=['GET'])
def subiframe(id):
    article=Article.query.get(id)
    return render_template('iframe.html',article=article)

# 发表评论
@main.route('/comment',methods=['POST'])
def comment():
    if hasattr(g,'user'):
        content = request.form.get('comment')
        article_id = request.form.get('article_id')
        comment = Comment(content=content,article_id=article_id,\
                    user_id=g.user.id,creat_time=datetime.now())
                    #不知道为何model中的datetime.now出点毛病，这里在从新写入一遍
        db.session.add(comment)
        db.session.commit()
        return json.dumps({'status':'ok'})
    else:
        return redirect(url_for('main.login'))

# 文章列表
@main.route('/articlelist/')
def article_list():
    context={
        'articles':Article.query.all(),
        'tags':Tag.query.all()
    }
    return render_template('article_list.html',**context)

# Tag列表
@main.route('/tag/<tag>/')
def tags(tag):
    context={
        'articles':Tag.query.filter(Tag.name==tag).first().articles,
        'tags':Tag.query.all(),
        'tag':tag,
        'tools':Tool.query.all()
    }
    return render_template('tag.html',**context)

# 好友列表
@main.route('/friendlist/')
def friend():
    context={
        'friends':Friend.query.all(),
        'tags':Tag.query.all()
    }
    return render_template('friend.html',**context)

# 关于我
@main.route('/aboutme/')
def aboutme():
    return render_template('aboutme.html')

# 用户注册
@main.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        phone_num = request.form.get('phone_num')
        email = request.form.get('email')
        sms_code = request.form.get('sms_code')
        if verifySmsCode(phone_num,sms_code) == 'ok':
            user = User.query.filter(User.phone_num == phone_num).first()
            if user:
                    return "exist"
            else:
                user = User(username=username,password=password,\
                    phone_num=phone_num,email=email)
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                session.permanent = True
                return redirect(url_for('main.first'))
        else:
            return "smsfail"

# 登录
@main.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username==username).first()
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session.permanent = True
            return redirect(url_for('main.first'))
        else:
            return redirect(url_for('main.login'))

# 注销
@main.route('/logout/')
def logout():
        session.pop('user_id')
        return redirect(url_for('main.first'))

# 发送短信
# @main.route('/sms/',methods=['POST'])
# def sms():
#     phone = request.form.get('phone')
#     send = {
#         'smsId':requestSmsCode(phone)
#     }
#     return json.dumps(send)

@main.route('/markdown/',methods=['GET'])
def editor():
    return render_template('markdown.html')

# 在每次请求之前
@main.before_request
def my_before_request():
        user_id = session.get('user_id')
        if user_id:
                user = User.query.filter(User.id==user_id).first()
                if user:
                    g.user = user

# 上下文处理器
@main.context_processor
def my_context_processor():
        if hasattr(g,'user'):
                return {'user':g.user}
        return {}
