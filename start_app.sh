#!/bin/bash

source .venv/bin/activate

export FLASK_APP=assessment.py
export FLASK_DEBUG=0

uwsgi --http 0.0.0.0:5000 --module assessment:app

