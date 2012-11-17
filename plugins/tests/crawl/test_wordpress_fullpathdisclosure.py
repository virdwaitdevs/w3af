# coding: utf8
'''
test_wordpress_fullpathdisclosure.py

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


class TestWordpressPathDisclosure(PluginTest):

    wordpress_url = 'http://wordpress/'

    _run_configs = {
        'direct': {
            'target': wordpress_url,
            'plugins': {
        'crawl': (PluginConfig('wordpress_fullpathdisclosure',),)
            },
        },
    }

    def test_enumerate_users(self):
        cfg = self._run_configs['direct']
        self._scan(cfg['target'], cfg['plugins'])

        infos = self.kb.get('wordpress_fullpathdisclosure', 'info')

        self.assertEqual(len(infos), 1, infos)
        info = infos[0]

        self.assertEqual(info.get_name(), 'WordPress path disclosure')
        self.assertEqual(info.getURL().url_string,
                         self.wordpress_url + 'wp-content/plugins/akismet/akismet.php')
