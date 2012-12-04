.. image:: https://secure.travis-ci.org/joeribekker/restorm.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/joeribekker/restorm

Welcome to RestORM
==================

RestORM allows you to interact with :doc:`resources <resources>` as if they were
objects (object relational mapping), :doc:`mock <mocking>` an entire API and 
incorporate custom :doc:`client <clients>` logic.

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

Documentation
=============

.. toctree::
   :maxdepth: 2

   tutorial
   clients
   resources
   mocking
