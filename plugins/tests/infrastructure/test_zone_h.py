'''
test_zone_h.py

Copyright 2012 Andres Riancho

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

from plugins.tests.helper import PluginTest, PluginConfig


class TestZoneH(PluginTest):

    vuln_url = 'http://www.sgwater.gov.cn/'
    safe_url = 'http://www.google.com/'

    _run_configs = {
        'cfg': {
            'target': None,
            'plugins': {'infrastructure': (PluginConfig('zone_h'),)}
        }
    }

    def test_zone_h_positive(self):
        cfg = self._run_configs['cfg']
        self._scan(self.vuln_url, cfg['plugins'])

        infos = self.kb.get('zone_h', 'defacements')

        self.assertEqual(len(infos), 1, infos)

        info = infos[0]

        self.assertEqual(info.get_name(), 'Previous defacements')
        self.assertTrue(
            info.get_desc().startswith('The target site was defaced'))

    def test_zone_h_negative(self):
        cfg = self._run_configs['cfg']
        self._scan(self.safe_url, cfg['plugins'])

        infos = self.kb.get('zone_h', 'defacements')

        self.assertEqual(len(infos), 0, infos)
