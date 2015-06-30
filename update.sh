#!/bin/bash

echo "-= Updating things =-"
export PYENV_ROOT="`pwd`/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate lierogbg-env
pip install -r requirements.txt
bower install
