from flask import render_template,request,redirect,session,g,flash,url_for,current_app,send_from_directory
from . import main
from ..models import Article,User,Comment,Friend,Tag
from .. import db
import markdown
import base64
import sys
import os
from werkzeug import secure_filename
# from markdown.extensions.wikilinks import WikiLinkExtension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in \
        current_app.config['ALLOWED_EXTENSIONS']

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],filename)

# profile
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

@main.route('/')
def first():
    return redirect(url_for('main.index',page=1))

@main.route('/<page>')
def index(page):
    articles=Article.query.all()
    tags=Tag.query.all()

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


    # markdwon to html　and divide page j start with 0
    temp = int(page)
    for j,article in enumerate(articles):
        if j>=(temp-1)*6 and j<temp*6:
            article.content = markdown.markdown(article.content)
            pages_articles.append(article)

    context={
        'articles':pages_articles,
        'tags':tags,
        'pages':iterable,
        'current_page':int(page),
        'last_page':pages
    }

    return render_template('index.html',**context)

# article_detail
@main.route('/detail/<id>',methods=['GET','POST'])
def article_detail(id):
    if request.method == 'GET':
        forward = int(id)-1
        next = int(id)+1
        context={
            'article':Article.query.get(id),
            'f_article':Article.query.get(forward),
            'n_article':Article.query.get(next),
            'comments':Comment.query.filter(Comment.article_id==id).all(),
            'tags':Tag.query.all()
        }
        context['article'].content = markdown.markdown(context['article'].content)
        return render_template('article_detail.html',**context)
    else:
        if hasattr(g,'user'):
            comtent = request.form.get('comment')
            comment = Comment(content=comtent,article_id=id,user_id=g.user.id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('main.article_detail',id=id))
        else:
            return redirect(url_for('main.login'))

# all_article
@main.route('/articlelist/')
def all_article():
    context={
        'articles':Article.query.all(),
        'tags':Tag.query.all()
    }
    return render_template('all_article.html',**context)

# friends list
@main.route('/friendlist/')
def friend():
    context={
        'friends':Friend.query.all(),
        'tags':Tag.query.all()
    }
    return render_template('friend.html',**context)
# about me
@main.route('/aboutme/')
def aboutme():
    return render_template('aboutme.html')

# regist
@main.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # image = base64.b64encode(avatar)
        user = User.query.filter(User.username == username).first()
        if user:
                return redirect(url_for('main.regist'))
        else:
            if password1==password2:
                user = User(username=username,password=password1)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('main.login'))
            else:
                return redirect(url_for('main.regist'))

# login
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

# logout
@main.route('/logout/')
def logout():
        session.pop('user_id')
        return redirect(url_for('main.first'))



# markdown edit
@main.route('/markdown/',methods=['POST'])
def markdownedit():
    md=request.form.get('suggest')
    # html = markdown.markdown(md, output_format='html5', \
    # extensions=['markdown.extensions.toc',\
    # WikiLinkExtension(base_url='https://en.wikipedia.org/wiki/',\
    #     end_url='#Hyperlinks_in_wikis'),\
    # 'markdown.extensions.sane_lists',\
    # 'markdown.extensions.codehilite',\
    # 'markdown.extensions.abbr',\
    # 'markdown.extensions.attr_list',\
    # 'markdown.extensions.def_list',\
    # 'markdown.extensions.fenced_code',\
    # 'markdown.extensions.footnotes',\
    # 'markdown.extensions.smart_strong',\
    # 'markdown.extensions.meta',\
    # 'markdown.extensions.nl2br',\
    # 'markdown.extensions.tables'])
    html = markdown.markdown(md)
    return html

# before_request
@main.before_request
def my_before_request():
        user_id = session.get('user_id')
        if user_id:
                user = User.query.filter(User.id==user_id).first()
                if user:
                    g.user = user

# context_processor
@main.context_processor
def my_context_processor():
        if hasattr(g,'user'):
                return {'user':g.user}
        return {}
