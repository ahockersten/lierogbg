#!/bin/bash

[[ "${BASH_SOURCE[0]}" == "${0}" ]] && echo "ERROR! This script must be sourced"  && exit 1

echo "-= Activating virtual environment =-"
export PYENV_ROOT="`pwd`/pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate lierogbg-env
