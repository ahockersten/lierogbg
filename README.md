About
============
This is the LieroGBG ranking and match system. It's a Django + Bootstrap web application used for managing a Liero ranking system. It might serve as a good basis if you want to build your own, or for another game's ranking system.

A live deployment of this is currently available at http://lierogbg.maskinskrift.com.

Install instructions
====================

Installing dependencies for the virtual environment
---------------------------------------------------

* First, install pyenv if you don't have it
* $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
* Setup your shell as directed by the installer
* Install prerequisites
* (Ubuntu) $ sudo apt-get install libsqlite3-dev libreadline6-dev libbz2-dev
* (Fedora) $ sudo yum install readline-devel bzip2-devel sqlite-devel openssl-devel
* Install latest Python
* $ pyenv install 3.4.3

Setting up the virtual environment
----------------------------------

* Go to the root directory of the project
* Create virtual environment
* $ pyenv virtualenv 3.4.3 lierogbg-env
* $ pyenv activate lierogbg-env
* $ pip install -r requirements.txt
* $ bower install

Installing LESS and Bower
---------------
* (Ubuntu) $ sudo apt-get install nodejs-legacy npm
* (Fedora) $ sudo yum install npm
* $ sudo npm install -g bower less

Optional
--------
You may want to install the Django Debug Panel in Chrome to debug AJAX
requests:
* https://chrome.google.com/webstore/detail/django-debug-panel/nbiajhhibgfgkjegbnflpdccejocmbbn

Usage
=====

Using the virtual environment and running developer builds
----------------------------------------------------------
* $ pyenv activate lierogbg-env
* $ make
* $ cd lierogbg
* $ ./manage.py migrate
* $ ./manage.py runserver

Deployment instructions
===================
First, edit SECRET_KEY in lierogbg/lierogbg/settings.py and set it to something unique
for your installation.

* Go to the root directory of the project
* Install pyenv appropriately:
* $ export PYENV_ROOT="/var/www/lierogbg/pyenv"
* $ export PATH="$PYENV_ROOT/bin:$PATH"
* $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
* $ eval "$(pyenv init -)"
* $ eval "$(pyenv virtualenv-init -)"
* $ pyenv install 3.4.3
* Create virtual environment
* $ pyenv virtualenv 3.4.3 lierogbg-env
* $ pyenv activate lierogbg-env
* $ pip install -r requirements.txt

For every update, run the handy script "deploy.sh" to update everything and
reload the server.

Running the various tests
=========================

Unit tests
----------
The unit tests will do model testing, form testing and some basic view
testing for the various apps. Run with:
    $ ./manage.py test

Coverage
--------
Run coverage testing with:
    $ ./coverage.sh

PyLINT
------
PyLINT will check for syntax errors and coding standard errors. A configuration
is present in .pylintrc to make pylint and django play nicely together.
Run a full pylint test suite with:
    $ ./pylint.sh

A good total score would be around 8.0/10 or above.
