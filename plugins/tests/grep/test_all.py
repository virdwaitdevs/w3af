'''
test_all.py

Copyright 2011 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest
import os
import cProfile
import random

from mock import patch
from itertools import repeat

from core.controllers.w3afCore import w3afCore
from core.data.url.HTTPResponse import HTTPResponse
from core.data.dc.headers import Headers
from core.data.request.fuzzable_request import FuzzableRequest
from core.data.parsers.url import URL


class test_all(unittest.TestCase):

    PROFILING = False

    def setUp(self):
        self.url_str = 'http://moth/'
        self.url_inst = URL(self.url_str)

        self._is_404_patcher = patch

        self._w3af = w3afCore()
        self._plugins = []
        for pname in self._w3af.plugins.get_plugin_list('grep'):
            self._plugins.append(
                self._w3af.plugins.get_plugin_inst('grep', pname))

    def test_options_for_grep_plugins(self):
        '''
        We're not going to assert anything here. What just want to see if
        the plugins implement the following methods:
            - get_options()
            - set_options()
            - get_plugin_deps()
            - get_long_desc()

        And don't crash in any way when we call them.
        '''
        for plugin in self._plugins:
            o = plugin.get_options()
            plugin.set_options(o)

            plugin.get_plugin_deps()
            plugin.get_long_desc()

            plugin.end()

    # TODO: Is there a nicer way to do this? If I add a new grep plugin I won't
    #       remember about adding the patch...
    @patch('plugins.grep.motw.is_404', side_effect=repeat(False))
    @patch('plugins.grep.password_profiling.is_404', side_effect=repeat(False))
    @patch('plugins.grep.meta_tags.is_404', side_effect=repeat(False))
    @patch('plugins.grep.lang.is_404', side_effect=repeat(False))
    @patch('plugins.grep.code_disclosure.is_404', side_effect=repeat(False))
    def test_all_grep_plugins(self, *args):
        '''
        Run a set of 5 html files through all grep plugins.

        As with the previous test, the only thing we want to see is if the grep
        plugin crashes or not. We're not asserting any results.
        '''
        def profile_me():
            '''
            To be profiled
            '''
            for _ in xrange(1):
                for counter in xrange(1, 5):

                    file_name = 'test-' + str(counter) + '.html'
                    file_path = os.path.join(
                        'plugins', 'tests', 'grep', 'data', file_name)

                    body = file(file_path).read()
                    hdrs = Headers({'Content-Type': 'text/html'}.items())
                    response = HTTPResponse(200, body, hdrs,
                                            URL(self.url_str + str(counter)),
                                            URL(self.url_str + str(counter)),
                                            _id=random.randint(1, 5000))

                    request = FuzzableRequest(self.url_inst)
                    for pinst in self._plugins:
                        pinst.grep(request, response)

            for pinst in self._plugins:
                pinst.end()

        if self.PROFILING:
            #   For profiling
            cProfile.run('profile_me()', 'output.stats')
        else:
            #   The only test here is that we don't get any traceback
            profile_me()
