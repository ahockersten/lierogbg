#!/bin/bash

FIXME update for webpack/react

export PYENV_ROOT="`pwd`/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate lierogbg-env
pip install -r requirements.txt
npm install
make
./manage.py collectstatic
./manage.py migrate
sudo service apache2 reload
