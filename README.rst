.. image:: https://secure.travis-ci.org/joeribekker/restorm.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/joeribekker/restorm

RestORM
=======

RestORM allows you to interact with resources as if they were objects (object
relational mapping), mock an entire API and incorporate custom client logic.

Description
-----------

Most RESTful API's are very easy to access with very little code. RestORM is 
just a small layer on top of ``httplib2.Http`` to get a response from an API.
However, instead of regular Python ``dict`` objects, you'll get a ``dict``-like
object that knows how to access related resources as well.

Until a version 1.0 release, backwards incompatible changes may be introduced
in future 0.x versions. Currently, RestORM works on Python 2.5+ with Python 3
support on its way.

Features
--------

* Object relational mapping of API resources (Django-like but does not depend on
  Django at all).
* Flexible client architecture that can be used with your own or third party
  clients (like oauth).
* Extensive mocking module allows you to mock API responses, or even 
  complete API's.
* Examples for Twitter and Flickr API.

Tutorial
========

.. include:: docs/tutorial.rst
   :start-after: begin-readme
   :end-before: end-readme

Install
=======

RestORM is on PyPI so you can simply use::

    $ pip install restorm

If you want the latest development version, get the code from Github::

    $ git clone git://github.com/joeribekker/restorm.git
    $ cd restorm
    $ python setup.py install

Contribute
==========

#. Get the code from Github::

    $ git clone git://github.com/joeribekker/restorm.git

#. Create and activate a virtual environment::

    $ cd restorm
    $ virtualenv .
    $ source bin/activate

#. Setup the project for development::

    $ python setup.py develop

#. Start hacking!

Testing
=======

RestORM has a whooping 90% test coverage. Although reaching 100% is not a goal
by itself, I consider unit testing to be essential during development.

Performing the unit tests yourself::

    pip install nose
    python setup.py nosetest

