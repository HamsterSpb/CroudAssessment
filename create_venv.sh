#!/bin/bash

virtualenv .venv

. .venv/bin/activate

pip install Flask
pip install Flask-SQLAlchemy
pip install Flask-Migrate
pip install Flask-Admin
pip install psycopg2

pip install enum34
pip install uwsgi







