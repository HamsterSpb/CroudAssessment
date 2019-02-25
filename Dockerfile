FROM ubuntu:14.04

RUN apt-get update && apt-get install -y vim python-pip

RUN pip install --upgrade pip
RUN pip install virtualenv

RUN mkdir /opt/app
WORKDIR /opt/app

COPY ./create_venv.sh /opt/app/create_venv.sh

RUN chmod a+x ./create_venv.sh

RUN ./create_venv.sh

COPY . /opt/app
RUN mv ./app/config_docker.py ./app/config.py
RUN chmod a+x ./start_app.sh

CMD ["./start_app.sh"]
EXPOSE 5000

