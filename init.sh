#!/bin/bash

echo "-= Initializing a new virtual environment =-"
export PYENV_ROOT="`pwd`/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.4.3
pyenv virtualenv 3.4.3 web-env
pyenv activate web-env
pip install --upgrade pip
pip install -r requirements.txt
bower install