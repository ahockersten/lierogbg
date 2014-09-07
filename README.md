Things you will need
============
- Django 1.6 for python
- LESS
- A recent version of node.js (available via ppa:chris-lea/node.js) (needed for LESS)
- nodejs and npm from above source (version in Ubuntu 12.10 won't work) (needed for LESS)
- django-datetime-widget

Or, more easily put:
sudo add-apt-repository ppa:chris-lea/node.js
sudo add-apt-repository ppa:chris-lea/python-django
sudo apt-get update
sudo apt-get install python-django python-pip nodejs
sudo npm install -g less
sudo pip install django-datetime-widget

Deployment instructions
===================
make
cd lierogbg
python manage.py collectstatic

How to test developer builds
============
make
cd lierogbg
python manage.py runserver

Stuff to add
==================
- sorting matches
- filtering on matches
- display RP before/after for each player in tournament (data is in database)
- display comment field for players, matches and tournaments (data is in database)
- a little "show/hide" button for match results on the "matches" view

Stuff to add that requires database changes
=====================
- rename all "game"-related variables/database fields to "match"
- rename all "subgame"-related variables/database fields to "round"
