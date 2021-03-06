##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest, re, unittest
from zope.testing import renormalizing
import zc.buildout.testing

try:
    not_found = zc.buildout.testing.not_found
except AttributeError:
    not_found = (re.compile(r"Not found: [^\n]+/(\w|\.)+/\r?\n"), "")

# Buildout 1 says 'part', buildout 2 says 'section'.
initializing_part = (re.compile(r"Initializing (part|section) "),
                     "Initializing part ")

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.rhrc', test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
               zc.buildout.testing.normalize_path,
               zc.buildout.testing.normalize_script,
               zc.buildout.testing.normalize_egg_py,
               not_found,
               initializing_part,
               ])
            ),
        ))
