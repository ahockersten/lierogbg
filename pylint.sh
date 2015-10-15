#!/bin/sh

TARGETS="about accounts lierogbg maps rankings rules"

pylint --rcfile=.pylintrc $TARGETS
