repoze.what -- Authorization for WSGI applications
==================================================

:mod:`repoze.what` is an `authorization framework` for WSGI applications,
based on `repoze.who` (which deals with `authentication`).

On one hand, it enables an authorization system based on the groups to which
the `authenticated or anonymous` user belongs and the permissions granted to
such groups by loading these groups and permissions into the request on the way
in to the downstream WSGI application. It also provides some decorators that 
check permissions for you, which have the same API as the `TurboGears 
<http://turbogears.org/>`_ 1 identity module.

And on the other hand, it enables you to manage your groups and permissions
from the application itself or another program, under a backend-independent API.
Among other things, this means that it will be easy for you to switch from one 
back-end to other, and even use this framework to migrate the data.
