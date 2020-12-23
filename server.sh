#!/usr/bin/env bash

projectPath=$(cd "$(dirname "$0")"; pwd)
pidPath=$projectPath"/pid"
pid="0"

export PATH="~/miniconda3/bin:$PATH"

cd "$projectPath"

#source activate flask_spider
source activate flask_spider
nohup python app.py >>out.log 2>&1 &