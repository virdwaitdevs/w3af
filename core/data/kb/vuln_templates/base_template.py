'''
base_template.py

Copyright 2009 Andres Riancho

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
import core.data.kb.knowledge_base as kb
import core.data.constants.severity as severity
import core.data.kb.vuln as vuln

from core.controllers.configurable import Configurable
from core.controllers.misc.number_generator import consecutive_number_generator
from core.data.options.opt_factory import opt_factory
from core.data.options.option_list import OptionList
from core.data.parsers.url import parse_qs


class BaseTemplate(Configurable):
    '''
    Vulnerability templates are a way to let the user know which parameters
    need to be completed in order to add a vulnerability to the KB.

    This is specially useful in the new way we're going to define the exploit
    workflow in which the user will be able to add a vulnerability to the KB
    for later exploitation.
    '''
    def __init__(self):
        self.name = ''
        self.url = 'http://host.tld/'
        self.data = ''
        self.method = 'GET'
        self.vulnerable_parameter = ''

    def get_options(self):
        '''
        In this case we provide a sample implementation since most vulnerabilities
        will have this template. If the specific vulnerability needs other params
        then it should override this implementation.
        '''
        ol = OptionList()

        d = 'Vulnerability name (eg. SQL Injection)'
        o = opt_factory('name', self.name, d, 'string')
        ol.add(o)

        d = 'URL (without query string parameters)'
        o = opt_factory('url', self.url, d, 'url')
        ol.add(o)

        d = 'Query string or postdata parameters in url-encoded form'
        h = 'If the HTTP method is GET, the data will be sent in the query-string'\
            ' otherwise it will be sent using the HTTP request\'s body. If the'\
            ' vulnerability requires the request to be sent using multipart-'\
            'forms, the exploit will convert this url-encoded data into that'\
            ' format.'
        o = opt_factory('data', self.data, d, 'string', help=h)
        ol.add(o)

        d = 'HTTP method'
        o = opt_factory('method', self.method, d, 'string')
        ol.add(o)

        d = 'Vulnerable parameter (needs to be one of the entered in the data'\
            ' field).'
        o = opt_factory('vulnerable_parameter', self.vulnerable_parameter, d,
                        'string')
        ol.add(o)

        return ol

    def set_options(self, options_list):
        self.name = options_list['name'].get_value()
        self.url = options_list['url'].get_value()
        self.data = parse_qs(options_list['data'].get_value())
        self.method = options_list['method'].get_value()
        self.vulnerable_parameter = options_list[
            'vulnerable_parameter'].get_value()

        if self.vulnerable_parameter not in self.data:
            msg = 'The vulnerable parameter was not found in the configured data'\
                  ' field. Please enter one of the following values: %s.'
            raise ValueError(msg % ', '.join(self.data))

    def store_in_kb(self):
        '''
        @return: None, just stores the configured vulnerability to the KB.
        '''
        kb_loc_a, kb_loc_b = self.get_kb_location()
        created_vulnerability = self.create_vuln()
        kb.kb.append(kb_loc_a, kb_loc_b, created_vulnerability)

    def get_vuln_id(self):
        return consecutive_number_generator()

    def create_base_vuln(self):
        '''
        @return: A vulnerability with some preconfigured settings
        '''
        v = vuln.vuln()
        v.set_plugin_name('Manually added vulnerability')
        v.set_id(self.get_vuln_id())
        v.set_severity(severity.HIGH)
        desc = 'This vulnerability was added to the knowledge-base by the user'\
               ' and represents a "%s" vulnerability.'
        v.set_desc(desc % self.get_vulnerability_name())
        return v

    def create_vuln(self):
        '''
        Sample implementation of the
        @return: A vulnerability object based on the data that was configured
                 by the user with calls to set_options().
        '''
        v = self.create_base_vuln()

        # User configured
        v.set_method(self.method)
        v.set_name(self.name)
        v.set_var(self.vulnerable_parameter)
        v.setURL(self.url)
        v.set_dc(self.data)

        return v

    def get_kb_location(self):
        '''
        @return: A tuple with the location where the vulnerability will be saved,
                 example return value would be: ('eval', 'eval')
        '''
        raise NotImplementedError

    def get_vulnerability_name(self):
        '''
        @return: A string containing the name of the vulnerability to be added
                 to the KB, example: 'SQL Injection'. This is just a descriptive
                 string which can contain any information, not used for any
                 strict matching of vulns before exploiting.
        '''
        raise NotImplementedError

    def get_vulnerability_desc(self):
        '''
        @return: A string containing the description of the vulnerability to be
                 added to the KB, example: 'DAV misconfiguration which allows
                 file uploads using the HTTP PUT method'
        '''
        raise NotImplementedError
