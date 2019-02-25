from app import db
from sqlalchemy import event


class User(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	email = 						db.Column(db.String(256))
	group = 						db.Column(db.String(128))
	project_id = 					db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
	is_admin = 						db.Column(db.Boolean)

	project = 						db.relationship('Project', backref='users')	


class Project(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	name = 							db.Column(db.String(128))


class Week(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	num = 							db.Column(db.Integer)
	descr = 						db.Column(db.Text)
	is_active = 					db.Column(db.Boolean)
	project_id = 					db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

	project = 						db.relationship('Project', backref='weeks')


class Task(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	week_id = 						db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
	num = 							db.Column(db.Integer)
	descr = 						db.Column(db.Text)

	week = 							db.relationship('Week', backref='tasks')


class Answer(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	user_id = 						db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	task_id = 						db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
	answer = 						db.Column(db.Text)

	user = 							db.relationship('User', backref='answers')
	task = 							db.relationship('Task', backref='answers')


class Alock(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	user_id = 						db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	lock_time = 					db.Column(db.Integer)


assqt_helper = db.Table('assqt_helper',
	db.Column('answer_id', db.Integer, db.ForeignKey('answer.id'), primary_key=True),
	db.Column('assqt_id', db.Integer, db.ForeignKey('assqt.id'), primary_key=True),
)


assqt_checked = db.Table('assqt_checked',
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
	db.Column('assqt_id', db.Integer, db.ForeignKey('assqt.id'), primary_key=True),
)


assqt_locked = db.Table('assqt_locked',
	db.Column('alock_id', db.Integer, db.ForeignKey('alock.id'), primary_key=True),
	db.Column('assqt_id', db.Integer, db.ForeignKey('assqt.id'), primary_key=True),
)


class Assqt(db.Model): #  queued tasks for assessment
	id = 							db.Column(db.Integer, primary_key=True)
	week_id = 						db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
	user_id = 						db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	answers = 						db.relationship('Answer', secondary=assqt_helper, lazy='subquery', backref=db.backref('assqts', lazy=True))
	checked_by = 					db.relationship('User', secondary=assqt_checked, lazy='subquery', backref=db.backref('assqts', lazy=True))
	alocks = 						db.relationship('Alock', secondary=assqt_locked, lazy='subquery', backref=db.backref('assqts', lazy=True))
	checks_left = 					db.Column(db.Integer)


class Assessment(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	answer_id = 					db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
	assessed_by_id = 				db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	score = 						db.Column(db.Integer)
	descr = 						db.Column(db.Text)

	answer = 						db.relationship('Answer', backref='assessments')
	assessed_by = 					db.relationship('User', backref='assessments', foreign_keys=[assessed_by_id])		


class Applic(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	user_id = 						db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	week_id = 						db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
	is_all_done = 					db.Column(db.Boolean)

	user = 							db.relationship('User', backref='applics')
	week = 							db.relationship('Week', backref='applics')	


class Check(db.Model):
	id = 							db.Column(db.Integer, primary_key=True)
	user_id = 						db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	week_id =						db.Column(db.Integer, db.ForeignKey('week.id'), nullable=False)
	checks_count = 					db.Column(db.Integer)
	is_all_done = 					db.Column(db.Boolean, default=False)

	user = 							db.relationship('User', backref='checks')
	week = 							db.relationship('Week', backref='checks')	



from app.sqlhooks import process_assessment, process_answer


#event.listen(Answer, 'after_insert', process_answer)
#event.listen(Answer, 'after_update', process_answer)
#event.listen(Assessment, 'after_insert', process_assessment)
#event.listen(Assessment, 'after_update', process_assessment)















