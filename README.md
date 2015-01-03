About
============
This is the LieroGBG ranking and match system. It's a Django + Bootstrap web application used for managing a Liero ranking system. It might serve as a good basis if you want to build your own, or for another game's ranking system.

A live deployment of this is currently available at http://lierogbg.maskinskrift.com.

Install instructions
====================

Installing LESS
---------------
* $ sudo apt-get install nodejs
* $ sudo npm install -g less

Installing dependencies for the virtual environment
---------------------------------------------------

* First, install pyenv and if you don't have it
* $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
* Setup your shell as directed by the installer
* Install latest Python
* $ pyenv install 3.4.2
* Install pyenv-virtualenv, if it was not installed by the above (mine was?)
* $ git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

Setting up the virtual environment
----------------------------------

* Go to the root directory of the project
* Create virtual environment
* $ pyenv virtualenv 3.4.2 lierogbg-env
* $ pyenv activate lierogbg-env
* $ pip install -r requirements.txt

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
* $ cd lierogbg
* $ ./manage.py runserver

Deployment instructions
===================
First, edit SECRET_KEY in lierogbg/lierogbg/settings.py and set it to something unique
for your installation.

* Go to the root directory of the project
* Install pyenv appropriately:
* $ export PYENV_ROOT="./pyenv"
* $ curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
* $ export PATH="$PYENV_ROOT/bin:$PATH"
* $ eval "$(pyenv init -)"
* $ pyenv install 3.4.2
* Create virtual environment
* $ pyenv virtualenv 3.4.2 lierogbg-env
* $ pyenv activate lierogbg-env
* $ pip install -r requirements.txt

For every update, run these commands:
* $ make
* $ cd lierogbg
* $ python manage.py collectstatic
* $ sudo service apache2 reload

LieroGBG is now ready to run as per normal django deployment instructions.

How to test developer builds
============
    make
    cd lierogbg
    python manage.py runserver
