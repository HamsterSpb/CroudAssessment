**Crowdsessment** - very simple web application for crowd-based assessing assignments.
One answers questions, then assess other people's answers.

---

**Crowdsessment** - простое веб приложение для совместной оценки заданий.

Сначала пользователи сдают задания, а потом проверяют задания друг друга.

Прообразом послужил аналогичный функционал у coursera.

Прод живет тут: http://130.193.53.36/

У каждого задания есть необходимое количество проверок (после которого задание будет считаться проверенным). Такое же количество проверок - обязательно для участников. То есть если каждое задание должно быть проверено два раза, каждый участник, в свою очередь, должен проверить два задания.

Могут быть ситуации, когда задания на проверку заданчиваются. В таком случае нужно ждать поступления новых заданий или попросить прислать ссылку на уже проверенные.

Может быть и так, что задание пользователя никто не проверил. В такой ситуации можно взять ссылку и прислать ее на проверку любому другому участнику с логином и паролем.

Сейчас приложение на начальном этапе развития. Проверок прав доступа, обработки ошибок и всего такого нет. Считается, что все мы честные :) Знайте и не злоупотребляйте )

Для локального запуска понадобится python 2.7 и pip

Набираем команды в консоли:

```bash
login@login-w10:$ ./create_venv.sh
login@login-w10:$ source .venv/bin/activate
(.venv) login@login-w10:$ cp app/config_docker.py app/config.py
```

В файл app/config.py нужно добавить строчку
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
```
, а такую же строчку про постгрес - убрать (все равно постгрес по этому адресу доступен только внутри облака).

```bash
(.venv) login@login-w10:$ flask db init
(.venv) login@login-w10:$ flask db migrate
(.venv) login@login-w10:$ flask db upgrade
(.venv) login@login-w10:$ ./start_app_local.sh
```

В браузере на http://127.0.0.1:5000 появится приложение.

Чтобы приложение можно было потыкать, нужно завести пользователя. 

Для этого делаем в консоли

```python
login@login-w10:$ source .venv/bin/activate
(.venv) login@login-w10:$ flask shell
>>>from app import db
>>>from app.models import User, Project

>>>p = Project()
>>>p.name = "Test project"

>>>db.session.add(p)

>>>v = User()
>>>v.email = "test@email.com"
>>>v.is_admin = True
>>>v.group = "OXTY"
>>>v.project_id = 1

>>>db.session.add(v)

>>>db.session.commit()

>>>quit()

```

Смысл сделанного в следующем.
Project - это "разделитель учета". Нужен для того, чтобы можно было размещать параллельные задания для разных курсов, проектов итд.
Поэтому перед тем, как создавать пользователя, нам нужен проект.

Далее создаем пользователя и делаем его админом.

После этого на http://127.0.0.1:5000/admin появится админка. Заполнять ее нужно следующей минимальной информацией (чтобы заработало приложение):
- добавить неделю
- добавить задание для недели

Все, можно идти отвечать на вопросы :)

Поясню неочевидные названия таблиц:

* Alock - тут блокируем ответ, когда кто-то уже взял его на проверку. Чтобы не получилось так, что один ответ сразу схватили проверять 20 человек.
* Assqt - очередь заданий на проверку. Каждое сданное задание попадает сюда.
* Applic - сданные задания. Нужно, чтобы не дергать лишний раз базу, когда у нас будет 1000000 запросов в секунду (хехе). Как только пользователь сдает задания, сюда добавляется об этом запись.
* Check - проверенные задания. Как только кол-во заданий станет равным параметру CHECK_BY_USER в конфиге, пользователь будет считаться проверившим нужное количество заданий.