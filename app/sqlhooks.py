from app.models import User, Week, Task, Answer, Assessment, Applic, Check
from app import db
from sqlalchemy import and_


def process_tmpl(mapper, connection, target, has_count, need_count, where_to_save, user_id, week_id):

	if need_count > has_count:
		return

	wtss = where_to_save.query.filter_by(user_id=user_id, week_id=week_id).all()

	print wtss

	if wtss is not None:
		for wts in wtss:
			print wts
			db.session.delete(wts)

	wts = where_to_save()
	wts.user_id = user_id
	wts.week_id = week_id
	wts.is_all_done = True

	db.session.add(wts)


def process_answer(mapper, connection, target):
	user_id = target.user_id
	week_id = target.task.week_id

	answers_of_week_count = Task.query.filter(and_(
			Task.week_id == week_id,
			Task.week.has(project_id=target.user.project_id)
		)
	).count()
	answers_by_current_user = Answer.query.filter(
		and_(
			Answer.task.has(week_id=week_id), 
			Answer.user_id == user_id
		)
	).count()
	
	process_tmpl(mapper, connection, target, answers_by_current_user, answers_of_week_count, Applic, user_id, week_id)


def process_assessment(mapper, connection, target):
	user_id = target.assessed_by.id
	week_id = target.answer.task.week_id

	ass_of_week_count = 2
	ass_by_current_user = Assessment.query.filter(
		and_(
			Assessment.answer.has(Answer.task.has(week_id=week_id)), 
			Assessment.assessed_by_id == user_id
		)
	).count()
	
	process_tmpl(mapper, connection, target, ass_by_current_user, ass_of_week_count, Check, user_id, week_id)













	