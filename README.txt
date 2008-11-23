repoze.what -- Authorization for WSGI applications
==================================================

:mod:`repoze.what` is an `authorization framework` for WSGI applications,
based on `repoze.who` (which deals with `authentication`).

On the one hand, it enables an authorization system based on the groups to 
which the `authenticated or anonymous` user belongs and the permissions 
granted to such groups by loading these groups and permissions into the 
request on the way in to the downstream WSGI application.

And on the other hand, it enables you to manage your groups and permissions
from the application itself or another program, under a backend-independent 
API. For example, it would be easy for you to switch from one back-end to 
another, and even use this framework to migrate the data.

It's highly extensible, so it's very unlikely that it will get in your way.
Among other things, you can extend it to check for many other conditions 
(such as checking that the user comes from a given country, based on her IP 
address, for example).
