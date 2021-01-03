#!/usr/bin/env bash

export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

workon flask_spider
nohup python app.py >>out.log 2>&1 &
