About
============
This is the LieroGBG ranking and match system. It's a Django + Bootstrap web application used for managing a Liero ranking system. It might serve as a good basis if you want to build your own, or for another game's ranking system.

A live deployment of this is currently available at http://lierogbg.orbmit.org

Install instructions
====================

Installing npm and less
---------------
* (Ubuntu) $ sudo apt-get install nodejs-legacy npm
* (Fedora) $ sudo yum install npm

Installing dependencies for the virtual environment
---------------------------------------------------

* Install prerequisites
* (Ubuntu) $ sudo apt-get install libsqlite3-dev libreadline6-dev libbz2-dev
* (Fedora) $ sudo yum install readline-devel bzip2-devel sqlite-devel openssl-devel

Optional
--------
You may want to install the Django Debug Panel in Chrome to debug AJAX
requests:
* https://chrome.google.com/webstore/detail/django-debug-panel/nbiajhhibgfgkjegbnflpdccejocmbbn

Usage
=====

Setting up the dev environment
------------------
* Run ./init_dev.sh

Using the virtual environment and running developer builds
----------------------------------------------------------
* $ source activate.sh
* $ ./update.sh
* $ ./manage.py runserver

Deployment instructions
===================
First, edit SECRET_KEY in lierogbg/lierogbg/settings.py and set it to something unique
for your installation.
* Run ./init_production.sh

For every update, run the script "deploy.sh" to update everything and
reload the server.

Running the various tests
=========================

Unit tests
----------
$ ./manage.py test

Coverage
--------
Run coverage testing with:
$ ./coverage.sh

PyLINT
------
Run a full pylint test suite with:
$ ./pylint.sh

A good total score would be around 8.0/10 or above.
