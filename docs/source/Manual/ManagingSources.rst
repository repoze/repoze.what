*******************************************
How to manage groups and permission sources
*******************************************

.. module:: repoze.what.adapters
    :synopsis: repoze.what source adapters
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

.. topic:: Overview

    It's possible for you to manage your groups and permissions under a
    :term:`source`-independent API and here you will learn how to do it.

:term:`Source adapters <source adapter>` enable you to
retrieve information from your :term:`groups <group source>` and 
:term:`permissions <permission source>`, as well as manage them, under an API
absolutely independent of the source type. You may take advantage
of this functionality to manage your sources from your own application or to
write an application-independent front-end to manage groups and permissions
in arbitrary WSGI applications using :mod:`repoze.what`.

This functionality will also enable you to switch from one back-end to another
with no need to update your code (except for the part where you instance the
source adapter).


Managing your sources
=====================

Sources are managed from their respective adapters. For example, to manage the
groups defined in a database, you can use::

    from repoze.what.plugins.sql import SqlGroupsAdapter
    from your_model import User, Group, DBSession
    
    groups = SqlGroupsAdapter(Group, User, DBSession)

Or to manage the permissions defined in an XML file, you could use::

    from repoze.what.plugins.xml import XMLGroupsAdapter
    
    permissions = XMLGroupsAdapter('/path/to/permissions.xml')

.. tip::

    As of v1.0.1, you can re-use the same adapters used by :mod:`repoze.what` 
    to control access. You will find them in the WSGI environment::
    
        # This is where repoze.what adapters are kept:
        adapters = environ['repoze.what.adapters']
        
        # Now let's extract the group and permission adapters:
        group_adapters = adapters['groups']
        permission_adapters = adapters['permissions']


Retrieving all the available :term:`sections <section>` from a source
---------------------------------------------------------------------

To get all the groups from the group source above, you may use the code below,
which will return a dictionary whose keys are the name of the groups and the
items are the username of the users that belong to such groups::

    >>> groups.get_all_sections()
    {u'admins': set([u'gustavo', u'adolfo']), u'developers': set([u'narea'])}

And to get all the permissions from the permission source above, you may use 
the code below, which will return a dictionary whose keys are the name of the 
permissions and the items are the name of the groups that are granted such 
permissions::

    >>> permissions.get_all_sections()
    {u'upload-images': set([u'admins', u'developers']), u'write-post': set()}

Retrieving all the :term:`items <item>` from a given :term:`section`
--------------------------------------------------------------------

To get all the users that belong to a given group in the group source above, 
you may use::

    >>> groups.get_section_items(u'admins')
    set([u'gustavo', u'adolfo'])

And to get all the groups that are granted a given permission in the permission
source above::

    >>> permissions.get_section_items(u'upload-images')
    set([u'admins', u'developers'])

Setting the :term:`items <item>` of a given :term:`section`
-----------------------------------------------------------

To set the members of a given group in the group source above, you may use::

    >>> groups.set_section_items(u'admins', [u'rms', u'guido'])

And to set the groups that are granted a given permission in the permission
source above::

    >>> permissions.set_section_items(u'write-post', [u'admins'])

.. warning::

    ``set_section_items`` will `override` the previous set of items. See, for
    example::
    
        >>> groups.get_all_sections()
        {u'admins': set([u'gustavo', u'adolfo']), u'developers': set([u'narea'])}
        >>> groups.set_section_items(u'admins', [u'rms', u'guido'])
        >>> groups.get_all_sections()
        {u'admins': set([u'rms', u'guido']), u'developers': set([u'narea'])}

Including :term:`items <item>` in a :term:`section`
---------------------------------------------------

To add one the item to a given group of the group source above, you may use::

    >>> groups.include_item(u'admins', u'rms')

Or to include many users at once::

    >>> groups.include_items(u'admins', [u'rms', u'guido'])

And to grant a given permission to one group in the permission source above::

    >>> permissions.include_item(u'write-post', u'admins')

Or to grant the same permission to many groups at once::

    >>> permissions.include_items(u'write-post', [u'admins', u'developers'])

Excluding :term:`items <item>` from a :term:`section`
-----------------------------------------------------

To remove one the items from a given group of the group source above, you may 
use::

    >>> groups.exclude_item(u'admins', u'gustavo')

Or to exclude many items at once::

    >>> groups.exclude_items(u'admins', [u'gustavo', u'adolfo'])

And to deny a given permission to one group in the permission source above::

    >>> permissions.exclude_item(u'upload-images', u'developers')

Or to grant the same permission to many groups at once::

    >>> permissions.exclude_items(u'upload-images', [u'admins', u'developers'])

Adding a :term:`section` to a :term:`source`
--------------------------------------------

To create a group in the group source above, you may use::

    >>> groups.create_section(u'designers')

And to create a permission in the permission source above::

    >>> permissions.create_section(u'edit-post')

Renaming a :term:`section`
--------------------------

To rename a group in the group source above, you may use::

    >>> groups.edit_section(u'designers', u'graphic-designers')

And to rename a permission in the permission source above::

    >>> permissions.edit_section(u'write-post', u'create-post')

Removing a :term:`section` from a :term:`source`
------------------------------------------------

To remove a group from the group source above, you may use::

    >>> groups.delete_section(u'developers')

And to remove a permission from the permission source above::

    >>> permissions.delete_section(u'write-post')

Checking whether the :term:`source` is writable
-----------------------------------------------

Some adapters may not support writting the source, or some source types may
be read-only (e.g., a source served over HTTP), or some source types may be
writable but the current source itself may be read-only (e.g., a read-only
file). For this reason, you should check whether you can write to the source 
-- You will get a :class:`SourceError` exception if you try to write to a
read-only source.

To check whether the group source above is writable, you may use::

    >>> groups.is_writable
    True

And to check whether the permission source above is writable::

    >>> permissions.is_writable
    False

Possible problems
=================

While dealing with an adapter, the following exceptions may be raised if an
error occurs:

.. autoexception:: AdapterError

.. autoexception:: SourceError

.. autoexception:: ExistingSectionError

.. autoexception:: NonExistingSectionError

.. autoexception:: ItemPresentError

.. autoexception:: ItemNotPresentError


Writing your own source adapters
================================

.. note::

    It's `very` unlikely that you'll want to write a :term:`source adapter`, so 
    if you get bored reading this section, it's absolutely safe for you to skip
    it and come back later if you `ever` need to create an adapter.

Both :term:`group <group adapter>` and :term:`permission <permission adapter>` 
:term:`adapters <source adapter>` must extend the abstract class 
:class:`BaseSourceAdapter`:

.. autoclass:: BaseSourceAdapter
    :members: __init__, _get_all_sections, _get_section_items, 
        _find_sections, _include_items, _exclude_items, _item_is_included,
        _create_section, _edit_section, _delete_section, _section_exists


Sample :term:`source adapters <source adapter>`
-----------------------------------------------

The following class illustrates how a :term:`group adapter` may look like::

    from repoze.what.adapters import BaseSourceAdapter

    class FakeGroupSourceAdapter(BaseSourceAdapter):
        """Mock group source adapter"""
    
        def __init__(self, *args, **kwargs):
            super(FakeGroupSourceAdapter, self).__init__(*args, **kwargs)
            self.fake_sections = {
                u'admins': set([u'rms']),
                u'developers': set([u'rms', u'linus']),
                u'trolls': set([u'sballmer']),
                u'python': set(),
                u'php': set()
                }
    
        def _get_all_sections(self):
            return self.fake_sections
    
        def _get_section_items(self, section):
            return self.fake_sections[section]
    
        def _find_sections(self, credentials):
            username = credentials['repoze.what.userid']
            return set([n for (n, g) in self.fake_sections.items()
                        if username in g])
    
        def _include_items(self, section, items):
            self.fake_sections[section] |= items
    
        def _exclude_items(self, section, items):
            for item in items:
                self.fake_sections[section].remove(item)
    
        def _item_is_included(self, section, item):
            return item in self.fake_sections[section]
    
        def _create_section(self, section):
            self.fake_sections[section] = set()
    
        def _edit_section(self, section, new_section):
            self.fake_sections[new_section] = self.fake_sections[section]
            del self.fake_sections[section]
    
        def _delete_section(self, section):
            del self.fake_sections[section]
    
        def _section_exists(self, section):
            return self.fake_sections.has_key(section)

And the following class illustrates how a :term:`permission adapter` may look 
like::

    from repoze.what.adapters import BaseSourceAdapter
    
    class FakePermissionSourceAdapter(BaseSourceAdapter):
        """Mock permissions source adapter"""
    
        def __init__(self, *args, **kwargs):
            super(FakePermissionSourceAdapter, self).__init__(*args, **kwargs)
            self.fake_sections = {
                u'see-site': set([u'trolls']),
                u'edit-site': set([u'admins', u'developers']),
                u'commit': set([u'developers'])
                }
    
        def _get_all_sections(self):
            return self.fake_sections
    
        def _get_section_items(self, section):
            return self.fake_sections[section]
    
        def _find_sections(self, group_name):
            return set([n for (n, p) in self.fake_sections.items()
                        if group_name in p])
    
        def _include_items(self, section, items):
            self.fake_sections[section] |= items
    
        def _exclude_items(self, section, items):
            for item in items:
                self.fake_sections[section].remove(item)
    
        def _item_is_included(self, section, item):
            return item in self.fake_sections[section]
    
        def _create_section(self, section):
            self.fake_sections[section] = set()
    
        def _edit_section(self, section, new_section):
            self.fake_sections[new_section] = self.fake_sections[section]
            del self.fake_sections[section]
    
        def _delete_section(self, section):
            del self.fake_sections[section]
    
        def _section_exists(self, section):
            return self.fake_sections.has_key(section)


Testing your source adapters with :mod:`testutil <repoze.what.adapters.testutil>`
---------------------------------------------------------------------------------

.. module:: repoze.what.adapters.testutil
    :synopsis: Automatic tests for repoze.what source adapters

:mod:`repoze.what` provides convenient utilities to automate the verification 
of your adapters. This utility is the :mod:`repoze.what.adapters.testutil` 
module, made up four test cases, which when extended must define the adapter 
(as ``self.adapter``) in the setup, as well as call this class' ``setUp()``
method:

.. autoclass:: ReadOnlyGroupsAdapterTester

.. autoclass:: ReadOnlyPermissionsAdapterTester

.. autoclass:: GroupsAdapterTester

.. autoclass:: PermissionsAdapterTester


.. attention::

    :mod:`repoze.what.adapters.testutil` is not a full replacement for a test 
    suite, so you are still highly encouraged to write the relevant/missing 
    tests to lead the code coverage of your adapters to 100%.
