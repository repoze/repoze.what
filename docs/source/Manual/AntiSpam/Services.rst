***************************
Anti-spam service providers
***************************

:Status: Official

.. module:: repoze.what.antispam.services
    :synopsis: repoze.what anti-spam service providers
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    :mod:`repoze.what` supports anti-spam service providers (e.g., `Akismet
    <http://akismet.com/>`_) through its so-called `anti-spam services`. Here
    you will learn how to deal with such services and also you may optionally
    learn how to support more anti-spam service providers.


Supported service providers
===========================


Dealing with service providers
==============================

Setting up a service
--------------------


Checking if a comment is spam


.. autoexception:: ServiceError


How to add support for a service provider
=========================================

.. autoclass:: BaseAntiSpamService
    :members:
