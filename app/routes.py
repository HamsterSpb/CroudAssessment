from app import app, db, checks_by_user
from app.models import User, Week, Task, Answer, Assessment, Applic, Check, Assqt, Alock
from flask import render_template, url_for, redirect, session, request,  flash
from sqlalchemy import and_

import time, datetime


def get_blank(params):
	return render_template('get_blank.html', **params)


def get_questions(params):
	tasks = Task.query.filter_by(week_id=params["cur_week"]).all()
	params["tasks"] = tasks
	return render_template('get_questions.html', **params)


def get_answers(params):

	raw_sql = """
	select 
		t1.* 
	from assqt as t1
	left join (
		select 
		assqt_id, 
		sum(has_checked) as hcks 
		from (
			select 
				assqt_id, 
				case 
					when user_id = :userid then 1 else 0 
				end as has_checked 
			from assqt_checked
		) as q11
		group by assqt_id
	) as q1 on q1.assqt_id = t1.id
	left join (
		select 
			assqt_id, 
			count(alock_id) as alock_cou 
		from assqt_locked
		group by assqt_id
	) as q2 on q2.assqt_id = t1.id
	left join (
		select 
		    assqt_id, 
	        answer_id as answer_id,
	        answer.user_id
		from assqt_helper
	    left join answer on answer.id = assqt_helper.answer_id
	    where answer.user_id = :userid
	) as q3 on q3.assqt_id = t1.id
	where
	(q2.alock_cou < :checks_by_user or q2.alock_cou is null)
	and (q1.assqt_id is null or q1.hcks = 0)
	and t1.week_id = :week_id
	and q3.assqt_id is null
	LIMIT 1;
	"""

	# first lets try to find an assessment already locked by the current user

	assqt = Assqt.query.filter(and_(
		Assqt.alocks.any(Alock.user_id == int(session["userid"])),
		Assqt.week_id == int(params["cur_week"])
	)).first()

	# if not, lets try to get first free assessment
	# "free" means that it didn't locked 2 times by another users and didn't already checked by the current user
	if assqt is None:
		assqt = Assqt.query.from_statement(db.text(raw_sql)).params(
			userid=int(session["userid"]), 
			week_id=int(params["cur_week"]), 
			checks_by_user=checks_by_user
		).first()
		if assqt is not None:
			assqt.alocks.append(Alock(user_id=int(session["userid"]),lock_time=time.mktime(datetime.datetime.now().timetuple())))

	if assqt is None:
		return render_template('no_answers.html', **params)

	db.session.commit()

	params["answers"] = assqt.answers
	params["answered_by"] = assqt.user_id
	params["assqt_id"] = assqt.id
	params["answers_cou"] = len(assqt.answers)

	_ch = Check.query.filter(
		and_(
			Check.week_id == params["cur_week"], 
			Check.user_id == int(session["userid"])
		)
	).first()

	if not _ch:
		asl = checks_by_user
	else:
		asl = checks_by_user - _ch.checks_count

	if asl < 0:
		asl = 0

	params["assessment_left"] = asl

	return render_template('get_answers.html', **params)


def get_results(params):

	cur_week = params["cur_week"]

	answers = Answer.query.filter(and_(
		Answer.user_id == int(session["userid"]),
		Answer.task.has(Task.week_id == cur_week)
	)).all()

	res = []

	def get_average_score(assessments):
		i = 0
		score = 0
		for assessment in assessments:
			score += int(assessment.score)
			i += 1
		if i == 0:
			return 0

		return score / i

	for answer in answers:
		if len(answer.assessments) < checks_by_user:
			continue
		cres = {}
		cres["question"] = answer.task.descr
		cres["question_num"] = answer.task.num
		cres["answer"] = answer.answer
		cres["assessments"] = answer.assessments
		cres["average_score"] = get_average_score(answer.assessments)
		res.append(cres)

	params["answers"] = res

	return render_template('get_results.html', **params)


def get_general_params():
	return {
		"login": session['login'],
		"userid": session["userid"]
	}


@app.route('/')
def index():
	if 'login' not in session:
		return redirect('/login')

	weeks = Week.query.filter(Week.project_id == User.query.get(session["userid"]).project_id).all()

	if weeks is None:
		flash("No weeks - no job")
		return redirect('/logout')

	cur_week = None
	if 'week' not in request.args:
		for week in weeks:
		 	if week.is_active:
		 		cur_week = week.id
		 		break
	else:
		week = Week.query.get(int(request.args.get("week")))
		if week.is_active:
			cur_week = week.id

	params = get_general_params()

	params["weeks"] = weeks;
	params["cur_week"] = cur_week

	if not cur_week:
		return get_blank(params)

	is_complete = Applic.query.filter(and_(
		Applic.user_id == session["userid"],
		Applic.week_id == cur_week
	)).first()

	if is_complete is None or is_complete.is_all_done == False:
		return get_questions(params)

	is_checked = Check.query.filter(and_(
		Check.user_id == session["userid"],
		Check.week_id == cur_week
	)).first()

	if is_checked is None or is_checked.is_all_done == False:
		return get_answers(params)

	return get_results(params)


@app.route('/check')
def check_by_hands():
	if 'login' not in session:
		return redirect('/')

	if 'week' not in request.args or 'answered_by' not in request.args:
		return redirect('/')

	cur_week = int(request.args.get("week"))
	answered_by = int(request.args.get("answered_by"))

	assqt = Assqt.query.filter_by(week_id=cur_week, user_id=answered_by).first()

	if assqt:
		answers = assqt.answers
	else:
		answers = Answer.query.filter(and_(
			Answer.user_id == answered_by,
			Answer.task.has(Task.week_id == cur_week)
		)).all()

	params = get_general_params()

	params["cur_week"] = cur_week

	params["answers"] = answers
	params["answered_by"] = answered_by
	params["assqt_id"] = assqt.id if assqt else "-1"
	params["answers_cou"] = len(answers)

	_ch = Check.query.filter(
		and_(
			Check.week_id == params["cur_week"], 
			Check.user_id == int(session["userid"])
		)
	).first()

	if not _ch:
		asl = checks_by_user
	else:
		asl = checks_by_user - _ch.checks_count

	if asl < 0:
		asl = 0

	params["assessment_left"] = asl

	return render_template('get_answers.html', **params)


@app.route('/send_answers', methods=['POST'])
def send_answers():
	cur_week = int(request.form.get('week_id'))
	for assqt in Assqt.query.filter(and_(
			Assqt.week_id == cur_week,
			Assqt.user_id == int(session["userid"])
		)).all():
		db.session.delete(assqt)
	_a = Assqt()
	_a.week_id = cur_week
	_a.user_id = int(session["userid"])
	_a.checks_left = checks_by_user
	db.session.add(_a)
	for key in request.form:
		if key == "week_id":
			continue
		cur_task_id = int(key) 
		cur_answer = request.form.get(key)
		_v = Answer.query.filter(
			and_(
				Answer.user_id == int(session["userid"]),
				Answer.task_id == cur_task_id
			)
		).first()
		if _v is None:
			_v = Answer(user=User.query.get(int(session["userid"])), task=Task.query.get(cur_task_id))
			db.session.add(_v)
		_v.answer = cur_answer
		_a.answers.append(_v)

	_ac = Applic.query.filter(and_(
		Applic.user_id == int(session["userid"]),
		Applic.week_id == cur_week
	)).first()
	if _ac is None:
		_ac = Applic()
		_ac.user = User.query.get(int(session["userid"]))
		_ac.week = Week.query.get(cur_week)
		db.session.add(_ac)
	_ac.is_all_done = True

	db.session.commit()
	return redirect('/')


@app.route('/send_assessment', methods=['POST'])
def send_assessment():
	user_id = int(session["userid"])
	cur_week = int(request.form.get('week_id'))
	assqt_id = int(request.form.get('assqt_id'))
	answers_cou = request.form.get('answers_cou')

	_aq = Assqt.query.get(assqt_id)
	if _aq:
		for _c in _aq.checked_by:
			if _c.id == user_id:
				flash("You've already assessed this assignment")
				return redirect('/')

	for i in range(1, int(answers_cou)+1):
		_a = Assessment()
		_a.answer = Answer.query.get(int(request.form.get('ans_id_{}'.format(i))))
		if _a.answer.user.id == user_id:
			flash("It's impossible to assess your own assignment")
			return redirect('/')
		_a.assessed_by = User.query.get(int(session["userid"]))
		_a.score = request.form.get('rg2_{}'.format(i))
		_a.descr = request.form.get('ans_desc_{}'.format(i))
		db.session.add(_a)

	if _aq:
		_aq.checked_by.append(User.query.get(user_id))
		_aq.checks_left -= 1

		for lock in _aq.alocks:
			if lock.user_id == user_id:
				db.session.delete(lock)
		if _aq.checks_left == 0:
			db.session.delete(_aq)

	_ck = Check.query.filter(and_(
		Check.user_id == user_id,
		Check.week_id == cur_week
	)).first()

	if _ck is None:
		_ck = Check()
		_ck.user = User.query.get(user_id)
		_ck.week = Week.query.get(cur_week)
		_ck.checks_count = 0
		db.session.add(_ck)

	_ck.checks_count += 1

	if _ck.checks_count == checks_by_user:
		_ck.is_all_done = True

	db.session.commit()

	return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == "POST":
		login = request.form["email"]
		groupid = request.form["groupid"]
		_v = User.query.filter(and_(
			User.email == login,
			User.group == groupid
		)).first()
		if _v is not None:
			session['login'] = login
			session['group'] = groupid
			session["userid"] = _v.id
			session["is_admin"] = "1" if _v.is_admin else "0"
			return redirect('/')
		else:
			flash("User nor found")
	return render_template("login.html")


@app.route('/logout')
def logout():
	session.pop('login')
	session.pop('group')
	return redirect('/')



