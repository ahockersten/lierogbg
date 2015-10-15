#!/bin/bash

PACKAGES="about,accounts,lierogbg,maps,rankings,rules"

coverage run --source=$PACKAGES manage.py test
coverage report --show-missing
coverage html
