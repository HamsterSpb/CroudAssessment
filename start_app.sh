#!/bin/bash

source .venv/bin/activate

export FLASK_APP=assessment.py
export FLASK_DEBUG=0

uwsgi --http 127.0.0.1:5000 --module assessment:app

