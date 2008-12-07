*******************************************
How to manage groups and permission sources
*******************************************

.. module:: repoze.what.adapters
    :synopsis: repoze.what source adapters
.. moduleauthor:: Gustavo Narea <me@gustavonarea.net>

:Status: Official

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

    # Please note that the XML plugin has not been created as of this writing.
    from repoze.what.plugins.xml import XmlGroupsAdapter
    
    permissions = XmlGroupsAdapter('/path/to/permissions.xml')

.. tip::

    You can re-use the same adapters used by :mod:`repoze.what` to control
    access. You will find them in the WSGI environment::
    
        # This is where repoze.who plugins are kept:
        repozewho_plugins = environ['repoze.who.plugins']
        
        # Extracting the repoze.who metadata plugin provided by repoze.what.
        # It contains the adapters:
        repozewhat_md = repozewho_plugins['authorization_md']
        
        # Now let's extract the group and permission adapters:
        group_adapters = repozewhat_md.group_adapters
        permission_adapters = repozewhat_md.permission_adapters


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

To remove one the item from a given group of the group source above, you may 
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

.. exception:: AdapterError

    This is the base class for adapter-related problems; it's never raised
    directly.

.. exception:: SourceError

    Exception raised when the adapter found a problem in the source itself.
    
    .. attention::
        If you are creating a :term:`source adapter`, this is the only
        exception you should raise.

.. exception:: ExistingSectionError

    Exception raised when trying to add an existing group.

.. exception:: NonExistingSectionError

    Exception raised when trying to use a non-existing group.

.. exception:: ItemPresentError

    Exception raised when trying to add an item to a group that already
    contains it.

.. exception:: ItemNotPresentError

    Exception raised when trying to remove an item from a group that doesn't
    contain it.


Writing your own source adapters
================================

.. note::

    It's `very` unlikely that you'll want to write a :term:`source adapter`, so 
    if you get bored reading this section, it's absolutely safe for you to skip
    it and come back later if you `ever` need to create an adapter.

Both :term:`group <group adapter>` and :term:`permission <permission adapter>` 
:term:`adapters <source adapter>` must extend the abstract class 
:class:`BaseSourceAdapter`:

.. class:: BaseSourceAdapter([writable=True])

    :param writable: Whether the source is writable.
    :type writable: bool

    Base class for :term:`source adapters <source adapter>`.
    
    Please note that these abstract methods may only raise one exception:
    :class:`SourceError`, which is raised if there was a problem while dealing 
    with the source. They may not raise other exceptions because they should not
    validate anything but the source (not even the parameters they get).
    
    .. method:: _get_all_sections()
    
        Return all the sections found in the source.
        
        :return: All the sections found in the source.
        :rtype: dict
        :raise SourceError: If there was a problem with the source while
            retrieving the sections.
    
    .. method:: _get_section_items(section)
        
        Return the items of the section called ``section``.
        
        :param section: The name of the section to be fetched.
        :type section: unicode
        :return: The items of the section.
        :rtype: set
        :raise SourceError: If there was a problem with the source while 
            retrieving the section.
        
        .. attention::
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.

    .. method:: _find_sections(hint)
    
        Return the sections that meet a given criteria.
        
        This method depends on the type of adapter that is implementing it:
        
        * If it's a ``group`` source adapter, it returns the groups the 
          authenticated user belongs to. In this case, hint represents
          repoze.who's identity dict. Please note that hint is not an 
          user name because some adapters may need something else to find the 
          groups the authenticated user belongs to. For example, LDAP adapters 
          need the full Distinguished Name (DN) in the identity dict, or a 
          given adapter may only need the email address, so the user name alone 
          would be useless in both situations.
        * If it's a ``permission`` source adapter, it returns the name of the
          permissions granted to the group in question; here hint represents
          the name of such a group.
        
        :param hint: repoze.who's identity dictionary or a group name.
        :type hint: dict or unicode
        :return: The sections that meet the criteria.
        :rtype: tuple
        :raise SourceError: If there was a problem with the source while
            retrieving the sections.

    .. method:: _include_items(section, items)
    
        Add items to the section, in the source.
        
        :param section: The section to contain the items.
        :type section: unicode
        :param items: The new items of the section.
        :type items: tuple
        :raise SourceError: If the items could not be added to the section.

        .. attention:: 
            When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.

    .. method:: _exclude_items(section, items)
    
        Remove C{items from the section, in the source.
        
        :param section: The section that contains the items.
        :type section: unicode
        :param items: The items to be removed from section.
        :type items: tuple
        :raise SourceError: If the items could not be removed from the section.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists or the items are already included; that's 
            already done when this method is called.

    .. method:: _item_is_included(section, item)
    
        Check whether item is included in section.
        
        :param section: The name of the item to look for.
        :type section: unicode
        :param section: The name of the section that may include the item.
        :type section: unicode
        :return: Whether the item is included in section or not.
        :rtype: bool
        :raise SourceError: If there was a problem with the source.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.

    .. method:: _create_section(section)
    
        Add section to the source.
        
        :param section: The section name.
        :type section: unicode
        :raise SourceError: If the section could not be added.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section already exists; that's already done when this method is
            called.

    .. method:: _edit_section(section, new_section)
    
        Edit section's properties.
        
        :param section: The current name of the section.
        :type section: unicode
        :param new_section: The new name of the section.
        :type new_section: unicode
        :raise SourceError: If the section could not be edited.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.

    .. method:: _delete_section(section)
    
        It removes the section from the source.
        
        :param section: The name of the section to be deleted.
        :type section: unicode
        :raise SourceError: If the section could not be deleted.
        
        .. attention:: 
            When implementing this method, don't check whether the
            section really exists; that's already done when this method is
            called.

    .. method:: _section_exists(section)
    
        Check whether section is defined in the source.
        
        :param section: The name of the section to check.
        :type section: unicode
        :return: Whether the section is the defined in the source or not.
        :rtype: bool
        :raise SourceError: If there was a problem with the source.

    .. attribute:: is_writable = True

        :type: bool
        
        Whether the adapter can write to the source.
        
        If the source type handled by your adapter doesn't support write
        access, or if your adapter itself doesn't support writting to the
        source (yet), then you should set this value to ``False`` in the class
        itself; it will get overriden if the ``writable`` parameter in 
        :class:`the contructor<BaseSourceAdapter>` is set, unless you 
        explicitly disable that parameter::
        
            # ...
            class MyFakeAdapter(BaseSourceAdapter):
                def __init__():
                    super(MyFakeAdapter, self).__init__(writable=False)
            # ...
        
        .. note::
        
            If it's ``False``, then you don't have to define the methods that
            modify the source because they won't be used:
            
            * :meth:`_include_items`
            * :meth:`_exclude_items`
            * :meth:`_create_section`
            * :meth:`_edit_section`
            * :meth:`_delete_section`

    .. warning::
    
        Do not ever cache the results -- that is :class:`BaseSourceAdapter`'s
        job. It requests a given datum once, not multiple times, thanks to
        its internal cache.


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
    
        def _find_sections(self, identity):
            username = identity['repoze.who.userid']
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

:mod:`repoze.what` provides a very convenient utility to automate the
verification of your adapters. This utility is the 
:mod:`repoze.what.adapters.testutil` module, made up two test cases:

.. class:: GroupsAdapterTester
    
    Test case for groups source adapters.
    
    The groups source used for the tests `must` only contain the following
    groups (aka "sections") and their relevant users (aka "items"; if any):
    
    * admins
    
      * rms
      
    * developers
    
      * rms
      
      * linus
      
    * trolls
    
      * sballmer
      
    * python
    
    * php
    
    .. attention::
        
        Test cases that extend this, must define the adapter (as :attr:`adapter`)
        in the setup, as well as call this class' setUp() method.
    
    .. attribute:: adapter
    
        An instance of the :term:`group adapter` to be tested.
    
    For example, a test case for the mock group adapter defined above
    (``FakeGroupSourceAdapter``) may look like this::
    
        from repoze.what.adapters.testutil import GroupsAdapterTester
        
        class TestGroupsAdapterTester(GroupsAdapterTester, unittest.TestCase):
            def setUp(self):
                super(TestGroupsAdapterTester, self).setUp()
                self.adapter = FakeGroupSourceAdapter()
    
    .. note::
    
        If you are going to test a read-only adapter, then you should use
        :class:`ReadOnlyGroupsAdapterTester` instead (it can be used
        similarly).

.. class:: PermissionsAdapterTester

    Test case for permissions source adapters.
    
    The permissions source used for the tests `must` only contain the following
    permissions (aka "sections") and their relevant groups (aka "items"; if
    any):
    
    * see-site
    
      * trolls
      
    * edit-site
    
      * admins
      
      * developers
      
    * commit
    
      * developers
    
    .. attention::
        
        Test cases that extend this, must define the adapter (as :attr:`adapter`)
        in the setup, as well as call this class' setUp() method.
    
    .. attribute:: adapter
    
        An instance of the :term:`permission adapter` to be tested.
    
    For example, a test case for the mock permission adapter defined above
    (``FakePermissionSourceAdapter``) may look like this::
    
        from repoze.what.adapters.testutil import PermissionsAdapterTester
        
        class TestPermissionsAdapterTester(PermissionsAdapterTester, unittest.TestCase):
            def setUp(self):
                super(TestPermissionsAdapterTester, self).setUp()
                self.adapter = FakePermissionSourceAdapter()
    
    .. note::
    
        If you are going to test a read-only adapter, then you should use
        :class:`ReadOnlyPermissionsAdapterTester` instead (it can be used
        similarly).

.. attention::

    :mod:`repoze.what.adapters.testutil` is not a full replacement for a test 
    suite, so you are still highly encouraged to write the relevant/missing 
    tests to lead the code coverage of your adapters to 100%.
