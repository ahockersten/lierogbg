Things you will need
============
- Django 1.4 for python
- django-recaptcha 0.0.6 for python
- LESS
- A recent version of node.js (available via ppa:chris-lea/node.js) (needed for LESS)
- nodejs and npm from above source (version in Ubuntu 12.10 won't work) (needed for LESS)

Or, more easily put:
sudo add-apt-repository ppa:chris-lea/node.js
sudo add-apt-repository ppa:chris-lea/python-django
sudo apt-get update
sudo apt-get install python-django python-pip nodejs
sudo npm install -g less

Install instructions
===================
make
cd lierogbg
python manage.py collectstatic

How to test developer builds
============
python manage.py runserver

