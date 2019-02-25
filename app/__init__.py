from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import random
import string

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app, session_options={"autoflush": False})
migrate = Migrate(app, db)

checks_by_user = app.config["CHECK_BY_USER"]

app.secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(100))

from app.models import User, Week, Task, Answer, Assessment, Applic, Check, Project, Assqt, Alock

admin = Admin(app, name='app', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(Week, db.session))
admin.add_view(ModelView(Task, db.session))
admin.add_view(ModelView(Answer, db.session))
admin.add_view(ModelView(Assessment, db.session))
admin.add_view(ModelView(Check, db.session))
admin.add_view(ModelView(Assqt, db.session))
admin.add_view(ModelView(Applic, db.session))
admin.add_view(ModelView(Alock, db.session))

from app import routes