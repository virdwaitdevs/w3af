'''
test_base_consumer.py

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

from core.controllers.core_helpers.consumers.base_consumer import BaseConsumer
from core.controllers.w3afCore import w3afCore
from core.data.request.fuzzable_request import FuzzableRequest
from core.data.parsers.url import URL


class TestBaseConsumer(unittest.TestCase):

    def setUp(self):
        self.bc = BaseConsumer([], w3afCore())

    def test_handle_exception(self):
        url = URL('http://moth/')
        fr = FuzzableRequest(url)
        try:
            raise Exception()
        except Exception, e:
            self.bc.handle_exception('audit', 'sqli', fr, e)

        exception_data = self.bc.out_queue.get()

        self.assertTrue(exception_data.traceback is not None)
        self.assertEqual(exception_data.phase, 'audit')
        self.assertEqual(exception_data.plugin, 'sqli')
        self.assertEqual(exception_data.exception, e)
