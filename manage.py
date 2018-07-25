import os
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from app import create_app, db
from app.models import Article,Comment,User,Friend,Tool

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
#flask-migrate必须同时绑定app,db

migrate = Migrate(app,db)

#把MigrateCommand命令添加到manager中
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
        manager.run()
