Welcome to RestORM
==================

.. image:: https://secure.travis-ci.org/joeribekker/restorm.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/joeribekker/restorm

RestORM allows you to interact with :doc:`resources <resources>` as if they were
objects (object relational mapping), :doc:`mock <mocking>` an entire API and 
incorporate custom :doc:`client <clients>` logic.

Description
-----------

RestORM structures the way you access a RESTful API and allows you to access
related resources. On top of that, you can easily mock an entire API and replace
the real client with a mock version in unit tests. RestORM is very extensible
but offers many functionalities out of the box to get up and running quickly.

Currently, RestORM works on Python 2.5+ with Python 3 support on its way.

Features
--------

* Object relational mapping of API resources (Django-like but does not depend on
  Django at all).
* Flexible client architecture that can be used with your own or third party
  clients (like oauth).
* Extensive mocking module allows you to mock API responses, or even 
  complete API's.
* Examples for Twitter and Flickr API.

Documentation
=============

.. toctree::
   :maxdepth: 2

   tutorial
   clients
   resources
   mocking

Installation
============

RestORM is on PyPI, so you can simply use::

    $ pip install restorm

If you want the latest development version, get the code from Github::

    $ pip install -e git+git://github.com/joeribekker/restorm.git#egg=restorm

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
    python setup.py nosetests

.. note::

    Until a version 1.0 release, backwards incompatible changes may be 
    introduced in future 0.x versions.
