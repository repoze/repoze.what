# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009, Gustavo Narea <me@gustavonarea.net>.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
from repoze.what.adapters.benchmark import (GroupsRetrievalAction,
                                            PermissionsRetrievalAction)


iterations_per_action = 5

mock_items_per_section = 10
mock_sections = 5

# Making the sources:


groups = {
    u'admins': [u"gustavo", u"foo", u"bar"],
    u'venezuelans': [u"gustavo", u"foo"],
    u'developers': [u"rms", u"gustavo", u"baz"],
    u'cavemen': [],
}

permissions = {
    u'add': [u"admins", u"venezuelans", u"developers"],
    u'edit': [],
    u'view': [u"cavemen", u"admins"],
    u'scream': [u"admins"],
}


# Specifying the actions to be performed:

group_actions = (
    GroupsRetrievalAction(u"gustavo"),
)

permission_actions = (
    PermissionsRetrievalAction(u"admins"),
)