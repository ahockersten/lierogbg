#!/bin/bash
set -e

echo "-= Initializing a new virtual environment =-"
export PYENV_ROOT="`pwd`/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.4.3
pyenv virtualenv 3.4.3 lierogbg-env
pyenv activate lierogbg-env
echo "-= Installing python packages =-"
pip install --upgrade pip
pip install -r requirements.txt
echo "-= Installing NPM packages =-"
npm install
echo "-= Adding pre-push hook =-"
ln -s ../../misc/hooks/pre-push.sh .git/hooks/pre-push
