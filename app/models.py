from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager
import datetime

#文章与标签多对多,利用第三张表连接
article_and_tag= db.Table('article_and_tag',
    db.Column('article_id',db.Integer,db.ForeignKey('article.id'),primary_key=True),
    db.Column('tag_id',db.Integer,db.ForeignKey('tag.id'),primary_key=True)
)
#文章表
class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200),nullable=False)
    content_preview = db.Column(db.Text,nullable=False)
    content = db.Column(db.Text,nullable=False)
    content_all = db.Column(db.Text,nullable=False)
    creat_time = db.Column(db.DateTime,default=datetime.datetime.now())

    tags = db.relationship('Tag',secondary=article_and_tag,backref=db.backref('articles'))
    # article.tags.append(tag1)
    def __repr__(self):
        return '<Article %r>' % self.title

    __mapper_args__ = {#按时间倒序排序
                'order_by': creat_time.desc()
        }
#标签表
class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text,nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.name

    __mapper_args__ = {#按id倒序排序
                'order_by': id.desc()
        }
# 用户表
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),nullable=False)
    password_hash = db.Column(db.String(128),nullable=False)
    phone_num = db.Column(db.String(11),nullable=False,unique=True)
    email = db.Column(db.String(60),nullable=True)
    avatar_url = db.Column(db.String(60),nullable=True)
    admin = db.Column(db.Boolean,default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter#sha加密
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):#验证密码
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.title
#登录控制管理
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text,nullable=False)
    creat_time = db.Column(db.DateTime, index=True, default=datetime.datetime.now())
    article_id = db.Column(db.Integer,db.ForeignKey('article.id'))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    #文章与评论，用户与评论，一对多
    article = db.relationship('Article',backref='acomments')
    user = db.relationship('User',backref='ucomments')

    __mapper_args__ = {
        'order_by': creat_time.desc()
    }

#友链表
class Friend(db.Model):
    __tablename__ = 'friend'
    name = db.Column(db.String(60),nullable=False)
    url = db.Column(db.String(100),nullable=False)
    creat_time = db.Column(db.DateTime, primary_key=True, default=datetime.datetime.now())

    __mapper_args__ = {
        'order_by': creat_time.desc()
    }
# 工具表
class Tool(db.Model):
    __tablename__ = 'tool'
    name = db.Column(db.String(60),nullable=False)
    url = db.Column(db.String(100),nullable=False)
    creat_time = db.Column(db.DateTime, primary_key=True, default=datetime.datetime.now())

    __mapper_args__ = {
        'order_by': creat_time.desc()
    }
