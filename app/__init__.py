from flask import Flask, session, request
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


class AssessModelView(ModelView):
	def is_accessible(self):
		if 'is_admin' in session and session["is_admin"] == "1":
			return True
		else:
			return False

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('login', next=request.url))


admin = Admin(app, name='app', template_mode='bootstrap3')
admin.add_view(AssessModelView(User, db.session))
admin.add_view(AssessModelView(Project, db.session))
admin.add_view(AssessModelView(Week, db.session))
admin.add_view(AssessModelView(Task, db.session))
admin.add_view(AssessModelView(Answer, db.session))
admin.add_view(AssessModelView(Assessment, db.session))
admin.add_view(AssessModelView(Check, db.session))
admin.add_view(AssessModelView(Assqt, db.session))
admin.add_view(AssessModelView(Applic, db.session))
admin.add_view(AssessModelView(Alock, db.session))

from app import routes